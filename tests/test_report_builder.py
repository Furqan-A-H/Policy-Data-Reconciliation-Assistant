from app.extraction.schema import DiscrepancyRecord, MetricRecord, TokenUsageReport
from app.reporting.report_builder import build_html_report


def _metric(value: int, source_file: str, source_location: str) -> MetricRecord:
    return MetricRecord(
        metric_name="Housing starts",
        canonical_metric_name="housing_starts",
        value=value,
        unit="dwellings",
        year=2025,
        period="annual",
        geography="UK",
        source_file=source_file,
        source_type="xlsx",
        source_location=source_location,
        extraction_method="rule_based",
        confidence=0.9,
        caveat=None,
        raw_text=str(value),
    )


def test_report_includes_discrepancy_source_locations() -> None:
    first = _metric(145320, "report.xlsx", "sheet Summary row 2")
    second = _metric(180250, "report.xlsx", "sheet Summary row 8")
    discrepancy = DiscrepancyRecord(
        canonical_metric_name="housing_starts",
        year=2025,
        period="annual",
        geography="UK",
        unit="dwellings",
        severity="high",
        likely_reason="internal_document_conflict",
        records=[first, second],
        explanation="Conflicting values were found.",
        recommended_action="Resolve the source conflict.",
    )
    token_usage = TokenUsageReport(
        files_processed=1,
        chunks_created=2,
        chunks_sent_to_llm=0,
        chunks_skipped=2,
        estimated_input_tokens=0,
        estimated_output_tokens=0,
        estimated_token_saving_percent=100.0,
    )

    html = build_html_report(
        metrics=[first, second],
        discrepancies=[discrepancy],
        token_usage_report=token_usage,
        mock_llm=True,
    )

    assert "report.xlsx (sheet Summary row 2)" in html
    assert "report.xlsx (sheet Summary row 8)" in html
    assert "severity-high" in html
