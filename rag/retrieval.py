"""Find the chunks that best match a question.

    from rag.retrieval import search
    for hit in search("How do I protect the root user?"):
        print(hit.score, hit.section, hit.text)
"""

from dataclasses import dataclass

from common.aws import client
from common.config import settings
from common.embeddings import embed


@dataclass
class Hit:
    score: float     # similarity 0..1, higher = better match
    chunk_id: str
    doc_id: str
    section: str
    page_start: int
    page_end: int
    text: str


def search(question: str, top_k: int = 5, doc_id: str | None = None) -> list[Hit]:
    """Embed the question and return the top_k most similar chunks (optionally from one document)."""
    request = {
        "vectorBucketName": settings.vector_bucket,
        "indexName": settings.vector_index,
        "queryVector": {"float32": embed(question)},  # same model as the chunks, or the vectors don't compare
        "topK": top_k,
        "returnMetadata": True,
        "returnDistance": True,
    }
    if doc_id:
        request["filter"] = {"doc_id": doc_id}  # only chunks whose metadata doc_id matches

    response = client("s3vectors").query_vectors(**request)

    hits = []
    for vector in response["vectors"]:
        meta = vector["metadata"]
        hits.append(
            Hit(
                score=1 - vector["distance"],  # cosine distance = 1 - similarity
                chunk_id=vector["key"],
                doc_id=meta["doc_id"],
                section=meta["section"],
                page_start=int(meta["page_start"]),
                page_end=int(meta["page_end"]),
                text=meta["text"],
            )
        )
    return hits