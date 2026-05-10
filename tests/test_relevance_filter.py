from app.chunking.deduplicator import deduplicate_chunks
from app.chunking.relevance_filter import filter_relevant_chunks, is_relevant_chunk
from app.chunking.semantic_chunker import prepare_chunks_for_extraction
from app.extraction.token_budget import build_token_usage_report
from app.extraction.schema import SourceChunk


def _chunk(text: str, chunk_id: str = "chunk-1") -> SourceChunk:
    return SourceChunk(
        chunk_id=chunk_id,
        source_file="briefing.docx",
        source_type="docx",
        source_location="paragraph 1",
        content_type="text",
        text=text,
        metadata={},
    )


def test_is_relevant_chunk_matches_policy_keyword() -> None:
    assert is_relevant_chunk(_chunk("Housing starts increased in Q2."))


def test_is_relevant_chunk_rejects_unrelated_text() -> None:
    assert not is_relevant_chunk(_chunk("This paragraph describes meeting logistics."))


def test_filter_relevant_chunks_skips_generic_policy_text() -> None:
    relevant_chunks, skipped_chunks = filter_relevant_chunks(
        [
            _chunk("The committee reviewed general policy governance.", "generic"),
            _chunk("Affordable completions reached 120 dwellings.", "metric"),
        ]
    )

    assert [chunk.chunk_id for chunk in relevant_chunks] == ["metric"]
    assert [chunk.chunk_id for chunk in skipped_chunks] == ["generic"]


def test_deduplicate_chunks_removes_normalised_duplicates() -> None:
    unique_chunks, duplicate_count = deduplicate_chunks(
        [
            _chunk(" Affordable completions reached 120 dwellings. ", "first"),
            _chunk("affordable   completions reached 120 dwellings.", "duplicate"),
            _chunk("Average price was revised in Q4.", "second"),
        ]
    )

    assert [chunk.chunk_id for chunk in unique_chunks] == ["first", "second"]
    assert duplicate_count == 1


def test_prepare_chunks_for_extraction_adds_token_metadata() -> None:
    prepared_chunks = prepare_chunks_for_extraction([_chunk("Affordable homes")])

    assert prepared_chunks[0].metadata["character_count"] == len("Affordable homes")
    assert prepared_chunks[0].metadata["estimated_tokens"] == 4


def test_build_token_usage_report_counts_savings() -> None:
    chunks = prepare_chunks_for_extraction(
        [
            _chunk("Affordable homes", "sent-1"),
            _chunk("Q1 starts", "sent-2"),
        ]
    )

    report = build_token_usage_report(
        files_processed=2,
        chunks_created=5,
        chunks_sent_to_llm=len(chunks),
        chunks=chunks,
        chunks_skipped=3,
        estimated_output_tokens=100,
    )

    assert report.files_processed == 2
    assert report.chunks_created == 5
    assert report.chunks_sent_to_llm == 2
    assert report.chunks_skipped == 3
    assert report.estimated_input_tokens == 6
    assert report.estimated_output_tokens == 100
    assert report.estimated_token_saving_percent == 60.0
