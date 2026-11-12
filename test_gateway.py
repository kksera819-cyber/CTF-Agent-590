
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["LITELLM_TOKEN"],
    base_url=os.environ["DUKE_API_BASE"],
    timeout=30,
    max_retries=0
)

model = os.environ["DUKE_MODEL"]

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Gateway connected"
        }
    ],
    max_tokens=40
)

print("Model:", model)
print("Response:", response.choices[0].message.content)

if response.usage:
    print("Input tokens:", response.usage.prompt_tokens)
    print("Output tokens:", response.usage.completion_tokens)
