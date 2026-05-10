# Prompt Design

Prompts should be small, schema-first, and focused only on structured extraction.

Schema-first prompting is used because the extraction result must flow into
deterministic Python reconciliation. A strict shape makes validation, testing,
and provenance checks straightforward.

The LLM should be asked to:

- extract candidate housing metrics;
- preserve raw supporting text;
- include source provenance;
- provide confidence and caveats;
- avoid reconciling or judging conflicting numbers.

The LLM should not:

- decide which source is correct;
- invent missing years, units, or geographies;
- perform discrepancy severity scoring;
- produce unstructured data when a schema is expected.

## Numeric Judgement

The LLM is not used for numeric judgement because discrepancy detection must be
reproducible and explainable. The model may extract candidate `MetricRecord`
objects, but Python rules decide whether values conflict.

## Mock Mode

`MOCK_LLM=true` lets the project run without an API key. This is useful for local
development, tests, demos, and technical assessment review because the pipeline
can exercise the LLM boundary without making network calls.

## Caching

LLM extraction results are cached by chunk text and prompt version. This avoids
paying repeatedly for the same chunk during iterative development and keeps
token usage easier to explain.
