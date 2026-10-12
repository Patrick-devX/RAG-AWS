"""All project settings in one place.

Reads the DOCPILOT_* values from the .env file. Use it anywhere like this:

    from common.config import settings
    print(settings.region)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Where to read from: variables starting with DOCPILOT_, from the .env file
    model_config = SettingsConfigDict(env_prefix="DOCPILOT_", env_file=".env", extra="ignore")

    # AWS
    region: str = "eu-central-1"          # DOCPILOT_REGION
    aws_profile: str | None = None        # DOCPILOT_AWS_PROFILE (None = no profile, e.g. on AWS itself)

    # Models (no default: the program stops with a clear error if one is missing)
    generation_model_id: str              # DOCPILOT_GENERATION_MODEL_ID
    fast_model_id: str                    # DOCPILOT_FAST_MODEL_ID
    embedding_model_id: str               # DOCPILOT_EMBEDDING_MODEL_ID
    embedding_dimensions: int = 1024      # DOCPILOT_EMBEDDING_DIMENSIONS
    rerank_model_id: str                  # DOCPILOT_RERANK_MODEL_ID

    # Documents
    raw_bucket: str                       # DOCPILOT_RAW_BUCKET (no default: required)
    raw_prefix: str = ""                  # DOCPILOT_RAW_PREFIX ("" = whole bucket)

    # Vector store
    vector_bucket: str = "docpilot-vectors"   # DOCPILOT_VECTOR_BUCKET
    vector_index: str = "chunks-v1"           # DOCPILOT_VECTOR_INDEX


# Created once when the module is first imported; every other file reuses it
settings = Settings()