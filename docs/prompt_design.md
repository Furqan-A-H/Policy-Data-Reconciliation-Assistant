# Prompt Design

Prompts should be small, schema-first, and focused only on structured extraction.

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
