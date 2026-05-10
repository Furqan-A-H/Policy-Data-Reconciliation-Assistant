import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.config import settings
from app.pipeline import run_analysis

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


@app.post("/run-analysis")
def run_default_analysis() -> dict[str, Any]:
    return run_analysis(Path("sample_data"), Path("outputs"))


@app.get("/outputs/discrepancies")
def get_discrepancies() -> Any:
    return _read_output_json(Path("outputs") / "discrepancies.json")


@app.get("/outputs/metrics")
def get_metrics() -> Any:
    return _read_output_json(Path("outputs") / "extracted_metrics.json")


@app.get("/outputs/report", response_class=HTMLResponse)
def get_report() -> str:
    path = Path("outputs") / "reconciliation_report.html"
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
