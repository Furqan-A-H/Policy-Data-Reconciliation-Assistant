from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.extraction.schema import DiscrepancyRecord


def build_html_report(discrepancies: list[DiscrepancyRecord]) -> str:
    template_dir = Path(__file__).parent / "templates"
    environment = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )
    template = environment.get_template("report.html")
    return template.render(discrepancies=discrepancies)
