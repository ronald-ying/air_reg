from openai import OpenAI

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
