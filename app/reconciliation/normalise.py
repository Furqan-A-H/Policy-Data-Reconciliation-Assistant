import re

POUND_SYMBOL = "\u00a3"

CANONICAL_METRIC_ALIASES = {
    "housing starts": "housing_starts",
    "uk starts": "housing_starts",
    "new housing starts": "housing_starts",
    "starts": "housing_starts",
    "housing completions": "housing_completions",
    "completions": "housing_completions",
    "completed dwellings": "housing_completions",
    "affordable housing share": "affordable_housing_percentage",
    "affordable housing %": "affordable_housing_percentage",
    "affordable %": "affordable_housing_percentage",
    "average new-build price": "average_new_build_price",
    "avg new-build price": "average_new_build_price",
    "avg price": "average_new_build_price",
    "new build price": "average_new_build_price",
    "private sector share": "private_sector_share",
    "private sector %": "private_sector_share",
}

UNIT_ALIASES = {
    "dwelling": "dwellings",
    "dwellings": "dwellings",
    "home": "dwellings",
    "homes": "dwellings",
    "unit": "dwellings",
    "units": "dwellings",
    "percent": "percent",
    "%": "percent",
    "percentage": "percent",
    "gbp": "gbp",
    POUND_SYMBOL: "gbp",
}


def canonicalise_metric_name(metric_name: str) -> str:
    """Map known metric aliases to deterministic canonical names."""
    normalised_name = _normalise_label(metric_name)
    if normalised_name in CANONICAL_METRIC_ALIASES:
        return CANONICAL_METRIC_ALIASES[normalised_name]

    slug = re.sub(r"[^a-z0-9]+", "_", normalised_name).strip("_")
    return re.sub(r"_+", "_", slug)


def parse_numeric_value(value: str | int | float) -> float:
    """Parse common policy number formats into a plain numeric value."""
    if isinstance(value, int | float):
        return float(value)

    text = str(value).strip().lower()
    multiplier = 1

    if text.startswith(POUND_SYMBOL):
        text = text.removeprefix(POUND_SYMBOL).strip()

    if text.endswith("%"):
        text = text.removesuffix("%").strip()

    if text.endswith("k"):
        multiplier = 1_000
        text = text.removesuffix("k").strip()
    elif text.endswith("m"):
        multiplier = 1_000_000
        text = text.removesuffix("m").strip()

    text = text.replace(",", "")
    return float(text) * multiplier


def normalise_unit(unit: str) -> str:
    cleaned = _normalise_label(unit)
    return UNIT_ALIASES.get(cleaned, cleaned)


def normalise_geography(geography: str | None) -> str | None:
    if geography is None:
        return None
    return re.sub(r"\s+", " ", geography.strip()).title()


def _normalise_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())
