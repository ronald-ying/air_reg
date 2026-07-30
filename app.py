import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit(
        "OPENAI_API_KEY was not found. Check your local .env file."
    )

client = OpenAI()

question = input("Ask Omni Consultant a question: ").strip()

if not question:
    raise SystemExit("No question entered.")

response = client.responses.create(
    model="gpt-5.6-luna",
    input=question,
)

print("\nOmni Consultant:")
print(response.output_text)
