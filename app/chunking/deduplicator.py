import hashlib

from app.extraction.schema import SourceChunk


def deduplicate_chunks(chunks: list[SourceChunk]) -> list[SourceChunk]:
    seen_hashes: set[str] = set()
    unique_chunks: list[SourceChunk] = []

    for chunk in chunks:
        digest = hashlib.sha256(chunk.text.strip().lower().encode("utf-8")).hexdigest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        unique_chunks.append(chunk)

    return unique_chunks
