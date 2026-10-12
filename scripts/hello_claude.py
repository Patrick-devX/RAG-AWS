

from common.aws import client
from common.config import settings

# "bedrock-runtime" is the API for calling models 
bedrock_runtime = client("bedrock-runtime")

response = bedrock_runtime.converse(
    modelId=settings.generation_model_id,
    # The system prompt: standing instructions that shape every answer
    system=[{"text": "You are a concise AWS architect. Answer in at most three sentences."}],
    # The conversation so far: here just one message from the user
    messages=[
        {"role": "user", "content": [{"text": "What is retrieval-augmented generation (RAG)?"}]},
    ],
    # maxTokens = upper limit for the answer length; temperature 0 = most predictable answer
    inferenceConfig={"maxTokens": 300, "temperature": 0},
)

answer = response["output"]["message"]["content"][0]["text"]
usage = response["usage"]

print(answer)
print(f"\nmodel:       {settings.generation_model_id}")
print(f"tokens:      {usage['inputTokens']} in, {usage['outputTokens']} out")
print(f"stop reason: {response['stopReason']}")