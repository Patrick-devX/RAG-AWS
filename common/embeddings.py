"""Turn text into vectors with the embedding model from .env.

    from common.embeddings import embed, embed_many
    vector = embed("some text")                 # one text  -> one vector
    vectors = embed_many(["a", "b", "c"])       # many texts -> vectors, same order
"""

import json
from concurrent.futures import ThreadPoolExecutor

from common.aws import client
from common.config import settings


def embed(text: str) -> list[float]:
    """One text -> one normalized vector (Titan Text Embeddings V2)."""
    body = {"inputText": text, "dimensions": settings.embedding_dimensions, "normalize": True}
    response = client("bedrock-runtime").invoke_model(modelId=settings.embedding_model_id, body=json.dumps(body))
    return json.loads(response["body"].read())["embedding"]


def embed_many(texts: list[str], workers: int = 8) -> list[list[float]]:
    """Embed many texts in parallel threads. The result keeps the order of the input."""
    client("bedrock-runtime")  # create the client once, before the threads start using it
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(embed, texts))