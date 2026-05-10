from pathlib import Path

from app.extraction.schema import SourceChunk
from app.ingestion.base import BaseLoader


class DocxLoader(BaseLoader):
    source_type = "docx"

    def load(self, file_path: Path) -> list[SourceChunk]:
        raise NotImplementedError("DOCX ingestion will be implemented in a later phase.")
