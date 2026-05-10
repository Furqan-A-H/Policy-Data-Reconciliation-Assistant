from fastapi import FastAPI

from app.config import settings

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
