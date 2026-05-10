from app.extraction.rule_extractor import extract_metrics_rule_based
from app.extraction.schema import SourceChunk


def _chunk(text: str) -> SourceChunk:
    return SourceChunk(
        chunk_id="chunk-1",
        source_file="briefing.docx",
        source_type="docx",
        source_location="paragraph 1",
        content_type="text",
        text=text,
        metadata={},
    )


def test_extracts_annual_housing_starts() -> None:
    metrics = extract_metrics_rule_based(
        [_chunk("Annual Housing Starts 132,460 -25.7%")]
    )

    assert len(metrics) == 1
    assert metrics[0].metric_name == "Housing Starts"
    assert metrics[0].canonical_metric_name == "housing_starts"
    assert metrics[0].value == 132460
    assert metrics[0].unit == "dwellings"
    assert metrics[0].period == "annual"
    assert metrics[0].extraction_method == "rule_based"


def test_extracts_completions() -> None:
    metrics = extract_metrics_rule_based(
        [_chunk("England Housing Completions 174,180 -11.3%")]
    )

    assert len(metrics) == 1
    assert metrics[0].canonical_metric_name == "housing_completions"
    assert metrics[0].value == 174180
    assert metrics[0].geography == "England"


def test_extracts_affordable_percentage() -> None:
    metrics = extract_metrics_rule_based(
        [_chunk("Affordable housing share 28%")]
    )

    assert len(metrics) == 1
    assert metrics[0].canonical_metric_name == "affordable_housing_percentage"
    assert metrics[0].value == 28
    assert metrics[0].unit == "percent"


def test_extracts_price_and_quarterly_examples() -> None:
    chunks = [
        _chunk("Avg new-build price \u00a3285k"),
        _chunk("Q1 2024 starts 30,800"),
        _chunk("Q2 2025 completions 45,200"),
    ]

    metrics = extract_metrics_rule_based(chunks)

    assert [metric.canonical_metric_name for metric in metrics] == [
        "average_new_build_price",
        "housing_starts",
        "housing_completions",
    ]
    assert metrics[0].value == 285000
    assert metrics[0].unit == "gbp"
    assert metrics[1].period == "Q1"
    assert metrics[1].year == 2024
    assert metrics[2].period == "Q2"
    assert metrics[2].year == 2025


def test_captures_preliminary_caveat() -> None:
    metrics = extract_metrics_rule_based(
        [_chunk("Preliminary UK starts 134,470")]
    )

    assert len(metrics) == 1
    assert metrics[0].geography == "UK"
    assert metrics[0].caveat == "preliminary"


def test_does_not_extract_unrelated_numbers() -> None:
    metrics = extract_metrics_rule_based(
        [_chunk("The meeting had 12 attendees and lasted 45 minutes.")]
    )

    assert metrics == []
