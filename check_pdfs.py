from pathlib import Path

from pypdf import PdfReader


base_dir = Path(__file__).resolve().parent
source_dir = base_dir / "sources"
pdf_files = sorted(source_dir.glob("*.pdf"))

if not pdf_files:
    raise SystemExit(f"No PDFs found in: {source_dir}")

print(f"Found {len(pdf_files)} PDF files.\n")

total_pages = 0
total_characters = 0

for pdf_file in pdf_files:
    try:
        reader = PdfReader(pdf_file)

        readable_pages = 0
        character_count = 0

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                readable_pages += 1
                character_count += len(text)

        total_pages += len(reader.pages)
        total_characters += character_count

        print(pdf_file.name)
        print(f"  Total pages:    {len(reader.pages)}")
        print(f"  Readable pages: {readable_pages}")
        print(f"  Characters:     {character_count:,}")

        if readable_pages == 0:
            print("  WARNING: No text was extracted.")

        print()

    except Exception as error:
        print(pdf_file.name)
        print(f"  ERROR: {error}\n")

print("Corpus totals")
print(f"  PDFs:       {len(pdf_files)}")
print(f"  Pages:      {total_pages}")
print(f"  Characters: {total_characters:,}")