from app.extraction.schema import SourceChunk, TokenUsageReport


def estimate_tokens(text: str) -> int:
    """Approximate token count for budgeting before a tokenizer is selected."""
    return max(1, round(len(text) / 4)) if text else 0


def build_token_usage_report(
    *,
    files_processed: int,
    chunks_created: int,
    chunks_sent_to_llm: int,
    chunks: list[SourceChunk],
    chunks_skipped: int | None = None,
    estimated_output_tokens: int = 0,
) -> TokenUsageReport:
    estimated_input_tokens = sum(_chunk_token_estimate(chunk) for chunk in chunks)
    skipped_count = (
        chunks_skipped
        if chunks_skipped is not None
        else max(0, chunks_created - chunks_sent_to_llm)
    )
    saving_percent = (
        skipped_count / chunks_created * 100
        if chunks_created
        else 0.0
    )

    return TokenUsageReport(
        files_processed=files_processed,
        chunks_created=chunks_created,
        chunks_sent_to_llm=chunks_sent_to_llm,
        chunks_skipped=skipped_count,
        estimated_input_tokens=estimated_input_tokens,
        estimated_output_tokens=estimated_output_tokens,
        estimated_token_saving_percent=round(saving_percent, 2),
    )


def _chunk_token_estimate(chunk: SourceChunk) -> int:
    metadata_value = chunk.metadata.get("estimated_tokens")
    if isinstance(metadata_value, int):
        return metadata_value
    return estimate_tokens(chunk.text)
