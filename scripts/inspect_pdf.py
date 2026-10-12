"""Step 12 - parse one PDF with ingestion.parse and look at the result.

Run:  uv run python -m scripts.inspect_pdf                 (first PDF in data/raw)
      uv run python -m scripts.inspect_pdf my-file.pdf     (a specific one)
"""

import sys
from pathlib import Path

import pymupdf4llm

from ingestion.parse import Page, find_repeated_lines, parse_pdf

RAW_DIR = Path("data/raw")
PARSED_DIR = Path("data/parsed")

pdf_path = RAW_DIR / sys.argv[1] if len(sys.argv) > 1 else sorted(RAW_DIR.glob("*.pdf"))[0]
print(f"Parsing {pdf_path} ...")

# Show what the cleaning removes (parse once without cleaning, just for this report)
raw = pymupdf4llm.to_markdown(str(pdf_path), page_chunks=True)
removed = find_repeated_lines([Page(n, c["text"]) for n, c in enumerate(raw, start=1)])
print(f"header/footer lines removed: {len(removed)}")
for line in sorted(removed)[:10]:
    print(f"   - {line[:90]}")

pages = parse_pdf(pdf_path)

PARSED_DIR.mkdir(parents=True, exist_ok=True)
out_path = PARSED_DIR / f"{pdf_path.stem}.md"
with out_path.open("w", encoding="utf-8") as out:
    for page in pages:
        out.write(f"\n\n<!-- page {page.number} -->\n\n{page.text}")

print(f"\npages:      {len(pages)}")
print(f"characters: {sum(len(p.text) for p in pages):,}")
print(f"saved to:   {out_path}")