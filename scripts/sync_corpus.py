"""copy the PDFs from your S3 bucket into data/raw/ for local work.

Run:  uv run python -m scripts.sync_corpus
"""

from pathlib import Path

from common.aws import client
from common.config import settings

RAW_DIR = Path("data/raw")   # data/ is in .gitignore: PDFs never go to GitHub
s3 = client("s3")

RAW_DIR.mkdir(parents=True, exist_ok=True)
print(f"Source: s3://{settings.raw_bucket}/{settings.raw_prefix}\n")

found = 0
# S3 returns at most 1,000 objects per call; the paginator fetches all pages for us
for page in s3.get_paginator("list_objects_v2").paginate(
    Bucket=settings.raw_bucket, Prefix=settings.raw_prefix
):
    for obj in page.get("Contents", []):
        key, size = obj["Key"], obj["Size"]
        if not key.lower().endswith(".pdf"):
            continue
        found += 1
        target = RAW_DIR / Path(key).name

        # Skip files we already have in the same size: safe to run again and again
        if target.exists() and target.stat().st_size == size:
            print(f"  already there  {target.name}")
            continue
        s3.download_file(settings.raw_bucket, key, str(target))
        print(f"  downloaded     {target.name}  ({size // 1024} KB)")

print(f"\n{found} PDF(s) in the bucket, local copies in {RAW_DIR}/")