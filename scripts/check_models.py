# we ask Bedrock directly which Claude models your account can use from Frankfurt.

"""Step 7 - which Claude models can my account actually call?

Run:  uv run python -m scripts.check_models
"""

from common.aws import client
from common.config import settings

bedrock = client("bedrock")                  # management API: lists models
bedrock_runtime = client("bedrock-runtime")  # runtime API: calls models


def can_call(model_id: str) -> str:
    """Send a tiny request (max 1 output token, costs a fraction of a cent). Return 'OK' or the error."""
    try:
        bedrock_runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Hi"}]}],
            inferenceConfig={"maxTokens": 1},
        )
        return "OK"
    except Exception as error:  # we want to see every kind of failure here
        return f"NO  ({type(error).__name__})"


print(f"Region: {settings.region}\n")
print("Claude models (EU inference profiles) - listed and tested:")

for page in bedrock.get_paginator("list_inference_profiles").paginate():
    for profile in page["inferenceProfileSummaries"]:
        model_id = profile["inferenceProfileId"]
        if model_id.startswith("eu.anthropic."):
            print(f"   {model_id:<50} {can_call(model_id)}")

print("\nYour .env settings:")
for name in ["generation_model_id", "fast_model_id"]:
    model_id = getattr(settings, name)
    print(f"   {name:<20} {model_id:<50} {can_call(model_id)}")