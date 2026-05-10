from app.extraction.llm_client import LLMClient
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


def test_mock_llm_extracts_known_metric(tmp_path) -> None:
    client = LLMClient()
    client.mock_llm = True
    client.cache_dir = tmp_path

    metrics = client.extract_metrics_from_chunk(
        _chunk("Preliminary UK starts 134,470")
    )

    assert len(metrics) == 1
    assert metrics[0].canonical_metric_name == "housing_starts"
    assert metrics[0].value == 134470
    assert metrics[0].geography == "UK"
    assert metrics[0].extraction_method == "mock_llm"
    assert metrics[0].caveat == "preliminary"


def test_llm_client_reuses_cache(tmp_path) -> None:
    client = LLMClient()
    client.mock_llm = True
    client.cache_dir = tmp_path
    chunk = _chunk("Housing Completions 174,180")

    first_result = client.extract_metrics_from_chunk(chunk)
    client.mock_llm = False
    second_result = client.extract_metrics_from_chunk(chunk)

    assert first_result == second_result
    assert len(list(tmp_path.glob("*.json"))) == 1
