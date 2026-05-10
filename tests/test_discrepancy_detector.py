from app.extraction.schema import MetricRecord
from app.reconciliation.discrepancy_detector import detect_discrepancies


def _record(value: int) -> MetricRecord:
    return MetricRecord(
        metric_name="Affordable housing completions",
        canonical_metric_name="affordable_housing_completions",
        value=value,
        unit="homes",
        year=2024,
        period="annual",
        geography="Greater London",
        source_file=f"source-{value}.xlsx",
        source_type="xlsx",
        source_location="Sheet1!A1",
        extraction_method="rule_based",
        confidence=0.95,
        caveat=None,
        raw_text=str(value),
    )


def test_detect_discrepancies_flags_different_values() -> None:
    discrepancies = detect_discrepancies([_record(100), _record(120)])

    assert len(discrepancies) == 1
    assert discrepancies[0].severity == "medium"
    assert len(discrepancies[0].records) == 2


def test_detect_discrepancies_ignores_matching_values() -> None:
    discrepancies = detect_discrepancies([_record(100), _record(100)])

    assert discrepancies == []
