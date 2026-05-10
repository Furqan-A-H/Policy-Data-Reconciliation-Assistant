from typing import Any, Literal

from pydantic import BaseModel, Field

SourceType = Literal["docx", "xlsx", "pptx", "api"]
ExtractionMethod = Literal["rule_based", "llm", "mock_llm"]
Severity = Literal["low", "medium", "high"]


class SourceChunk(BaseModel):
    chunk_id: str
    source_file: str
    source_type: SourceType
    source_location: str
    content_type: str
    text: str
    metadata: dict[str, Any]


class MetricRecord(BaseModel):
    metric_name: str
    canonical_metric_name: str
    value: float | int | str
    unit: str
    year: int | None
    period: str | None
    geography: str | None
    source_file: str
    source_type: SourceType
    source_location: str
    extraction_method: ExtractionMethod
    confidence: float = Field(ge=0.0, le=1.0)
    caveat: str | None
    raw_text: str


class DiscrepancyRecord(BaseModel):
    canonical_metric_name: str
    year: int | None
    period: str | None
    geography: str | None
    unit: str
    severity: Severity
    likely_reason: str
    records: list[MetricRecord]
    explanation: str
    recommended_action: str


class TokenUsageReport(BaseModel):
    files_processed: int
    chunks_created: int
    chunks_sent_to_llm: int
    chunks_skipped: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_token_saving_percent: float
