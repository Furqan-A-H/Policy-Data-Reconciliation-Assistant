from abc import ABC, abstractmethod
from pathlib import Path

from app.extraction.schema import SourceChunk


class BaseLoader(ABC):
    """Base interface for source-specific document loaders."""

    source_type: str

    @abstractmethod
    def load(self, file_path: Path) -> list[SourceChunk]:
        """Load a file into provenance-aware source chunks."""
