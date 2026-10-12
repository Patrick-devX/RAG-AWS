"""create the vector bucket and the vector index (safe to run again).

Run:  uv run python -m scripts.setup_vector_store
"""

from common.aws import client
from common.config import settings

s3vectors = client("s3vectors")
bucket, index = settings.vector_bucket, settings.vector_index

# 1. The vector bucket: a container for vector indexes
try:
    s3vectors.create_vector_bucket(vectorBucketName=bucket)
    print(f"created vector bucket  {bucket}")
except s3vectors.exceptions.ConflictException:
    print(f"vector bucket exists   {bucket}")

# 2. The vector index: where the chunk vectors live
try:
    s3vectors.create_index(
        vectorBucketName=bucket,
        indexName=index,
        dataType="float32",
        dimension=settings.embedding_dimensions,  # must match the embedding model: 1024
        distanceMetric="cosine",                  # the same similarity we computed in Step 9
        # the chunk text is stored next to each vector but never used for filtering
        metadataConfiguration={"nonFilterableMetadataKeys": ["text"]},
    )
    print(f"created vector index   {index}")
except s3vectors.exceptions.ConflictException:
    print(f"vector index exists    {index}")

# 3. Read it back to prove it's there and configured as we expect
info = s3vectors.get_index(vectorBucketName=bucket, indexName=index)["index"]
print(f"\nindex:     {info['indexName']}")
print(f"dimension: {info['dimension']}")
print(f"distance:  {info['distanceMetric']}")