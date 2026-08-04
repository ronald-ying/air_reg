# Omni Consultant

An AI assistant that progressively replaces professional consulting workflows.

Current milestone:
- Learn OpenAI API
- Build one working feature at a time

## Current capability

Omni Consultant answers questions from the indexed FHWA MSAT guidance corpus using page-level semantic retrieval.

It currently:

- searches seven FHWA MSAT documents;
- retrieves relevant electronic PDF pages;
- provides filename and page-level citations;
- distinguishes FHWA guidance from prototype appendix language;
- identifies unsupported project-specific questions.

## Run

Activate the virtual environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1