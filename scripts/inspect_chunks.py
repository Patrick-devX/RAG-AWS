"""chunk one PDF and look at the result.

Run:  uv run python -m scripts.inspect_chunks                 (first PDF in data/raw)
      uv run python -m scripts.inspect_chunks my-file.pdf     (a specific one)
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

from ingestion.chunking import chunk_document
from ingestion.parse import parse_pdf

RAW_DIR = Path("data/raw")
CHUNKS_DIR = Path("data/chunks")

pdf_path = RAW_DIR / sys.argv[1] if len(sys.argv) > 1 else sorted(RAW_DIR.glob("*.pdf"))[0]
doc_id = pdf_path.stem  # the file name without .pdf identifies the document

chunks = chunk_document(doc_id, parse_pdf(pdf_path))

sizes = [len(c.text) for c in chunks]
print(f"document:        {doc_id}")
print(f"chunks:          {len(chunks)}")
print(f"size (chars):    min {min(sizes)}, average {sum(sizes) // len(sizes)}, max {max(sizes)}")
print(f"without section: {sum(1 for c in chunks if not c.section)}")
print(f"with a table:    {sum(1 for c in chunks if '|' in c.text.splitlines()[0])}")

# Show two examples: one from the start, one from the middle
for chunk in [chunks[1], chunks[len(chunks) // 2]]:
    print(f"\n--- {chunk.chunk_id} | {chunk.section} | pages {chunk.page_start}-{chunk.page_end}")
    print(chunk.text[:600])

# Save all chunks as JSON so you can browse them in VS Code
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
out_path = CHUNKS_DIR / f"{doc_id}.json"
out_path.write_text(json.dumps([asdict(c) for c in chunks], indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved to {out_path}")