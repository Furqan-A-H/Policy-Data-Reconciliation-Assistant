from app.extraction.schema import SourceChunk


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
