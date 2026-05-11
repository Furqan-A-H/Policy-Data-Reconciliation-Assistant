# Policy Data Reconciliation Assistant

## 1. Project Overview

Policy Data Reconciliation Assistant is a FastAPI-based technical assessment project for reconciling housing policy metrics across Word, Excel, and PowerPoint sources.

The project demonstrates a modular applied AI design: use language models where language understanding helps, but keep numeric comparison, discrepancy detection, and source reasoning deterministic and auditable.

The tool does not automatically declare the final truth. It helps analysts identify conflicts, inspect provenance, and decide where human review is needed.

## 2. Problem Being Solved

Policy teams often receive the same housing metric in multiple formats:

- a Word briefing may describe revised annual housing starts;
- an Excel workbook may contain workbook rows and formula-derived values;
- a PowerPoint deck may contain preliminary stakeholder-facing figures.

The same metric can appear with different wording, caveats, periods, geographies, or values. Manually checking these sources is slow and easy to get wrong.

## 3. Why This Matters For Policy Teams

Housing metrics are often used in briefings, public reporting, internal dashboards, and ministerial submissions. Quoting the wrong figure can undermine trust and create avoidable rework.

Policy analysts need:

- clear provenance for every extracted figure;
- visibility of preliminary, revised, rounded, or caveated values;
- deterministic comparison of numeric values;
- plain-English explanations of conflicts;
- a workflow that supports human judgement rather than replacing it.

## 4. What The Tool Does

The assistant currently:

- loads `.docx`, `.xlsx`, and `.pptx` files from `sample_data/`;
- converts source content into provenance-aware chunks;
- estimates tokens and filters irrelevant chunks before any LLM call;
- extracts obvious metrics with deterministic rules first;
- supports mock LLM extraction by default;
- can call OpenAI for schema-first extraction when configured;
- normalises metric names, units, and numeric values;
- detects discrepancies using deterministic Python;
- generates JSON outputs and a policy-friendly HTML reconciliation report.

## Domain Scope

The ingestion and reconciliation pipeline is designed to be reusable across
Word, Excel, and PowerPoint policy documents. However, the current metric
taxonomy and rule-based extraction patterns are intentionally scoped to the
housing policy assessment.

The project is not hardcoded to one sample file, but it does expect
housing-related metrics such as housing starts, completions, affordable housing
percentage, and new-build prices.

To support another policy domain, the main extension points would be the
canonical metric mappings, keyword relevance filters, and rule-based extraction
patterns. The deterministic reconciliation and reporting layers would remain
largely unchanged.

## 5. Architecture Diagram

```text
sample_data/
    |
    v
Ingestion Layer
  - Word paragraphs and tables
  - Excel worksheet rows, formulas, visible values
  - PowerPoint slide text and tables
    |
    v
SourceChunk objects with provenance
    |
    v
Token Optimisation Layer
  - chunk metadata
  - relevance filtering
  - deduplication
    |
    v
Extraction Layer
  - rule-based extraction first
  - LLM fallback when needed
  - mock LLM mode for local/test runs
  - cached LLM responses
    |
    v
MetricRecord objects
    |
    v
Reconciliation Layer
  - canonical metric names
  - unit and value normalisation
  - deterministic discrepancy detection
  - source reliability scoring
    |
    v
Reporting Layer
  - extracted_metrics.json
  - discrepancies.json
  - token_usage_report.json
  - reconciliation_report.html
```

## 6. Data Ingestion Approach

### Word

The DOCX loader uses `python-docx` to extract:

- paragraphs;
- table rows.

Each extracted chunk includes source provenance such as `paragraph 4` or `table 2 row 3`.

### Excel

The Excel loader uses `openpyxl` to extract worksheet rows. It preserves:

- sheet name;
- row number;
- visible values;
- formula text where a cell contains a formula.

Example provenance: `sheet Summary row 5`.

### PowerPoint

