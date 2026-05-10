# Design Decisions

## No LangChain Or LangGraph Initially

The initial foundation avoids orchestration frameworks so the core pipeline remains easy to inspect and explain during a technical assessment.

## Deterministic Reconciliation

Numeric discrepancy detection is implemented in Python because policy analysts need reproducible, auditable results.

## Provenance First

Every metric record includes source file, type, location, extraction method, confidence, caveat, and raw text. This allows findings to be traced back to the original document.

## Modular Folders

Each stage of the pipeline has a separate package so unit tests can target behaviour without running the full API.
