# Example Findings

This document describes the main housing-data discrepancies the system is meant
to surface. The logic is general and is not hardcoded to a single file.

## 2024 Preliminary Vs Revised Starts

A stakeholder deck may report 2024 UK housing starts around `134,470` with a
`preliminary` caveat, while a revised annual source reports `132,460`.

Expected outcome:

- canonical metric: `housing_starts`;
- year: `2024`;
- geography: `UK`;
- unit: `dwellings`;
- likely reason: `preliminary_vs_revised`.

The recommended action should favour the revised annual report figure for
external reporting while retaining the preliminary estimate as context.

## 2025 Internal Contradiction

One part of a 2025 report may show starts of `145,320` and completions of
`162,700`, while another part shows starts of `180,250` and completions of
`208,050`.

Expected outcome:

- starts and completions are treated as separate canonical metrics;
- conflicts from the same file are classified as `internal_document_conflict`;
- severity is high when the relative difference is above 5%.

## 2025 Stakeholder Deck Vs Report

A stakeholder deck may show 2025 UK starts around `156,200` or `154,500`, while
a report shows `180,250`.

Expected outcome:

- records are grouped when metric, year, geography, and unit match;
- the large difference is high severity;
- the report warns against quoting externally until validated.

## Caveats

The extractor captures explicit caveats such as `preliminary`, `revised`,
`warning`, `not for external release`, `rounded`, `formula`, and `off by 1`.
These caveats feed deterministic reason classification.