The PPTX loader uses `python-pptx` to extract:

- slide text;
- table text from slides where available.

Example provenance: `slide 2` or `slide 4 table 1`.

## 7. LLM Design

The LLM is used only for candidate metric extraction and optional summary-style language. It is not used for numeric judgement.

The extraction prompt is schema-first:

- extract only housing metrics explicitly present in the chunk;
- return JSON only;
- do not infer missing values;
- do not guess missing year, geography, period, or unit;
- include confidence and caveats;
- include `source_file`, `source_type`, and `source_location`;
- return an empty list if no relevant metric is present.

This reduces hallucination risk because the model is constrained to structured extraction. The downstream Python code validates outputs into `MetricRecord` objects.

`MOCK_LLM=true` is the default so the project can run, demo, and test without an API key.

The default real model is `gpt-4o-mini`. I chose it as a practical default for
this prototype because the LLM task is narrow structured extraction, where low
latency and lower cost matter more than long-form reasoning. The model name is
configurable through `OPENAI_MODEL`, and the rest of the system depends on the
`MetricRecord` schema rather than on a specific provider or model.

## 8. Why Discrepancy Detection Is Deterministic

Numeric reconciliation is an audit-style task. Analysts need to know exactly why two values were flagged.

For that reason, discrepancy detection is deterministic Python:

- records are grouped by canonical metric, year, period, geography, and unit;
- numeric values are compared directly;
- severity is calculated from relative difference;
- likely reasons are classified from explicit source properties and caveats.

The LLM does not decide whether two figures conflict and does not choose the authoritative source.

## 9. Token And Cost Optimisation

The tool is designed not to send full documents to the LLM.

Current controls:

- **Semantic chunking:** loader-created chunks are kept as the initial meaningful unit, with character and token estimates added.
- **Relevance filtering:** chunks are filtered using housing metric keywords and caveat indicators.
- **Deduplication:** repeated chunks are removed using a normalised text hash.
- **Rule-first extraction:** obvious metrics are extracted before using the LLM.
- **LLM fallback:** only chunks not confidently handled by rules are sent to the LLM.
- **Caching:** LLM extraction results are cached by chunk text and prompt version.
- **Token usage report:** the pipeline writes `token_usage_report.json` showing chunks created, skipped, sent to the LLM, and estimated savings.

This design reduces token cost and limits the amount of text exposed to the model.

## 10. Source Reliability Model

The project includes a simple deterministic source reliability score:

- API/live official source: `1.0`
- revised annual report: `0.9`
- Excel workbook: `0.75`
- preliminary stakeholder PowerPoint: `0.55`
- unknown: `0.5`

This is intentionally simple. It is used to support recommended actions, not to automatically declare truth.

## 11. Example Findings From The Housing Sample Data

The system is designed to surface findings such as:

- **2024 preliminary vs revised:** a stakeholder deck reports UK starts around `134,470` as preliminary, while a revised annual source reports `132,460`. This should be flagged as `preliminary_vs_revised`.
- **2025 internal contradiction:** one part of a 2025 report shows starts of `145,320` and completions of `162,700`, while another part shows starts of `180,250` and completions of `208,050`. If these come from the same file, they should be flagged as `internal_document_conflict`.
- **2025 deck vs report:** a stakeholder deck reports 2025 UK starts around `156,200` or revised around `154,500`, while a report shows `180,250`. This should be a high severity discrepancy.

These examples are not hardcoded. They fall out of canonical metric mapping, caveat detection, deterministic grouping, and relative difference scoring.

More detail is in `docs/example_findings.md`.

## 12. How To Run Locally

Clone the repository:

```powershell
git clone https://github.com/Furqan-A-H/Policy-Data-Reconciliation-Assistant.git
cd Policy-Data-Reconciliation-Assistant
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

By default the project runs in mock LLM mode, so no API key is required:

```env
MOCK_LLM=true
```

To use a real OpenAI model, copy `.env.example` to `.env` and add your own API
key:

Then update `.env`:

```env
MOCK_LLM=false
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

