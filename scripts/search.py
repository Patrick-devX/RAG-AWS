"""Step 16 - ask a question, see which chunks come back.

Run:  uv run python -m scripts.search "your question here"
"""

import sys

from rag.retrieval import search

question = " ".join(sys.argv[1:]) or "What are the design principles?"
print(f"Question: {question}\n")

for rank, hit in enumerate(search(question, top_k=5), start=1):
    print(f"#{rank}  score {hit.score:.3f}  |  {hit.doc_id}  |  pages {hit.page_start}-{hit.page_end}")
    print(f"    section: {hit.section}")
    print(f"    {hit.text[:300].replace(chr(10), ' ')}...\n")