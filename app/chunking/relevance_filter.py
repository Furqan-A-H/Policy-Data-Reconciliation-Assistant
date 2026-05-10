from app.extraction.schema import SourceChunk

DEFAULT_POLICY_KEYWORDS = {
    "affordable",
    "annual",
    "average price",
    "avg price",
    "completions",
    "dwellings",
    "housing starts",
    "new build",
    "new-build",
    "ons",
    "preliminary",
    "q1",
    "q2",
    "q3",
    "q4",
    "revised",
    "starts",
    "year-over-year",
    "yoy",
}


def is_relevant_chunk(
    chunk: SourceChunk,
    keywords: set[str] | None = None,
) -> bool:
    """Return True when a chunk contains at least one policy metric keyword."""
    active_keywords = keywords or DEFAULT_POLICY_KEYWORDS
    text = chunk.text.lower()
    return any(keyword.lower() in text for keyword in active_keywords)


def filter_relevant_chunks(
    chunks: list[SourceChunk],
) -> tuple[list[SourceChunk], list[SourceChunk]]:
    relevant_chunks: list[SourceChunk] = []
    skipped_chunks: list[SourceChunk] = []

    for chunk in chunks:
        if is_relevant_chunk(chunk):
            relevant_chunks.append(chunk)
        else:
            skipped_chunks.append(chunk)

    return relevant_chunks, skipped_chunks
