from pathlib import Path

from app.extraction.schema import SourceChunk
from app.ingestion.base import BaseLoader


class ExcelLoader(BaseLoader):
    source_type = "xlsx"

    def load(self, file_path: Path) -> list[SourceChunk]:
        raise NotImplementedError("Excel ingestion will be implemented in a later phase.")
