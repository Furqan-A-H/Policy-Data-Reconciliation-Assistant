from app.extraction.schema import SourceChunk, TokenUsageReport


def estimate_tokens(text: str) -> int:
    """Approximate token count for budgeting before a tokenizer is selected."""
    return max(1, len(text.split()) * 4 // 3) if text else 0


def build_token_usage_report(
    *,
    files_processed: int,
    chunks_created: int,
    chunks_sent_to_llm: int,
    chunks: list[SourceChunk],
    estimated_output_tokens: int = 0,
) -> TokenUsageReport:
    estimated_input_tokens = sum(estimate_tokens(chunk.text) for chunk in chunks)
    chunks_skipped = max(0, chunks_created - chunks_sent_to_llm)
    saving_percent = (
        chunks_skipped / chunks_created * 100
        if chunks_created
        else 0.0
    )

    return TokenUsageReport(
        files_processed=files_processed,
        chunks_created=chunks_created,
        chunks_sent_to_llm=chunks_sent_to_llm,
        chunks_skipped=chunks_skipped,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=estimated_output_tokens,
        estimated_token_saving_percent=round(saving_percent, 2),
    )
