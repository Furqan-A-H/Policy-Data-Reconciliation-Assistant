from abc import ABC, abstractmethod
import logging
from pathlib import Path

from app.extraction.schema import SourceChunk

logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """Base interface for source-specific document loaders."""

    source_type: str

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Return True when this loader can read the supplied file."""

    @abstractmethod
    def load(self, file_path: Path) -> list[SourceChunk]:
        """Load a file into provenance-aware source chunks."""


def available_loaders() -> list[BaseLoader]:
    from app.ingestion.docx_loader import DocxLoader
    from app.ingestion.excel_loader import ExcelLoader
    from app.ingestion.pptx_loader import PptxLoader

    return [DocxLoader(), PptxLoader(), ExcelLoader()]


def load_files_from_directory(directory: Path) -> list[SourceChunk]:
    """Load supported files from a directory without stopping on bad files."""
    if not directory.exists():
        logger.error("Input directory does not exist: %s", directory)
        return []

    if not directory.is_dir():
        logger.error("Input path is not a directory: %s", directory)
        return []

    chunks: list[SourceChunk] = []
    loaders = available_loaders()

    for file_path in sorted(path for path in directory.rglob("*") if path.is_file()):
        loader = next((candidate for candidate in loaders if candidate.supports(file_path)), None)
        if loader is None:
            continue

        try:
            chunks.extend(loader.load(file_path))
        except Exception:
            logger.exception("Failed to load %s", file_path)

    return chunks
