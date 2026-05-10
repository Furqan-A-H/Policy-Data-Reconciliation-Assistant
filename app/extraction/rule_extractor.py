import re

from app.extraction.schema import MetricRecord, SourceChunk
from app.reconciliation.normalise import (
    canonicalise_metric_name,
    normalise_unit,
    parse_numeric_value,
)

POUND_SYMBOL = "\u00a3"

METRIC_ALIASES = [
    "affordable housing share",
    "affordable housing %",
    "average new-build price",
    "avg new-build price",
    "housing completions",
    "new housing starts",
    "completed dwellings",
    "private sector share",
    "private sector %",
    "new build price",
    "affordable %",
    "housing starts",
    "completions",
    "uk starts",
    "avg price",
    "starts",
]

CAVEAT_TERMS = [
    "preliminary",
    "revised",
    "rounded",
    "formula",
    "off by 1",
    "warning",
]

VALUE_PATTERN = re.compile(
    rf"(?P<value>(?:{POUND_SYMBOL})?-?\d+(?:,\d{{3}})*(?:\.\d+)?(?:k|m|%)?)",
    re.IGNORECASE,
)
YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
PERIOD_PATTERN = re.compile(r"\b(q[1-4]|annual)\b", re.IGNORECASE)
GEOGRAPHY_PATTERN = re.compile(r"\b(uk|england)\b", re.IGNORECASE)


def extract_metrics_rule_based(chunks: list[SourceChunk]) -> list[MetricRecord]:
    """Extract obvious metric/value pairs without using the LLM."""
    metrics: list[MetricRecord] = []

    for chunk in chunks:
        for text_part in _split_text_parts(chunk.text):
            metrics.extend(_extract_from_text_part(chunk, text_part))

    return metrics


def extract_metrics_with_rules(chunk: SourceChunk) -> list[MetricRecord]:
    """Compatibility wrapper for extracting from one chunk."""
    return extract_metrics_rule_based([chunk])


def _extract_from_text_part(chunk: SourceChunk, text: str) -> list[MetricRecord]:
    lower_text = text.lower()

    for alias in METRIC_ALIASES:
        alias_match = re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", lower_text)
        if not alias_match:
            continue

        value_match = _find_value_near_alias(text, alias_match.end())
        if value_match is None:
            continue

        raw_value = value_match.group("value")
        metric_name = text[alias_match.start() : alias_match.end()].strip()
        return [
            MetricRecord(
                metric_name=metric_name,
                canonical_metric_name=canonicalise_metric_name(alias),
                value=parse_numeric_value(raw_value),
                unit=_infer_unit(alias, raw_value),
                year=_extract_year(text),
                period=_extract_period(text),
                geography=_extract_geography(text, alias),
                source_file=chunk.source_file,
                source_type=chunk.source_type,
                source_location=chunk.source_location,
                extraction_method="rule_based",
                confidence=0.85,
                caveat=_extract_caveat(text),
                raw_text=text,
            )
        ]

    return []


def _split_text_parts(text: str) -> list[str]:
    parts = [line.strip() for line in text.splitlines() if line.strip()]
    return parts or [text.strip()]


def _find_value_near_alias(text: str, alias_end: int) -> re.Match[str] | None:
    search_window = text[alias_end : alias_end + 80]

    for match in VALUE_PATTERN.finditer(search_window):
        value = match.group("value")
        if value.startswith("-") and value.endswith("%"):
            continue
        return match

    return None


def _extract_year(text: str) -> int | None:
    match = YEAR_PATTERN.search(text)
    return int(match.group(1)) if match else None


def _extract_period(text: str) -> str | None:
    match = PERIOD_PATTERN.search(text)
    if not match:
        return None

    period = match.group(1)
    return period.upper() if period.lower().startswith("q") else period.lower()


def _extract_geography(text: str, alias: str) -> str | None:
    if alias.lower().startswith("uk "):
        return "UK"

    match = GEOGRAPHY_PATTERN.search(text)
    if not match:
        return None

    geography = match.group(1)
    return "UK" if geography.lower() == "uk" else geography.title()


def _infer_unit(alias: str, raw_value: str) -> str:
    alias_lower = alias.lower()
    if POUND_SYMBOL in raw_value or "price" in alias_lower:
        return normalise_unit("gbp")
    if "%" in raw_value or "share" in alias_lower:
        return normalise_unit("percent")
    return normalise_unit("dwellings")


def _extract_caveat(text: str) -> str | None:
    text_lower = text.lower()
    matches = [term for term in CAVEAT_TERMS if term in text_lower]
    return ", ".join(matches) if matches else None
