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
readable_pages = 0

for pdf_file in pdf_files:
    reader = PdfReader(pdf_file)

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or "").strip()

        if not page_text:
            continue

        source_sections.append(
            f"""
=== SOURCE: {pdf_file.name} | PDF PAGE {page_number} ===
{page_text}
""".strip()
        )

        readable_pages += 1

source_text = "\n\n".join(source_sections)

if not source_text:
    raise SystemExit("No readable text was extracted from the PDFs.")

print(
    f"Loaded {len(pdf_files)} PDFs and "
    f"{readable_pages} readable pages."
)

question = input(
    "\nAsk a question about the FHWA MSAT documents: "
).strip()

if not question:
    raise SystemExit("No question entered.")

prompt = f"""
Answer the question using only the FHWA source documents provided below.

Requirements:
1. Cite each substantive conclusion as [filename, PDF page number].
2. Do not invent FHWA requirements, thresholds, project facts, or results.
3. State clearly when the documents do not support a conclusion.
4. Distinguish FHWA guidance from sample appendix language.
5. Distinguish source statements from professional inference.
6. Identify any material differences among the documents.
7. Use the electronic PDF page numbers shown in the source markers.

FHWA SOURCE DOCUMENTS
=====================
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