# Limitations

This is an assessment-ready prototype, not a production system.

## Document Coverage

Office parsing handles common text, rows, and tables. It does not fully extract
charts, embedded images, speaker notes, complex merged-cell logic, or every
possible document layout.

Chart extraction is especially limited. A production version would need chart
data extraction, image OCR, or access to the original chart data sources.

## LLM Extraction Risk

LLM extraction can miss ambiguous figures or produce malformed output. The code
validates model output into Pydantic records and falls back safely on invalid
JSON or API errors, but extraction quality still depends on source clarity and
prompt quality.

The LLM is not allowed to infer missing values, which is safer but can reduce
recall.

## Source Reliability

Source reliability scoring is simple and heuristic-based. It is useful for
demonstrating the design, but production use would need configurable rules agreed
with policy owners.

## Human Review

Human review is still required. The tool identifies conflicts and recommends
next steps, but it does not automatically declare the final truth.

## Official Data Integration

A production system would likely need live official API integration for
authoritative figures and release metadata. The current prototype supports an
`api` source type in the schema, but does not implement live official data
retrieval.

## Security And Operations

Authentication is not included because this is a prototype. A real deployment
would need authentication, authorisation, audit logs, secure file handling, and
environment-specific configuration.

No database is included. JSON outputs are enough for assessment scope, but a
production system would need persistence for runs, source files, extracted
metrics, review decisions, and report history.

## Processing Model

The pipeline runs synchronously. Large document batches would need background
jobs, progress tracking, retries, and observability.
