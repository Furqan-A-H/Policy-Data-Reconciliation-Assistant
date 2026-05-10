from pathlib import Path

from app.extraction.schema import SourceChunk
from app.ingestion.base import BaseLoader


class PptxLoader(BaseLoader):
    source_type = "pptx"

    def load(self, file_path: Path) -> list[SourceChunk]:
        raise NotImplementedError("PPTX ingestion will be implemented in a later phase.")
