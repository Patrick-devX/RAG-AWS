"""Step 17 - ask a question, get an answer with citations.

Run:  uv run python -m scripts.ask "your question here"
"""

import re
import sys

from rag.generation import answer

question = " ".join(sys.argv[1:]) or "What are the design principles?"
result = answer(question)

print(f"Question: {question}\n")
print(result.text)

# Which source numbers did Claude actually cite? e.g. "[1][3]" or "[2, 4]" -> {1, 2, 3, 4}
cited = {int(n) for group in re.findall(r"\[([\d,\s]+)\]", result.text) for n in group.split(",") if n.strip()}

print("\nSources:")
for number, hit in enumerate(result.sources, start=1):
    marker = "cited" if number in cited else "     "
    print(f"  [{number}] {marker}  {hit.doc_id} | pages {hit.page_start}-{hit.page_end} | {hit.section}")

print(f"\ntokens: {result.input_tokens} in, {result.output_tokens} out")