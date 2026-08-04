import os
import re
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "sources"

load_dotenv(BASE_DIR / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit(
        "OPENAI_API_KEY was not found. Check your local .env file."
    )

pdf_files = sorted(SOURCE_DIR.glob("*.pdf"))

if not pdf_files:
    raise SystemExit(f"No PDF files found in: {SOURCE_DIR}")

client = OpenAI()

vector_store = client.vector_stores.create(
    name="FHWA MSAT Guidance - Page Indexed"
)

print(f"Created vector store: {vector_store.id}")

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)
    page_files = []

    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)

        safe_name = re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            pdf_file.stem,
        )

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            page_text = (page.extract_text() or "").strip()

            if not page_text:
                continue

            page_file = temporary_path / (
                f"{safe_name}__page_{page_number:03d}.txt"
            )

            page_file.write_text(
                (
                    f"Source PDF: {pdf_file.name}\n"
                    f"Electronic PDF page: {page_number}\n\n"
                    f"{page_text}"
                ),
                encoding="utf-8",
            )

            page_files.append(page_file)

    if not page_files:
        raise SystemExit("No readable PDF pages were found.")

    print(f"Prepared {len(page_files)} page-level files.")
    print("Uploading and indexing pages...")

    with ExitStack() as stack:
        file_streams = [
            stack.enter_context(page_file.open("rb"))
            for page_file in page_files
        ]

        batch = (
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=file_streams,
            )
        )

print(f"\nBatch status: {batch.status}")
print(f"Completed: {batch.file_counts.completed}")
print(f"Failed: {batch.file_counts.failed}")
print(f"In progress: {batch.file_counts.in_progress}")
print(f"Total: {batch.file_counts.total}")

if batch.file_counts.failed:
    raise SystemExit("One or more page files failed to index.")

print("\nAdd this line to your local .env file:")
print(
    "OPENAI_PAGE_VECTOR_STORE_ID="
    f"{vector_store.id}"
)