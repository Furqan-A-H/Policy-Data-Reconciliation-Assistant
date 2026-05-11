# Architecture

## End-To-End Pipeline

The application follows a simple explicit pipeline:

```text
sample_data/
  -> ingestion loaders
  -> SourceChunk records
  -> chunk metadata, filtering, deduplication
  -> rule-based extraction
  -> optional LLM extraction fallback
  -> MetricRecord records
  -> normalisation
  -> deterministic discrepancy detection
  -> JSON outputs and HTML report
```

The important boundary is between extraction and reconciliation. Extraction can
use language understanding. Reconciliation is deterministic Python.

## Module Responsibilities

- `app/ingestion`: reads source files and creates provenance-aware chunks.
- `app/chunking`: adds token metadata, filters irrelevant chunks, and removes duplicates.
- `app/extraction`: extracts candidate metrics using rules first, then optional LLM fallback.
- `app/reconciliation`: normalises metrics, scores source reliability, and detects conflicts.
- `app/reporting`: creates analyst-facing HTML output.
- `app/pipeline.py`: orchestrates the full flow and writes outputs.
- `app/main.py`: exposes the pipeline and outputs through FastAPI.

## Data Flow

`SourceChunk` is the handoff object from ingestion to extraction. It includes:

- source file;
- source type;
- source location;
- content type;
- extracted text;
- metadata.

`MetricRecord` is the handoff object from extraction to reconciliation. It
includes:

- canonical metric name;
- value and unit;
- year, period, and geography;
- provenance;
- extraction method;
- confidence;
- caveat;
- raw supporting text.

`DiscrepancyRecord` is the final reconciliation finding. It keeps the grouped
records so an analyst can trace the issue back to source material.

## Why The Design Is Modular

The modules are separated so each stage can be tested independently. This is
important for an applied AI system because model behaviour should not be mixed
with deterministic business rules.

The design also makes the project easier to explain:

- ingestion can improve without changing discrepancy logic;
- prompt design can evolve without changing source parsing;
- source reliability scoring can be tuned without changing extraction;
- reporting can be redesigned without changing the pipeline contract.

## Source Handling

### Word

DOCX files are parsed with `python-docx`. The loader extracts paragraphs and
table rows. Provenance uses locations such as `paragraph 4` and `table 2 row 3`.

### Excel

XLSX files are parsed with `openpyxl`. The loader extracts worksheet rows and
includes both visible values and formulas where present. Provenance uses sheet
and row locations such as `sheet Summary row 5`.

### PowerPoint

PPTX files are parsed with `python-pptx`. The loader extracts slide text and
table text where available. Provenance uses locations such as `slide 2` and
`slide 4 table 1`.

## API Surface

The FastAPI app intentionally exposes a small surface:

- `GET /health`
- `POST /run-analysis`
- `GET /outputs/metrics`
- `GET /outputs/discrepancies`
- `GET /outputs/report`

This keeps the assessment focused on the data pipeline rather than UI work.
