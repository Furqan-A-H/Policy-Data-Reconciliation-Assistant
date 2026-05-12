# Prompt Design

## Purpose

The LLM is used only for candidate metric extraction. It is not used to decide
whether figures conflict, which figure is correct, or what should be reported
externally.

## Extraction Prompt Design

The prompt asks for JSON only and requires the model to extract only metrics
explicitly present in the chunk. It must preserve source file, source type,
source location, raw text, confidence, and caveats.

The LLM is instructed not to infer missing values, years, periods, geographies,
or units. If no relevant metric is present, it should return an empty list.

## Why JSON Output

The downstream pipeline validates LLM output into `MetricRecord` Pydantic models.
This makes the model boundary explicit and prevents malformed output from
entering deterministic reconciliation.

## Caveats And Confidence

Caveats such as `preliminary`, `revised`, `rounded`, `formula issue`,
`definition difference`, and `not for external release` are captured because
they affect how analysts interpret conflicting figures.

Confidence supports review and fallback decisions. It does not declare truth.

## Mock Mode

`MOCK_LLM=true` is the default. In mock mode, no external API call is made. This
supports local development, repeatable tests, demos, and assessment review
without credentials.

## Caching

LLM extraction results are cached by chunk text and prompt version in
`.cache/llm_extractions`. This avoids repeated cost during iterative runs.
