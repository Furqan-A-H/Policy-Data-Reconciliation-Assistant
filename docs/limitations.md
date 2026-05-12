# Limitations

This is an assessment-ready prototype, not production software.

## Document Coverage

The loaders handle common text, rows, and tables. Chart extraction is limited.
The current implementation does not fully handle embedded images, OCR, complex
merged cells, speaker notes, or every Office layout edge case.

## LLM Extraction

LLM extraction can miss ambiguous figures or return malformed output. The app
validates model output and falls back safely, but extraction quality still
depends on source clarity and prompt quality.

## Source Reliability

Source reliability scoring is a simple heuristic. Production use would need
configurable rules agreed with policy owners.

## Human Review

Human review is still required. The tool identifies conflicts and recommends
next steps, but it does not automatically declare final truth.

## Production Gaps

A production system would need live official API integration, authentication,
authorisation, audit logs, secure file handling, persistence, background jobs,
and observability. JSON outputs are sufficient for the assessment scope.
