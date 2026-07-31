import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "sources"
INSTRUCTIONS_PATH = BASE_DIR / "instructions.txt"

load_dotenv(BASE_DIR / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit(
        "OPENAI_API_KEY was not found. Check your local .env file."
    )

if not INSTRUCTIONS_PATH.exists():
    raise SystemExit("instructions.txt was not found.")

pdf_files = sorted(SOURCE_DIR.glob("*.pdf"))

if not pdf_files:
    raise SystemExit(f"No PDF files were found in {SOURCE_DIR}")

instructions = INSTRUCTIONS_PATH.read_text(
    encoding="utf-8"
).strip()

source_sections = []
extracted_page_count = 0

for pdf_file in pdf_files:
    reader = PdfReader(pdf_file)

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or "").strip()

        if not page_text:
            continue

        source_sections.append(
            f"""
=== SOURCE FILE: {pdf_file.name} | PDF PAGE: {page_number} ===
{page_text}
""".strip()
        )

        extracted_page_count += 1

source_text = "\n\n".join(source_sections)

if not source_text:
    raise SystemExit(
        "The PDFs were found, but no readable text was extracted."
    )

print(
    f"Loaded {len(pdf_files)} PDFs, "
    f"{extracted_page_count} readable pages, "
    f"and {len(source_text):,} characters."
)

question = input(
    "\nAsk a question about the FHWA MSAT documents: "
).strip()

if not question:
    raise SystemExit("No question entered.")

prompt = f"""
Answer the user's question using only the FHWA source documents below.

Source rules:
1. Cite every substantive conclusion as:
   [filename, PDF page number]
2. Do not invent FHWA requirements, thresholds, project facts, or conclusions.
3. Clearly state when the documents do not support an answer.
4. Distinguish FHWA guidance from appendix sample language.
5. Distinguish source statements from professional inference.
6. Identify conflicting or superseded language if documents differ.
7. PDF page numbers refer to the electronic PDF page, not necessarily
   the printed page number shown inside the document.

FHWA SOURCE CORPUS
==================
{source_text}

USER QUESTION
=============
{question}
"""

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    instructions=instructions,
    input=prompt,
)

print("\nOmni Consultant:")
print(response.output_text)