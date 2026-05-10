from app.extraction.schema import SourceChunk


def prepare_chunks_for_extraction(chunks: list[SourceChunk]) -> list[SourceChunk]:
    """Keep loader-created chunks and attach lightweight token metadata."""
    prepared_chunks: list[SourceChunk] = []

    for chunk in chunks:
        character_count = len(chunk.text)
        estimated_tokens = estimate_tokens_from_characters(character_count)
        metadata = {
            **chunk.metadata,
            "character_count": character_count,
            "estimated_tokens": estimated_tokens,
        }
        prepared_chunks.append(
            SourceChunk(
                chunk_id=chunk.chunk_id,
                source_file=chunk.source_file,
                source_type=chunk.source_type,
                source_location=chunk.source_location,
                content_type=chunk.content_type,
                text=chunk.text,
                metadata=metadata,
            )
        )

    return prepared_chunks


def estimate_tokens_from_characters(character_count: int) -> int:
    """Approximate tokens as one token per four characters."""
    if character_count <= 0:
        return 0
    return max(1, round(character_count / 4))


def split_text_into_chunks(
    text: str,
    *,
    source_file: str,
    source_type: str,
    max_words: int = 400,
) -> list[SourceChunk]:
    """Create simple word-bounded chunks until semantic chunking is added."""
    words = text.split()
    chunks: list[SourceChunk] = []

    for index in range(0, len(words), max_words):
        chunk_text = " ".join(words[index : index + max_words])
        chunks.append(
            SourceChunk(
                chunk_id=f"{source_file}:{index // max_words + 1}",
                source_file=source_file,
                source_type=source_type,
                source_location=f"chunk {index // max_words + 1}",
                content_type="text",
                text=chunk_text,
                metadata={"word_start": index},
            )
        )

    return chunks
