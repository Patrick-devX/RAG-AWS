"""Step 15 - ingest every PDF in data/raw into the vector index.

Run:  uv run python -m scripts.ingest
"""

import time
from pathlib import Path

from common.aws import client
from common.config import settings
from ingestion.chunking import chunk_document
from ingestion.index import index_chunks
from ingestion.parse import parse_pdf

RAW_DIR = Path("data/raw")

pdfs = sorted(RAW_DIR.glob("*.pdf"))
print(f"Ingesting {len(pdfs)} PDF(s) into {settings.vector_bucket}/{settings.vector_index}\n")

total_chunks, started = 0, time.perf_counter()
for pdf in pdfs:
    t0 = time.perf_counter()
    chunks = chunk_document(pdf.stem, parse_pdf(pdf))
    index_chunks(chunks)
    total_chunks += len(chunks)
    print(f"  {pdf.stem:<45} {len(chunks):>5} chunks  {time.perf_counter() - t0:6.1f} s")

print(f"\n{total_chunks} chunks in {time.perf_counter() - started:.0f} s")

# Count what is really in the index (list_vectors returns up to 1000 keys per call)
s3vectors, count, token = client("s3vectors"), 0, None
while True:
    kwargs = {"nextToken": token} if token else {}
    page = s3vectors.list_vectors(
        vectorBucketName=settings.vector_bucket, indexName=settings.vector_index, maxResults=1000, **kwargs
    )
    count += len(page.get("vectors", []))
    token = page.get("nextToken")
    if not token:
        break
print(f"vectors in the index: {count}")