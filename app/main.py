import json
import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.config import settings
from app.pipeline import run_analysis

SUPPORTED_UPLOAD_EXTENSIONS = {".docx", ".xlsx", ".xlsm", ".pptx"}

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Foundation API for policy data reconciliation workflows.",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "foundation-ready",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-file")
def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload .docx, .xlsx, .xlsm, or .pptx files.",
        )

    settings.input_dir.mkdir(parents=True, exist_ok=True)
    destination = settings.input_dir / filename

    with destination.open("wb") as output_file:
        shutil.copyfileobj(file.file, output_file)

    return {
        "status": "uploaded",
        "filename": filename,
        "saved_to": str(destination.resolve()),
        "next_step": "Run POST /run-analysis to process uploaded files.",
    }


@app.post("/run-analysis")
def run_default_analysis() -> dict[str, Any]:
    return run_analysis(settings.input_dir, settings.output_dir)


@app.get("/outputs/discrepancies")
def get_discrepancies() -> Any:
    return _read_output_json(settings.output_dir / "discrepancies.json")


@app.get("/outputs/metrics")
def get_metrics() -> Any:
    return _read_output_json(settings.output_dir / "extracted_metrics.json")


@app.get("/outputs/report", response_class=HTMLResponse)
def get_report() -> str:
    path = settings.output_dir / "reconciliation_report.html"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{path} does not exist yet. Run POST /run-analysis first.",
        )

    return path.read_text(encoding="utf-8")


def _read_output_json(path: Path) -> Any:
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{path} does not exist yet. Run POST /run-analysis first.",
        )

    return json.loads(path.read_text(encoding="utf-8"))
