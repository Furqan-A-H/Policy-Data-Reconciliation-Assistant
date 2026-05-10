from app.extraction.schema import MetricRecord


def score_source_reliability(record: MetricRecord) -> float:
    """Placeholder reliability score using extraction confidence only."""
    return record.confidence
