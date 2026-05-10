from app.extraction.schema import MetricRecord
from app.reconciliation.discrepancy_detector import detect_discrepancies


def _record(
    value: int,
    *,
    year: int = 2024,
    source_file: str | None = None,
    caveat: str | None = None,
    source_type: str = "xlsx",
    metric_name: str = "Housing starts",
) -> MetricRecord:
    return MetricRecord(
        metric_name=metric_name,
        canonical_metric_name="housing_starts",
        value=value,
        unit="dwellings",
        year=year,
        period="annual",
        geography="UK",
        source_file=source_file or f"source-{value}.xlsx",
        source_type=source_type,
        source_location="Sheet1!A1",
        extraction_method="rule_based",
        confidence=0.95,
        caveat=caveat,
        raw_text=str(value),
    )


def test_same_value_no_discrepancy() -> None:
    discrepancies = detect_discrepancies([_record(134470), _record(134470)])

    assert discrepancies == []


def test_2024_medium_discrepancy() -> None:
    discrepancies = detect_discrepancies([_record(134470), _record(132460)])

    assert len(discrepancies) == 1
    assert discrepancies[0].severity == "medium"
    assert discrepancies[0].canonical_metric_name == "housing_starts"
    assert "different values" in discrepancies[0].explanation


def test_2025_high_discrepancy() -> None:
    discrepancies = detect_discrepancies(
        [
            _record(145320, year=2025),
            _record(180250, year=2025),
        ]
    )

    assert len(discrepancies) == 1
    assert discrepancies[0].severity == "high"
    assert discrepancies[0].likely_reason == "unknown"
    assert discrepancies[0].recommended_action == (
        "Do not quote this figure externally until validated against an official source."
    )


def test_same_source_conflict_becomes_internal_document_conflict() -> None:
    discrepancies = detect_discrepancies(
        [
            _record(134470, source_file="annual_report.xlsx"),
            _record(132460, source_file="annual_report.xlsx"),
        ]
    )

    assert len(discrepancies) == 1
    assert discrepancies[0].likely_reason == "internal_document_conflict"


def test_preliminary_vs_revised_reason() -> None:
    discrepancies = detect_discrepancies(
        [
            _record(134470, caveat="preliminary", source_file="stakeholder_deck.pptx", source_type="pptx"),
            _record(132460, caveat="revised", source_file="annual_report.xlsx"),
        ]
    )

    assert len(discrepancies) == 1
    assert discrepancies[0].likely_reason == "preliminary_vs_revised"
    assert discrepancies[0].recommended_action == (
        "Use the revised annual report figure for external reporting, "
        "but retain the preliminary estimate as historical context."
    )
