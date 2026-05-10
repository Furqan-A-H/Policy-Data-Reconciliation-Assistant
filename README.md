# Policy Data Reconciliation Assistant

## Problem

Housing policy analysts often receive related data points across Word briefings, Excel workbooks, and PowerPoint decks. The same metric may appear with different labels, locations, periods, units, caveats, or levels of precision. Manually reconciling those figures is slow, difficult to audit, and error-prone.

## Solution

This project is the foundation for a FastAPI-based reconciliation assistant. It will ingest policy source documents, extract structured housing metrics, normalise those metrics, detect numeric discrepancies using deterministic Python, and generate a policy-friendly report for nontechnical analysts.

The intended workflow is:

1. Load content from `.docx`, `.xlsx`, and `.pptx` files.
2. Split content into source chunks with provenance.
3. Filter and deduplicate chunks before any LLM call.
4. Extract metrics into a strict Pydantic schema.
5. Normalise labels, units, periods, and geographies.
6. Detect discrepancies deterministically.
7. Build a clear reconciliation report with source references.

## Architecture Idea

The codebase is deliberately modular:

- `app/ingestion` handles source-specific file loading.
- `app/chunking` prepares token-aware chunks and filters irrelevant content.
- `app/extraction` owns prompts, schema contracts, token budgeting, and the LLM client boundary.
- `app/reconciliation` owns deterministic normalisation, reliability scoring, and discrepancy detection.
- `app/reporting` turns reconciled results into analyst-friendly output.

Every extracted metric must carry provenance: source file, source type, source location, raw text, extraction method, confidence, and caveats.

## Token And Cost Optimisation

The assistant should not send full documents to the LLM by default. Loader-created chunks are first enriched with simple token estimates, then filtered for housing metric keywords and deduplicated using a normalised text hash.

This keeps the extraction stage cheaper, faster, and easier to explain:

- irrelevant policy prose is skipped;
- repeated boilerplate is sent once;
- every skipped and retained chunk can still be counted;
- token savings are reported through `TokenUsageReport`.

## Why The LLM Is Used Only For Extraction

The LLM is useful for turning messy policy text into structured records, especially when tables, slide bullets, and prose use inconsistent language. It should not decide whether numbers conflict. That decision must remain inspectable, reproducible, and testable.

In this design, the LLM boundary is narrow:

- identify relevant text;
- extract metric candidates into a strict schema;
- optionally draft a final plain-language summary.

## Why Discrepancy Detection Is Deterministic

Numeric reconciliation is a policy audit task. Analysts need to know exactly why two records were flagged and be able to reproduce the result. Deterministic Python rules are easier to test, explain, and defend than model-generated judgments.

The reconciliation layer will compare normalised metric records by canonical metric name, time period, geography, unit, and numeric value. Severity and recommended action should be based on transparent rules.

## Current Project Status

This repository currently contains the initial project foundation only:

- FastAPI app shell with health endpoints.
- End-to-end local pipeline that reads `sample_data/` and writes JSON outputs.
- Configuration loading.
- Core Pydantic schemas.
- Source-aware ingestion for Word, PowerPoint, and Excel files.
- Token-aware chunk metadata, relevance filtering, and deduplication.
- Rule-based extraction, mock LLM extraction, and deterministic discrepancy detection.
- Placeholder reporting module.
- Minimal tests for early deterministic helpers.
- Architecture and design documentation.

Complex business logic, real LLM extraction, persistence, authentication, and production deployment hardening are intentionally out of scope for this initial scaffold.

Run the local pipeline from the project root with:

```powershell
python -m app.pipeline
```

Or start the API and call:

```text
POST /run-analysis
GET /outputs/metrics
GET /outputs/discrepancies
GET /outputs/report
```
