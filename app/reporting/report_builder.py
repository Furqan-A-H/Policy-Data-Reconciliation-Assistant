from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.extraction.schema import DiscrepancyRecord, MetricRecord, TokenUsageReport


def build_html_report(
    *,
    metrics: list[MetricRecord],
    discrepancies: list[DiscrepancyRecord],
    token_usage_report: TokenUsageReport,
    mock_llm: bool,
) -> str:
    template_dir = Path(__file__).parent / "templates"
    environment = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )
    template = environment.get_template("report.html")
    sorted_discrepancies = sorted(
        discrepancies,
        key=lambda item: {"high": 0, "medium": 1, "low": 2}.get(item.severity, 3),
    )
    return template.render(
        executive_summary=_build_executive_summary(metrics, sorted_discrepancies, mock_llm),
        key_findings=_build_key_findings(metrics, sorted_discrepancies, token_usage_report),
        metric_rows=[_metric_row(metric) for metric in metrics],
        discrepancy_rows=[_discrepancy_row(discrepancy) for discrepancy in sorted_discrepancies],
        caveats=_source_caveats(metrics),
        token_usage=token_usage_report,
        mock_llm=mock_llm,
    )


def _build_executive_summary(
    metrics: list[MetricRecord],
    discrepancies: list[DiscrepancyRecord],
    mock_llm: bool,
) -> str:
    mode_note = (
        "The summary was generated deterministically because mock LLM mode is enabled."
        if mock_llm
        else "The summary is based only on extracted metrics and detected discrepancies."
    )

    if not metrics:
        return (
            "No housing metrics were extracted from the available source files. "
            "Add relevant Word, Excel, or PowerPoint files to sample_data and rerun the analysis. "
            f"{mode_note}"
        )

    if not discrepancies:
        return (
            f"The analysis extracted {len(metrics)} housing metric records and found no "
            f"overlapping numeric conflicts. {mode_note}"
        )

    high_count = sum(1 for item in discrepancies if item.severity == "high")
    medium_count = sum(1 for item in discrepancies if item.severity == "medium")
    low_count = sum(1 for item in discrepancies if item.severity == "low")
    return (
        f"The analysis extracted {len(metrics)} housing metric records and found "
        f"{len(discrepancies)} discrepancy or discrepancies requiring review. "
        f"Severity breakdown: {high_count} high, {medium_count} medium, {low_count} low. "
        f"{mode_note}"
    )


def _build_key_findings(
    metrics: list[MetricRecord],
    discrepancies: list[DiscrepancyRecord],
    token_usage_report: TokenUsageReport,
) -> list[str]:
    findings = [
        f"{len(metrics)} metric records were extracted from the source material.",
        f"{len(discrepancies)} discrepancy or discrepancies were detected.",
        (
            f"{token_usage_report.chunks_skipped} chunks were not sent to the LLM, "
            f"an estimated saving of {token_usage_report.estimated_token_saving_percent}%."
        ),
    ]

    high_severity = [item for item in discrepancies if item.severity == "high"]
    if high_severity:
        findings.append(
            f"{len(high_severity)} high severity conflict or conflicts should not be quoted externally until validated."
        )

    reason_counts = _reason_counts(discrepancies)
    for reason, count in reason_counts.items():
        findings.append(f"{count} discrepancy or discrepancies were classified as {reason}.")

    return findings


def _metric_row(metric: MetricRecord) -> dict[str, Any]:
    return {
        "metric": _humanise_metric(metric.canonical_metric_name),
        "value": _format_value(metric.value),
        "unit": metric.unit,
        "year": metric.year or "",
        "source_file": metric.source_file,
        "source_location": metric.source_location,
        "extraction_method": metric.extraction_method,
        "caveat": metric.caveat or "",
    }


def _discrepancy_row(discrepancy: DiscrepancyRecord) -> dict[str, Any]:
    first_record = discrepancy.records[0] if discrepancy.records else None
    second_record = discrepancy.records[1] if len(discrepancy.records) > 1 else None

    return {
        "metric": _humanise_metric(discrepancy.canonical_metric_name),
        "year": discrepancy.year or "",
        "period": discrepancy.period or "",
        "geography": discrepancy.geography or "",
        "source_a": _format_source_reference(first_record),
        "value_a": _format_value(first_record.value) if first_record else "",
        "source_b": _format_source_reference(second_record),
        "value_b": _format_value(second_record.value) if second_record else "",
        "severity": discrepancy.severity,
        "likely_reason": discrepancy.likely_reason,
        "recommended_action": discrepancy.recommended_action,
    }


def _source_caveats(metrics: list[MetricRecord]) -> list[dict[str, str]]:
    caveats: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for metric in metrics:
        if not metric.caveat:
            continue

        key = (metric.source_file, metric.source_location, metric.caveat)
        if key in seen:
            continue

        seen.add(key)
        caveats.append(
            {
                "source_file": metric.source_file,
                "source_location": metric.source_location,
                "caveat": metric.caveat,
            }
        )

    return caveats


def _humanise_metric(value: str) -> str:
    return value.replace("_", " ").title()


def _format_value(value: float | int | str) -> str:
    if isinstance(value, int):
        return f"{value:,}"

    if isinstance(value, float):
        return f"{value:,.0f}" if value.is_integer() else f"{value:,.2f}"

    return str(value)


def _format_source_reference(record: MetricRecord | None) -> str:
    if record is None:
        return ""
    return f"{record.source_file} ({record.source_location})"


def _reason_counts(discrepancies: list[DiscrepancyRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for discrepancy in discrepancies:
        counts[discrepancy.likely_reason] = counts.get(discrepancy.likely_reason, 0) + 1
    return counts
