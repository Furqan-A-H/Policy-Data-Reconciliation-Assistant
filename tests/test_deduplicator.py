from app.chunking.deduplicator import deduplicate_chunks
from app.extraction.schema import SourceChunk


def _chunk(text: str, chunk_id: str) -> SourceChunk:
    return SourceChunk(
        chunk_id=chunk_id,
        source_file="briefing.docx",
        source_type="docx",
        source_location="paragraph 1",
        content_type="text",
        text=text,
        metadata={},
    )


def test_deduplicate_chunks_removes_repeated_text() -> None:
    unique_chunks, duplicate_count = deduplicate_chunks(
        [
            _chunk("Housing starts were 132,460.", "first"),
            _chunk("Housing starts were 132,460.", "second"),
        ]
    )

    assert [chunk.chunk_id for chunk in unique_chunks] == ["first"]
    assert duplicate_count == 1


def test_deduplicate_chunks_preserves_first_occurrence_after_normalisation() -> None:
    unique_chunks, duplicate_count = deduplicate_chunks(
        [
            _chunk(" Housing starts were 132,460. ", "first"),
            _chunk("housing   starts were 132,460.", "second"),
            _chunk("Housing completions were 174,180.", "third"),
        ]
    )

    assert [chunk.chunk_id for chunk in unique_chunks] == ["first", "third"]
    assert duplicate_count == 1
