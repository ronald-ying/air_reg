from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6-luna",
    input="Explain Mobile Source Air Toxics in three concise sentences.",
)

print(response.output_text)
