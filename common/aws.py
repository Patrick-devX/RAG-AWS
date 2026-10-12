"""One place to create AWS clients.

    from common.aws import client
    s3 = client("s3")
    bedrock = client("bedrock-runtime")
"""

from functools import cache

import boto3
from botocore.config import Config

from common.config import settings

# How every client behaves on the network
RETRY_CONFIG = Config(
    retries={"max_attempts": 8, "mode": "adaptive"},  # retry up to 8 times, slowing down when throttled
    connect_timeout=10,                               # seconds to wait for a connection
    read_timeout=120,                                 # seconds to wait for an answer (LLM answers can be slow)
)


@cache
def session() -> boto3.Session:
    """The login: your profile (or none, when running on AWS itself) and your region."""
    return boto3.Session(profile_name=settings.aws_profile, region_name=settings.region)


@cache
def client(service: str):
    """A ready-to-use client for one AWS service, e.g. client("s3")."""
    return session().client(service, config=RETRY_CONFIG)