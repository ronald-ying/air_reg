import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
INSTRUCTIONS_PATH = BASE_DIR / "instructions.txt"

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
page_vector_store_id = os.getenv("OPENAI_PAGE_VECTOR_STORE_ID")

if not api_key:
    raise SystemExit(
        "OPENAI_API_KEY was not found. Check your local .env file."
    )

if not page_vector_store_id:
    raise SystemExit(
        "OPENAI_PAGE_VECTOR_STORE_ID was not found. "
        "Check your local .env file."
    )

if not INSTRUCTIONS_PATH.exists():
    raise SystemExit("instructions.txt was not found.")

instructions = INSTRUCTIONS_PATH.read_text(
    encoding="utf-8"
).strip()

retrieval_instructions = f"""
{instructions}

Additional source-grounding rules:

1. Use only information retrieved from the FHWA MSAT page-level vector store.
2. Each retrieved text file represents one electronic PDF page.
3. Each page begins with the original PDF filename and electronic page number.
4. Cite substantive conclusions as:
   [original PDF filename, electronic PDF page number]
5. Do not use outside knowledge to fill gaps.
6. Distinguish FHWA guidance from appendix prototype language.
7. State clearly when the retrieved material does not support an answer.
8. Do not invent project-specific traffic, emissions, modeling, or design data.
"""

question = input(
    "Ask a question about the FHWA MSAT documents: "
).strip()

if not question:
    raise SystemExit("No question entered.")

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    instructions=retrieval_instructions,
    input=question,
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [page_vector_store_id],
            "max_num_results": 12,
        }
    ],
    include=["file_search_call.results"],
)

print("\nOmni Consultant:")
print(response.output_text)

cited_page_files = []

for output_item in response.output:
    if output_item.type != "message":
        continue

    for content_item in output_item.content:
        if content_item.type != "output_text":
            continue

        for annotation in content_item.annotations:
            if annotation.type != "file_citation":
                continue

            if annotation.filename not in cited_page_files:
                cited_page_files.append(annotation.filename)

if cited_page_files:
    print("\nRetrieved source pages:")

    page_pattern = re.compile(
        r"^(?P<document>.+)__page_(?P<page>\d+)\.txt$"
    )

    for filename in cited_page_files:
        match = page_pattern.match(filename)

        if match:
            document_name = f"{match.group('document')}.pdf"
            page_number = int(match.group("page"))

            print(
                f"- {document_name}, "
                f"electronic PDF page {page_number}"
            )
        else:
            print(f"- {filename}")
else:
    print(
        "\nWARNING: The response did not return any file citations."
    )