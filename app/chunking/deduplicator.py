import hashlib
import re

from app.extraction.schema import SourceChunk


def deduplicate_chunks(chunks: list[SourceChunk]) -> tuple[list[SourceChunk], int]:
    seen_hashes: set[str] = set()
    unique_chunks: list[SourceChunk] = []
    duplicate_count = 0

    for chunk in chunks:
        digest = hashlib.sha256(_normalise_text(chunk.text).encode("utf-8")).hexdigest()
        if digest in seen_hashes:
            duplicate_count += 1
            continue
        seen_hashes.add(digest)
        unique_chunks.append(chunk)

    return unique_chunks, duplicate_count


def _normalise_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())
