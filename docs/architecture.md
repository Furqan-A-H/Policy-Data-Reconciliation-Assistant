# Architecture

## End-To-End Pipeline

```text
sample_data/
  -> ingestion loaders
  -> SourceChunk records
  -> token metadata, filtering, deduplication
  -> rule-based extraction
  -> optional LLM extraction fallback
  -> MetricRecord records
  -> normalisation
  -> deterministic discrepancy detection
  -> JSON outputs and HTML report
```

The key boundary is between extraction and reconciliation. Extraction may use an
LLM for language understanding. Reconciliation remains deterministic Python.

## Module Responsibilities

- `app/ingestion`: reads Word, Excel, and PowerPoint files.
- `app/chunking`: adds token metadata, filters relevance, and removes duplicates.
- `app/extraction`: performs rule-first extraction and optional LLM fallback.
- `app/reconciliation`: normalises metrics and detects discrepancies.
- `app/reporting`: generates the analyst-facing HTML report.
- `app/pipeline.py`: orchestrates the full flow.
- `app/main.py`: exposes the API endpoints.

## Data Flow

`SourceChunk` carries source text with provenance. `MetricRecord` carries an
extracted metric with value, unit, time period, geography, confidence, caveat,
raw text, and provenance. `DiscrepancyRecord` groups conflicting records and
explains what needs review.

## Source Handling

DOCX files are parsed into paragraphs and table rows. XLSX files are parsed into
worksheet rows, including visible values and formulas. PPTX files are parsed into
slide text and slide table text. Each loader preserves source location, such as
`paragraph 4`, `sheet Summary row 5`, or `slide 2 table 1`.

## Modularity

The modular design keeps deterministic logic testable and keeps the LLM boundary
small. Ingestion, extraction, reconciliation, and reporting can evolve
independently.
