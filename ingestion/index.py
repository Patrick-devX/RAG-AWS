"""Embed chunks and store them in the S3 Vectors index."""

from common.aws import client
from common.config import settings
from common.embeddings import embed_many
from ingestion.chunking import Chunk

BATCH_SIZE = 100  # chunks per request (S3 Vectors accepts up to 500)


def text_for_embedding(chunk: Chunk) -> str:
    """What gets embedded: the chunk text plus where it comes from.

    "Enable MFA for the root user" alone loses the information that it belongs to the
    Security document, section Identity. This small header puts that context back into the vector.
    """
    return f"Document: {chunk.doc_id}\nSection: {chunk.section}\n\n{chunk.text}"


def index_chunks(chunks: list[Chunk]) -> None:
    """Embed the chunks and write them to the vector index, batch by batch."""
    s3vectors = client("s3vectors")
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        vectors = embed_many([text_for_embedding(c) for c in batch])
        s3vectors.put_vectors(
            vectorBucketName=settings.vector_bucket,
            indexName=settings.vector_index,
            vectors=[
                {
                    "key": chunk.chunk_id,          # same key again = overwrite, so re-running is safe
                    "data": {"float32": vector},
                    "metadata": {                   # returned with every search hit
                        "doc_id": chunk.doc_id,
                        "section": chunk.section,
                        "page_start": chunk.page_start,
                        "page_end": chunk.page_end,
                        "text": chunk.text,
                    },
                }
                for chunk, vector in zip(batch, vectors)
            ],
        )