# Architecture

The assistant is organised around a narrow, auditable pipeline:

1. Ingestion loads document content while preserving source location.
2. Chunking creates token-aware `SourceChunk` records.
3. Relevance filtering reduces unnecessary LLM calls.
4. Extraction converts chunks into structured `MetricRecord` objects.
5. Normalisation creates deterministic comparison keys.
6. Discrepancy detection compares numeric values in Python.
7. Reporting presents findings in policy-friendly language.

The main architectural boundary is between extraction and reconciliation. Extraction may use an LLM when rules are insufficient. Reconciliation must remain deterministic.
