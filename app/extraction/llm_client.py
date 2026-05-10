from app.config import settings


class LLMClient:
    """Thin boundary for future structured extraction calls."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.openai_model

    def extract_metrics(self, text: str) -> list[dict]:
        raise NotImplementedError("LLM extraction will be implemented in a later phase.")
