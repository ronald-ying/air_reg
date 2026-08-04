import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
INSTRUCTIONS_PATH = BASE_DIR / "instructions.txt"

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")

if not api_key:
    raise SystemExit(
        "OPENAI_API_KEY was not found. Check your local .env file."
    )

if not vector_store_id:
    raise SystemExit(
        "OPENAI_VECTOR_STORE_ID was not found. Check your local .env file."
    )

if not INSTRUCTIONS_PATH.exists():
    raise SystemExit("instructions.txt was not found.")

instructions = INSTRUCTIONS_PATH.read_text(
    encoding="utf-8"
).strip()

retrieval_instructions = f"""
{instructions}

Additional source-grounding rules:

1. Use only information retrieved from the FHWA MSAT vector store.
2. Do not rely on outside knowledge to fill gaps.
3. Cite the supporting FHWA filename for each substantive conclusion.
4. Distinguish FHWA guidance from appendix prototype language.
5. State clearly when the retrieved documents do not support an answer.
6. Do not invent project-specific traffic, emissions, modeling, or design data.
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
            "vector_store_ids": [vector_store_id],
            "max_num_results": 10,
        }
    ],
    include=["file_search_call.results"],
)

print("\nOmni Consultant:")
print(response.output_text)