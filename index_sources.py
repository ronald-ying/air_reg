import os
from contextlib import ExitStack
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


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

print(f"Preparing to index {len(pdf_files)} PDFs:")

for pdf_file in pdf_files:
    print(f"  - {pdf_file.name}")

client = OpenAI()

vector_store = client.vector_stores.create(
    name="FHWA MSAT Guidance"
)

print(f"\nCreated vector store: {vector_store.id}")
print("Uploading and indexing files...")

with ExitStack() as stack:
    file_streams = [
        stack.enter_context(pdf_file.open("rb"))
        for pdf_file in pdf_files
    ]

    batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams,
    )

print(f"\nBatch status: {batch.status}")
print(f"Completed: {batch.file_counts.completed}")
print(f"Failed: {batch.file_counts.failed}")
print(f"Total: {batch.file_counts.total}")

if batch.file_counts.failed:
    raise SystemExit(
        "One or more PDFs failed to index. Review the batch results."
    )

print("\nIndexing completed.")
print("Add this line to your local .env file:")
print(f"OPENAI_VECTOR_STORE_ID={vector_store.id}")