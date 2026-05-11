# Design Decisions

## FastAPI

FastAPI is a good fit for this assessment because it is lightweight, typed, and
simple to run locally. The project needs a small API surface rather than a full
web application.

The current endpoints expose health, analysis execution, and output retrieval.
That is enough to demonstrate the pipeline without adding frontend complexity.

## Pydantic

Pydantic is used for the core contracts:

- `SourceChunk`;
- `MetricRecord`;
- `DiscrepancyRecord`;
- `TokenUsageReport`.

These models make the LLM boundary safer because model outputs must validate
before entering reconciliation.

## Deterministic Discrepancy Detection

Discrepancy detection is deterministic because numeric comparison is an
audit-style task. The system groups records by metric, year, period, geography,
and unit, then compares numeric values directly.

This makes findings reproducible and explainable. The LLM is not allowed to
decide which numbers conflict or which value is correct.

## Lightweight LLM Wrapper

The project uses a small custom `LLMClient` rather than LangChain or LangGraph.
That keeps the LLM role narrow and inspectable:

- build prompt;
- call API or mock path;
- parse JSON;
- validate into `MetricRecord`;
- cache results.

For this prototype, a full orchestration framework would add more surface area
than value.

## Source Reliability Scoring

Source reliability scoring exists to support recommended actions. It does not
automatically declare truth.

The current model is intentionally simple:

- live official API: highest;
- revised annual report: high;
- Excel workbook: medium;
- preliminary stakeholder deck: lower;
- unknown: baseline.

In production, this should become configurable policy logic.

## Token Optimisation

Token optimisation is included because full-document LLM extraction is costly
and harder to explain.

The pipeline reduces token use through:

- chunk metadata;
- relevance filtering;
- deduplication;
- rule-first extraction;
- LLM fallback only where needed;
- cache reuse;
- token usage reporting.

This also reduces hallucination risk by sending less irrelevant text to the
model.
