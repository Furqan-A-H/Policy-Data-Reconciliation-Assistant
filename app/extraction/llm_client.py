import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.config import settings
from app.extraction.prompts import (
    METRIC_EXTRACTION_SYSTEM_PROMPT,
    PROMPT_VERSION,
    build_metric_extraction_user_prompt,
)
from app.extraction.rule_extractor import extract_metrics_rule_based
from app.extraction.schema import MetricRecord, SourceChunk

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM boundary for structured metric extraction only."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.openai_model
        self.mock_llm = settings.mock_llm
        self.cache_dir = settings.cache_dir

    def extract_metrics_from_chunk(self, chunk: SourceChunk) -> list[MetricRecord]:
        cache_path = self._cache_path(chunk)
        cached = self._read_cache(cache_path)
        if cached is not None:
            return cached

        if self.mock_llm:
            metrics = self._extract_mock(chunk)
        else:
            metrics = self._extract_openai(chunk)

        self._write_cache(cache_path, metrics)
        return metrics

    def _extract_mock(self, chunk: SourceChunk) -> list[MetricRecord]:
        rule_metrics = extract_metrics_rule_based([chunk])
        return [
            metric.model_copy(
                update={
                    "extraction_method": "mock_llm",
                    "confidence": min(metric.confidence, 0.8),
                }
            )
            for metric in rule_metrics
        ]

    def _extract_openai(self, chunk: SourceChunk) -> list[MetricRecord]:
        if not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY is not set; returning no LLM metrics.")
            return []

        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": METRIC_EXTRACTION_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": build_metric_extraction_user_prompt(
                            source_file=chunk.source_file,
                            source_type=chunk.source_type,
                            source_location=chunk.source_location,
                            text=chunk.text,
                        ),
                    },
                ],
            )
            content = response.choices[0].message.content or "[]"
            return self._validate_records(json.loads(content), chunk, "llm")
        except (json.JSONDecodeError, ValidationError, Exception) as exc:
            logger.warning("LLM extraction failed for %s: %s", chunk.chunk_id, exc)
            return []

    def _validate_records(
        self,
        payload: Any,
        chunk: SourceChunk,
        extraction_method: str,
    ) -> list[MetricRecord]:
        records_payload = payload.get("metrics", payload) if isinstance(payload, dict) else payload
        if not isinstance(records_payload, list):
            logger.warning("LLM output was not a JSON list for %s.", chunk.chunk_id)
            return []

        metrics: list[MetricRecord] = []
        for item in records_payload:
            if not isinstance(item, dict):
                continue

            candidate = {
                **item,
                "source_file": chunk.source_file,
                "source_type": chunk.source_type,
                "source_location": chunk.source_location,
                "extraction_method": extraction_method,
                "raw_text": item.get("raw_text") or chunk.text,
            }

            try:
                metrics.append(MetricRecord.model_validate(candidate))
            except ValidationError as exc:
                logger.warning("Skipping invalid LLM metric for %s: %s", chunk.chunk_id, exc)

        return metrics

    def _cache_path(self, chunk: SourceChunk) -> Path:
        cache_key = hashlib.sha256(
            f"{PROMPT_VERSION}\n{chunk.text}".encode("utf-8")
        ).hexdigest()
        return self.cache_dir / f"{cache_key}.json"

    def _read_cache(self, cache_path: Path) -> list[MetricRecord] | None:
        if not cache_path.exists():
            return None

        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            return [MetricRecord.model_validate(item) for item in payload]
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            logger.warning("Ignoring invalid LLM cache file %s: %s", cache_path, exc)
            return None

    def _write_cache(self, cache_path: Path, metrics: list[MetricRecord]) -> None:
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(
                    [metric.model_dump() for metric in metrics],
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning("Could not write LLM cache file %s: %s", cache_path, exc)
