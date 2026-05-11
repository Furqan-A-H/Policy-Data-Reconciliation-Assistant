from collections import defaultdict
from decimal import Decimal, InvalidOperation

from app.extraction.schema import DiscrepancyRecord, MetricRecord
from app.reconciliation.source_reliability import score_source_reliability


def detect_discrepancies(records: list[MetricRecord]) -> list[DiscrepancyRecord]:
    """Compare overlapping metric values using deterministic rules."""
    grouped: dict[tuple, list[MetricRecord]] = defaultdict(list)

    for record in records:
        key = (
            record.canonical_metric_name,
            record.year,
            record.period,
            record.geography,
            record.unit,
        )
        grouped[key].append(record)

    discrepancies: list[DiscrepancyRecord] = []
    for key, group in grouped.items():
        if len(group) < 2:
            continue

        comparable_values = [_to_decimal(record.value) for record in group]
        if any(value is None for value in comparable_values):
            continue

        values = [value for value in comparable_values if value is not None]
        if max(values) == min(values):
            continue

        canonical_metric_name, year, period, geography, unit = key
        severity = _classify_severity(values)
        likely_reason = _classify_likely_reason(group)

        discrepancies.append(
            DiscrepancyRecord(
                canonical_metric_name=canonical_metric_name,
                year=year,
                period=period,
                geography=geography,
                unit=unit,
                severity=severity,
                likely_reason=likely_reason,
                records=group,
                explanation=_build_explanation(group, values, severity, likely_reason),
                recommended_action=_build_recommended_action(group, severity, likely_reason),
            )
        )

    return discrepancies


def _to_decimal(value: float | int | str) -> Decimal | None:
    try:
        return Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return None


def _classify_severity(values: list[Decimal]) -> str:
    minimum = min(values)
    maximum = max(values)
    baseline = max(abs(minimum), Decimal("1"))
    relative_difference = (maximum - minimum) / baseline

    if relative_difference < Decimal("0.01"):
        return "low"
    if relative_difference <= Decimal("0.05"):
        return "medium"
    return "high"


def _classify_likely_reason(records: list[MetricRecord]) -> str:
    caveats = " | ".join(record.caveat or "" for record in records).lower()
    source_files = {record.source_file for record in records}
    metric_names = " | ".join(record.metric_name for record in records).lower()

    if "preliminary" in caveats and "revised" in caveats:
        return "preliminary_vs_revised"

    if _contains_any(caveats, ["formula", "range", "off by 1", "spreadsheet"]):
        return "formula_or_workbook_issue"

    if len(source_files) == 1:
        return "internal_document_conflict"

    if "rounded" in caveats:
        return "rounding_difference"

    if _contains_any(caveats, ["definition", "definition difference"]) or _metric_wording_differs(metric_names):
        return "definition_difference"

    return "unknown"


def _build_explanation(
    records: list[MetricRecord],
    values: list[Decimal],
    severity: str,
    likely_reason: str,
) -> str:
    sorted_values = sorted(values)
    metric = records[0].canonical_metric_name.replace("_", " ")
    location = _format_dimensions(records[0])
    source_values = "; ".join(
        f"{record.source_file} reports {record.value}" for record in records
    )
    return (
        f"{len(records)} sources report different values for {metric}{location}: "
        f"{sorted_values[0]} to {sorted_values[-1]}. "
        f"Source values: {source_values}. "
        f"This is a {severity} discrepancy. Likely reason: {likely_reason}."
    )


def _build_recommended_action(
    records: list[MetricRecord],
    severity: str,
    likely_reason: str,
) -> str:
    if likely_reason == "preliminary_vs_revised":
        return (
            "Use the revised annual report figure for external reporting, "
            "but retain the preliminary estimate as historical context."
        )

    if severity == "high" and likely_reason == "unknown":
        return (
            "Do not quote this figure externally until validated against an official source. "
            "Ask the source owner to confirm which figure is current."
        )

    if likely_reason == "internal_document_conflict":
        return (
            "Treat this as an internal contradiction. Resolve the conflict within the "
            "source document before using the figure in analysis or briefings."
        )

    if likely_reason == "formula_or_workbook_issue":
        return "Review the workbook formula or linked range before confirming the figure."

    if likely_reason == "rounding_difference":
        return "Confirm whether rounded and unrounded figures are both acceptable for the intended use."

    if likely_reason == "definition_difference":
        return "Check metric definitions before comparing or quoting these figures together."

    best_record = max(records, key=score_source_reliability)
    return (
        f"Review the source evidence and consider prioritising {best_record.source_file} "
        "if it is confirmed as the most authoritative source."
    )


def _format_dimensions(record: MetricRecord) -> str:
    parts = [
        str(record.year) if record.year else None,
        record.period,
        record.geography,
        record.unit,
    ]
    visible_parts = [part for part in parts if part]
    return f" ({', '.join(visible_parts)})" if visible_parts else ""


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _metric_wording_differs(metric_names: str) -> bool:
    return "share" in metric_names and "%" in metric_names
