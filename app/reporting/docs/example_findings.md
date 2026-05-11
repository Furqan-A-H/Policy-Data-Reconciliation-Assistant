# Example Findings

This document describes the main housing-data discrepancies the system is meant
to make obvious in the sample assessment data. The logic is general; it is not
hardcoded to specific filenames.

## 2024 Preliminary Vs Revised Starts

The sample data may contain a stakeholder deck figure for 2024 UK housing starts
around `134,470` with a `preliminary` caveat. A revised annual source may report
`132,460`.

Expected outcome:

- canonical metric: `housing_starts`;
- year: `2024`;
- geography: `UK`;
- unit: `dwellings`;
- severity: medium;
- likely reason: `preliminary_vs_revised`.

The recommended action should tell the analyst to use the revised annual report
figure for external reporting, while retaining the preliminary estimate as
historical context.

## 2025 Internal Contradiction

The sample data may contain one part of a 2025 report showing:

- housing starts: `145,320`;
- completions: `162,700`.

Another part of the same report may show:

- housing starts: `180,250`;
- completions: `208,050`.

Expected outcome:

- starts and completions are treated as separate canonical metrics;
- both conflicts are high severity because the relative differences are large;
- if records come from the same source file, the likely reason is
  `internal_document_conflict`.

The recommended action should tell the analyst to resolve the contradiction
inside the source document before using the figure in analysis or briefings.

## 2025 Stakeholder Deck Vs Report Difference

The sample data may contain a stakeholder deck showing 2025 UK starts around
`156,200` as preliminary, or around `154,500` as revised. A report may show
`180,250`.

Expected outcome:

- grouped as the same canonical metric when year, geography, and unit match;
- high severity because the difference is above 5%;
- recommended action should warn against quoting the figure externally until it
  is validated against an official source or source owner.

## Caveats Around Preliminary Data

Caveats matter because they often explain why figures differ. The extractor
captures explicit caveat phrases such as:

- `preliminary`;
- `revised`;
- `warning`;
- `not for external release`;
- `rounded`;
- `formula`;
- `off by 1`.

These caveats feed deterministic reason classification. For example,
`preliminary` plus `revised` becomes `preliminary_vs_revised`; formula-related
caveats become `formula_or_workbook_issue`.

## How The Report Should Surface These Findings

The HTML report sorts high severity discrepancies first and includes:

- metric;
- year and period;
- geography;
- source A and source B;
- values;
- severity;
- likely reason;
- recommended action.

The goal is not to produce a final policy answer automatically. The goal is to
make conflicts obvious enough that a nontechnical analyst knows where review is
needed.