```powershell
Copy-Item .env.example .env
```



Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Add input files to:

```text
sample_data/
```

Supported file types are `.docx`, `.xlsx`, and `.pptx`.

Run the analysis:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/run-analysis
```

`/run-analysis` is a POST endpoint, so entering it directly in a browser address
bar will not run the analysis. Use the PowerShell command above or the FastAPI
docs page.

Or run the pipeline directly:

```powershell
python -m app.pipeline
```

## 13. How To Run With Docker

- git clone https://github.com/Furqan-A-H/Policy-Data-Reconciliation-Assistant.git

- cd Policy-Data-Reconciliation-Assistant

- Put `.docx`, `.xlsx`, or `.pptx` files into:
- sample_data/

- Start Docker Desktop.

- Build and run the FastAPI container:
- docker compose up --build

- The service will be available at:
- http://127.0.0.1:8000

- Interactive API documentation is available at:
- http://127.0.0.1:8000/docs

- Run the analysis from another PowerShell window:
- Invoke-RestMethod -Method Post http://127.0.0.1:8000/run-analysis

- View the generated HTML report:
- http://127.0.0.1:8000/outputs/report

- Generated output files appear locally in:
- outputs/

The compose file mounts:
- `./sample_data` to `/app/sample_data`;
- `./outputs` to `/app/outputs`;
- `./.cache` to `/app/.cache`.

Stop the container:
docker compose down


## 14. How To Run Tests

- After installing requirements:
- pytest


The tests use mock LLM mode and do not require external API calls.

Current test coverage includes:

- normalisation;
- relevance filtering;
- deduplication;
- ingestion loaders;
- rule extraction;
- mock LLM extraction and caching;
- deterministic discrepancy detection;
- pipeline smoke coverage.

## 15. Outputs Generated

The pipeline writes files to `outputs/`:

- `extracted_metrics.json`
- `discrepancies.json`
- `token_usage_report.json`
- `reconciliation_report.html`

API endpoints:

GET /outputs/metrics
GET /outputs/discrepancies
GET /outputs/report


## 16. Limitations And Risks

This is not production-ready software. It is an assessment-ready foundation.

Known limitations:

- document parsing handles common structures, not every possible Office edge case;
- rule extraction is deliberately conservative;
- LLM extraction depends on prompt quality and schema validation;
- source reliability scoring is a simple heuristic;
- no persistent database is included;
- no authentication or user management is included;
- no asynchronous job queue is included;
- no full observability stack is included.

The main risk is false confidence. The tool should support analyst review, not replace it.

## 17. What I Would Do With More Time

Next steps I would prioritise:

- add richer sample data and expected-output fixtures;
- introduce structured OpenAI JSON schema output instead of plain JSON mode;
- add a review UI for accepting, rejecting, or annotating discrepancies;
- persist runs, source files, extracted metrics, and analyst decisions;
- add confidence calibration based on source type and extraction method;
- improve source reliability with configurable policy rules;
- add OpenTelemetry-style tracing for ingestion and extraction steps;
- add background processing for large document batches;
- add export to PDF or Word for analyst circulation.

## 18. Why I Did Not Use LangGraph Or A Full Agent Framework

I avoided LangGraph, LangChain, and a full agent framework deliberately.

For this assessment, the core challenge is not autonomous planning. It is reliable document ingestion, schema-constrained extraction, deterministic reconciliation, and clear provenance.

A framework could be useful later if the workflow becomes multi-step, interactive, or tool-rich. At this stage, a small explicit pipeline is easier to test, easier to explain, and less likely to hide important behaviour behind orchestration abstractions.

That is the lead-engineering tradeoff here: keep the AI boundary narrow, keep the comparison logic auditable, and make the system understandable before adding orchestration complexity.
