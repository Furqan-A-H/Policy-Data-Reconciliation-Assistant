# Prompt Design

## Purpose

The LLM is used only for candidate metric extraction. It is not used to decide
whether figures conflict, which figure is correct, or what should be reported
externally.

## Extraction Prompt Design

The extraction prompt is intentionally strict:

- extract only housing metrics explicitly present in the chunk;
- return JSON only;
- return an empty list when no relevant metric is present;
- include source provenance exactly as supplied;
- preserve raw supporting text;
- include confidence and caveats;
- avoid discrepancy detection or numeric judgement.

This makes the LLM a structured extraction component, not a decision maker.

## Why JSON Schema-Style Output Is Used

The downstream pipeline expects `MetricRecord` objects. JSON output gives a clear
contract between the model and the deterministic code.

The current implementation validates returned JSON into Pydantic models. In a
production version, I would tighten this further with OpenAI structured outputs
using a formal JSON schema.

## No Inference Of Missing Values

The prompt tells the LLM not to infer missing year, geography, period, value, or
unit. This matters because policy reconciliation depends on provenance and
traceability.

If a value is not present in the source chunk, the model should leave it missing
or return no record. Guessing would create false precision and increase
hallucination risk.

## Caveats And Confidence

The extraction schema includes:

- `confidence`;
- `caveat`;
- `raw_text`;
- source file, type, and location.

Caveats such as `preliminary`, `revised`, `rounded`, `formula issue`,
`definition difference`, and `not for external release` are important because
they affect how analysts interpret conflicts.

Confidence is not used to declare truth. It helps decide whether a chunk should
be reviewed or whether LLM fallback might be useful.

## Mock Mode

`MOCK_LLM=true` is the default. In mock mode, no external API call is made. The
client returns deterministic results for known sample-like text by reusing the
rule extraction path and marking records as `mock_llm`.

Mock mode exists for:

- local development without credentials;
- repeatable tests;
- predictable demos;
- assessment review where network access may not be available.

## Caching

LLM results are cached by chunk text and prompt version in
`.cache/llm_extractions`. This avoids paying repeatedly for the same extraction
during iterative development and makes token usage easier to explain.
