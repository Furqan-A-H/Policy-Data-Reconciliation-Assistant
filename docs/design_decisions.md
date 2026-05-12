# Design Decisions

## FastAPI

FastAPI keeps the API small, typed, and easy to run locally. The project needs a
simple backend surface rather than a full UI.

## Pydantic

Pydantic models define the contracts between pipeline stages: `SourceChunk`,
`MetricRecord`, `DiscrepancyRecord`, and `TokenUsageReport`.

## Deterministic Discrepancy Detection

Numeric comparison is an audit-style task, so it is implemented in deterministic
Python. The LLM extracts candidate records; Python decides whether values
conflict.

## Lightweight LLM Wrapper

The project uses a small custom `LLMClient` instead of LangChain or LangGraph.
That keeps prompt construction, API calls, JSON parsing, validation, and caching
easy to inspect.

## Source Reliability

Source reliability scoring supports recommended actions. It does not
automatically declare the authoritative value. The current scoring is simple and
would become configurable in production.

## Token Optimisation

Token optimisation is included to reduce cost and hallucination risk. The
pipeline uses relevance filtering, deduplication, rule-first extraction, LLM
fallback, caching, and token usage reporting.
