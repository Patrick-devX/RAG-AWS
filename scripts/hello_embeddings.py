"""

Run:  uv run python -m scripts.hello_embeddings
"""

import json

from common.aws import client
from common.config import settings

bedrock_runtime = client("bedrock-runtime")


def embed(text: str) -> list[float]:
    """Turn one text into a vector of numbers with Titan Text Embeddings V2."""
    body = {
        "inputText": text,
        "dimensions": settings.embedding_dimensions,  # 1024 numbers per text
        "normalize": True,                            # length 1, so the dot product = cosine similarity
    }
    # Embedding models have no Converse API: we send raw JSON with invoke_model
    response = bedrock_runtime.invoke_model(modelId=settings.embedding_model_id, body=json.dumps(body))
    return json.loads(response["body"].read())["embedding"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """For normalized vectors this is just the dot product: sum of a[i] * b[i]."""
    return sum(x * y for x, y in zip(a, b))


question = "How do I keep my application running if a whole AWS region goes down?"
passages = [
    "Use a multi-Region disaster recovery strategy such as pilot light or warm standby.",
    "Right-size your EC2 instances to reduce your monthly bill.",
    "Back up your data regularly and test that restores actually work.",
    "Das Wetter in Berlin ist heute sonnig.",
]

question_vector = embed(question)
print(f"A vector has {len(question_vector)} numbers. The first 5: {[round(x, 4) for x in question_vector[:5]]}\n")

# Score every passage against the question, best first
scored = [(cosine_similarity(question_vector, embed(p)), p) for p in passages]
print(f"Question: {question}\n")
for score, passage in sorted(scored, reverse=True):
    print(f"  {score:.3f}  {passage}")