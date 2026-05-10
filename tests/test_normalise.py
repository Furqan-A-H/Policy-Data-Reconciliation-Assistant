from app.reconciliation.normalise import (
    canonicalise_metric_name,
    normalise_geography,
    normalise_unit,
)


def test_canonicalise_metric_name() -> None:
    assert canonicalise_metric_name("Affordable Housing Completions") == "affordable_housing_completions"


def test_normalise_unit() -> None:
    assert normalise_unit(" Homes ") == "homes"


def test_normalise_geography() -> None:
    assert normalise_geography("  greater   london ") == "Greater London"
