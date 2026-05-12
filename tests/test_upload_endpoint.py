from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_upload_file_saves_supported_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "input_dir", tmp_path)
    client = TestClient(app)

    response = client.post(
        "/upload-file",
        files={
            "file": (
                "sample.xlsx",
                b"not a real workbook, endpoint only saves uploads",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
    assert (tmp_path / "sample.xlsx").exists()


def test_upload_file_rejects_unsupported_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "input_dir", tmp_path)
    client = TestClient(app)

    response = client.post(
        "/upload-file",
        files={"file": ("notes.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
