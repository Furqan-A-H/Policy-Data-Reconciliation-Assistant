import json
from pathlib import Path
from typing import Any

from app.chunking.deduplicator import deduplicate_chunks
from app.chunking.relevance_filter import filter_relevant_chunks
from app.chunking.semantic_chunker import prepare_chunks_for_extraction
from app.config import settings
from app.extraction.llm_client import LLMClient
from app.extraction.rule_extractor import extract_metrics_rule_based
from app.extraction.schema import DiscrepancyRecord, MetricRecord, SourceChunk
from app.extraction.token_budget import build_token_usage_report
from app.ingestion.base import available_loaders, load_files_from_directory
from app.reconciliation.discrepancy_detector import detect_discrepancies
from app.reporting.report_builder import build_html_report

METRICS_OUTPUT = "extracted_metrics.json"
DISCREPANCIES_OUTPUT = "discrepancies.json"
TOKEN_USAGE_OUTPUT = "token_usage_report.json"
HTML_REPORT_OUTPUT = "reconciliation_report.html"


def run_analysis(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Run the source-aware extraction and reconciliation pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)

    files_processed = _count_supported_files(input_dir)
    loaded_chunks = load_files_from_directory(input_dir)
    prepared_chunks = prepare_chunks_for_extraction(loaded_chunks)
    unique_chunks, duplicate_chunk_count = deduplicate_chunks(prepared_chunks)
    relevant_chunks, skipped_chunks = filter_relevant_chunks(unique_chunks)

    rule_metrics: list[MetricRecord] = []
    chunks_for_llm: list[SourceChunk] = []

    for chunk in relevant_chunks:
        extracted = extract_metrics_rule_based([chunk])
        rule_metrics.extend(extracted)

        if not extracted or max(metric.confidence for metric in extracted) < 0.8:
            chunks_for_llm.append(chunk)

    llm_client = LLMClient()
    llm_metrics: list[MetricRecord] = []
    for chunk in chunks_for_llm:
        llm_metrics.extend(llm_client.extract_metrics_from_chunk(chunk))

    metrics = _deduplicate_metric_records([*rule_metrics, *llm_metrics])
    discrepancies = detect_discrepancies(metrics)
    token_usage_report = build_token_usage_report(
        files_processed=files_processed,
        chunks_created=len(prepared_chunks),
        chunks_sent_to_llm=len(chunks_for_llm),
        chunks=chunks_for_llm,
        chunks_skipped=len(prepared_chunks) - len(chunks_for_llm),
        estimated_output_tokens=_estimate_output_tokens(llm_metrics),
    )

    metrics_path = output_dir / METRICS_OUTPUT
    discrepancies_path = output_dir / DISCREPANCIES_OUTPUT
    token_usage_path = output_dir / TOKEN_USAGE_OUTPUT
    report_path = output_dir / HTML_REPORT_OUTPUT

    _write_json(metrics_path, metrics)
    _write_json(discrepancies_path, discrepancies)
    _write_json(token_usage_path, token_usage_report)
    report_path.write_text(
        build_html_report(
            metrics=metrics,
            discrepancies=discrepancies,
            token_usage_report=token_usage_report,
            mock_llm=settings.mock_llm,
        ),
        encoding="utf-8",
    )

    return {
        "files_processed": files_processed,
        "chunks_loaded": len(loaded_chunks),
        "chunks_created": len(prepared_chunks),
        "duplicate_chunks_removed": duplicate_chunk_count,
        "chunks_relevant": len(relevant_chunks),
        "chunks_skipped": len(skipped_chunks),
        "chunks_sent_to_llm": len(chunks_for_llm),
        "metrics_extracted": len(metrics),
        "discrepancies_found": len(discrepancies),
        "output_file_paths": {
            "metrics": str(metrics_path.resolve()),
            "discrepancies": str(discrepancies_path.resolve()),
            "token_usage_report": str(token_usage_path.resolve()),
            "html_report": str(report_path.resolve()),
        },
    }


def _count_supported_files(input_dir: Path) -> int:
    if not input_dir.exists() or not input_dir.is_dir():
        return 0

    loaders = available_loaders()
    return sum(
        1
        for file_path in input_dir.rglob("*")
        if file_path.is_file() and any(loader.supports(file_path) for loader in loaders)
    )


def _deduplicate_metric_records(records: list[MetricRecord]) -> list[MetricRecord]:
    seen: set[str] = set()
    unique_records: list[MetricRecord] = []

    for record in records:
        digest = json.dumps(record.model_dump(mode="json"), sort_keys=True)
        if digest in seen:
            continue
        seen.add(digest)
        unique_records.append(record)

    return unique_records


def _estimate_output_tokens(records: list[MetricRecord]) -> int:
    return len(records) * 120


def _write_json(path: Path, payload: Any) -> None:
    if hasattr(payload, "model_dump"):
        serialisable = payload.model_dump(mode="json")
    elif isinstance(payload, list):
        serialisable = [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in payload
        ]
    else:
        serialisable = payload

    path.write_text(
        json.dumps(serialisable, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    summary = run_analysis(settings.input_dir, settings.output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
