from app.reconciliation.normalise import (
    canonicalise_metric_name,
    normalise_geography,
    normalise_unit,
    parse_numeric_value,
)


def test_canonicalise_uk_starts() -> None:
    assert canonicalise_metric_name("UK starts") == "housing_starts"


def test_canonicalise_completions() -> None:
    assert canonicalise_metric_name("completions") == "housing_completions"


def test_canonicalise_housing_completions() -> None:
    assert canonicalise_metric_name("Housing Completions") == "housing_completions"


def test_normalise_unit() -> None:
    assert normalise_unit(" Homes ") == "dwellings"
    assert normalise_unit("%") == "percent"
    assert normalise_unit("\u00a3") == "gbp"


def test_parse_numeric_value_with_commas() -> None:
    assert parse_numeric_value("132,460") == 132460


def test_parse_numeric_value_gbp_thousands() -> None:
    assert parse_numeric_value("\u00a3285k") == 285000


def test_parse_numeric_value_percent() -> None:
    assert parse_numeric_value("28%") == 28


def test_parse_numeric_value_millions() -> None:
    assert parse_numeric_value("1.2m") == 1200000


def test_normalise_geography() -> None:
    assert normalise_geography("  greater   london ") == "Greater London"
