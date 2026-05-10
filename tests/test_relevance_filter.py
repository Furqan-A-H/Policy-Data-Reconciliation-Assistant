from app.chunking.relevance_filter import is_relevant_chunk
from app.extraction.schema import SourceChunk


def _chunk(text: str) -> SourceChunk:
    return SourceChunk(
        chunk_id="chunk-1",
        source_file="briefing.docx",
        source_type="docx",
        source_location="paragraph 1",
        content_type="text",
        text=text,
        metadata={},
    )


def test_is_relevant_chunk_matches_policy_keyword() -> None:
    assert is_relevant_chunk(_chunk("The housing supply target increased."))


def test_is_relevant_chunk_rejects_unrelated_text() -> None:
    assert not is_relevant_chunk(_chunk("This paragraph describes meeting logistics."))
