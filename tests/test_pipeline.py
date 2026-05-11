import json

import pytest

openpyxl = pytest.importorskip("openpyxl")

from app.config import settings
from app.pipeline import run_analysis


def test_pipeline_smoke_creates_output_json_files(tmp_path, monkeypatch) -> None:
    input_dir = tmp_path / "sample_data"
    output_dir = tmp_path / "outputs"
    input_dir.mkdir()

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Summary"
    worksheet["A1"] = "2024 Annual UK Housing Starts 134,470 preliminary"
    worksheet["A2"] = "2024 Annual UK Housing Starts 132,460 revised"
    workbook.save(input_dir / "housing_sample.xlsx")

    monkeypatch.setattr(settings, "mock_llm", True)
    monkeypatch.setattr(settings, "cache_dir", tmp_path / ".cache" / "llm_extractions")

    summary = run_analysis(input_dir, output_dir)

    metrics_path = output_dir / "extracted_metrics.json"
    discrepancies_path = output_dir / "discrepancies.json"
    token_usage_path = output_dir / "token_usage_report.json"
    report_path = output_dir / "reconciliation_report.html"

    assert metrics_path.exists()
    assert discrepancies_path.exists()
    assert token_usage_path.exists()
    assert report_path.exists()
    assert summary["files_processed"] == 1
    assert summary["metrics_extracted"] == 2
    assert summary["discrepancies_found"] == 1

    discrepancies = json.loads(discrepancies_path.read_text(encoding="utf-8"))
    assert discrepancies[0]["likely_reason"] == "preliminary_vs_revised"
