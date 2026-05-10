from app.extraction.schema import MetricRecord


def score_source_reliability(record: MetricRecord) -> float:
    """Return a simple deterministic reliability score for ranking sources."""
    text = f"{record.source_file} {record.source_type} {record.caveat or ''} {record.raw_text}".lower()

    if record.source_type == "api" and _contains_any(text, ["official", "live"]):
        return 1.0

    if "annual report" in text and "revised" in text:
        return 0.9

    if record.source_type == "xlsx":
        return 0.75

    if record.source_type == "pptx" and _contains_any(text, ["stakeholder", "preliminary"]):
        return 0.55

    return 0.5


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)
