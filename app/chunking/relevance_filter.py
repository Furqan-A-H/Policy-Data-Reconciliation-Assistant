from app.extraction.schema import SourceChunk

DEFAULT_POLICY_KEYWORDS = {
    "affordable",
    "completion",
    "delivery",
    "dwelling",
    "homelessness",
    "housing",
    "rent",
    "supply",
    "tenure",
}


def is_relevant_chunk(
    chunk: SourceChunk,
    keywords: set[str] | None = None,
) -> bool:
    """Return True when a chunk contains at least one policy metric keyword."""
    active_keywords = keywords or DEFAULT_POLICY_KEYWORDS
    text = chunk.text.lower()
    return any(keyword.lower() in text for keyword in active_keywords)


def filter_relevant_chunks(chunks: list[SourceChunk]) -> list[SourceChunk]:
    return [chunk for chunk in chunks if is_relevant_chunk(chunk)]
