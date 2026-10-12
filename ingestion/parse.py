"""Turn a PDF into clean pages of Markdown.

    from ingestion.parse import parse_pdf
    pages = parse_pdf(Path("data/raw/my.pdf"))
    pages[0].number, pages[0].text
"""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pymupdf4llm


@dataclass
class Page:
    number: int  # 1-based, as shown in a PDF viewer
    text: str    # the page as Markdown


def find_repeated_lines(pages: list[Page], min_share: float = 0.5) -> set[str]:
    """Lines that appear on at least half of all pages: headers and footers."""
    if len(pages) < 4:  # too few pages to tell a header from real content
        return set()
    counts = Counter()
    for page in pages:
        # a set per page: a line counts once per page, however often it appears there
        counts.update({line.strip() for line in page.text.splitlines() if line.strip()})
    return {line for line, count in counts.items() if count >= min_share * len(pages)}


def clean(text: str, repeated: set[str]) -> str:
    """Drop header/footer lines and lines that are only a page number."""
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in repeated or stripped.isdigit():
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def parse_pdf(path: Path) -> list[Page]:
    """Read a PDF and return its pages as cleaned Markdown."""
    raw = pymupdf4llm.to_markdown(str(path), page_chunks=True)
    pages = [Page(number=n, text=chunk["text"]) for n, chunk in enumerate(raw, start=1)]
    repeated = find_repeated_lines(pages)
    return [Page(page.number, clean(page.text, repeated)) for page in pages]