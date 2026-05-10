from collections import defaultdict
from decimal import Decimal, InvalidOperation

from app.extraction.schema import DiscrepancyRecord, MetricRecord


def _to_decimal(value: float | int | str) -> Decimal | None:
    try:
        return Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return None


def detect_discrepancies(
    records: list[MetricRecord],
    *,
    absolute_tolerance: Decimal = Decimal("0"),
) -> list[DiscrepancyRecord]:
    """Flag records with matching dimensions but different numeric values."""
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
        numeric_values = [_to_decimal(record.value) for record in group]
        comparable_values = [value for value in numeric_values if value is not None]

        if len(group) < 2 or len(comparable_values) != len(group):
            continue

        if max(comparable_values) - min(comparable_values) <= absolute_tolerance:
            continue

        canonical_metric_name, year, period, geography, unit = key
        discrepancies.append(
            DiscrepancyRecord(
                canonical_metric_name=canonical_metric_name,
                year=year,
                period=period,
                geography=geography,
                unit=unit,
                severity="medium",
                likely_reason="Multiple sources report different numeric values.",
                records=group,
                explanation=(
                    f"Found {len(group)} records for {canonical_metric_name} "
                    "with inconsistent values."
                ),
                recommended_action="Review source provenance and confirm the authoritative value.",
            )
        )

    return discrepancies
