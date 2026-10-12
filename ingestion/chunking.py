"""Cut parsed pages into chunks along the document structure.

    from ingestion.chunking import chunk_document
    chunks = chunk_document("my-doc", pages)
"""

import re
from dataclasses import dataclass

from ingestion.parse import Page

HEADING = re.compile(r"^(#{1,6})\s+(.+)$")   # "## Title" -> level 2, "Title"
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")  # split point after . ! or ?


@dataclass
class Chunk:
    chunk_id: str    # "<doc_id>:00042" - unique and in document order
    doc_id: str      # which document
    section: str     # "Heading > Subheading > Sub-subheading"
    page_start: int  # first page the text comes from
    page_end: int    # last page the text comes from
    text: str        # what gets embedded and later shown to Claude


@dataclass
class Block:
    """One paragraph or one whole table, with where it came from."""
    section: str
    page: int
    text: str
    is_table: bool


def to_blocks(pages: list[Page]) -> list[Block]:
    """Walk all lines once: track the current headings, group lines into paragraphs and tables."""
    blocks: list[Block] = []
    headings: list[tuple[int, str]] = []  # the current heading path, e.g. [(1, "Security"), (2, "MFA")]
    lines: list[str] = []                 # lines of the block being collected
    block_page, block_is_table = 0, False

    def finish_block() -> None:
        text = "\n".join(lines).strip()
        if text:
            section = " > ".join(title for _, title in headings)
            blocks.append(Block(section, block_page, text, block_is_table))
        lines.clear()

    for page in pages:
        for line in page.text.splitlines():
            stripped = line.strip()

            heading = HEADING.match(stripped)
            if heading:
                finish_block()
                level, title = len(heading.group(1)), heading.group(2).strip("*# ")
                # a level-2 heading replaces any previous level-2+ headings
                headings = [(lvl, t) for lvl, t in headings if lvl < level] + [(level, title)]
                continue

            is_table = stripped.startswith("|")
            # a blank line, or a switch between table and normal text, ends the current block
            if not stripped or (lines and is_table != block_is_table):
                finish_block()
            if not stripped:
                continue
            if not lines:
                block_page, block_is_table = page.number, is_table
            lines.append(line)
        finish_block()  # blocks never run across a page break
    return blocks


def split_long_text(text: str, max_chars: int) -> list[str]:
    """Split a too-long paragraph at sentence ends into pieces of at most max_chars."""
    pieces, current = [], ""
    for sentence in SENTENCE_END.split(text):
        if current and len(current) + 1 + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def chunk_document(doc_id: str, pages: list[Page], max_chars: int = 2000) -> list[Chunk]:
    """Pack blocks into chunks of at most max_chars, never mixing sections, never splitting tables."""
    chunks: list[Chunk] = []
    parts: list[str] = []  # texts of the chunk being filled
    section, page_start, page_end = "", 0, 0

    def finish_chunk() -> None:
        text = "\n\n".join(parts).strip()
        if text:  # small chunks are kept: dropping them would lose information
            chunks.append(Chunk(f"{doc_id}:{len(chunks):05d}", doc_id, section, page_start, page_end, text))
        parts.clear()

    for block in to_blocks(pages):
        # tables stay whole; long paragraphs are split at sentence ends
        if block.is_table or len(block.text) <= max_chars:
            pieces = [block.text]
        else:
            pieces = split_long_text(block.text, max_chars)

        for piece in pieces:
            current_size = sum(len(p) + 2 for p in parts)
            if parts and (block.section != section or current_size + len(piece) > max_chars):
                finish_chunk()
            if not parts:
                section, page_start = block.section, block.page
            parts.append(piece)
            page_end = block.page
    finish_chunk()
    return chunks