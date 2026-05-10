import re


def canonicalise_metric_name(metric_name: str) -> str:
    """Normalise a metric label for deterministic grouping."""
    cleaned = re.sub(r"[^a-z0-9]+", "_", metric_name.lower()).strip("_")
    return re.sub(r"_+", "_", cleaned)


def normalise_unit(unit: str) -> str:
    return unit.strip().lower()


def normalise_geography(geography: str | None) -> str | None:
    if geography is None:
        return None
    return re.sub(r"\s+", " ", geography.strip()).title()
