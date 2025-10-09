import os

from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
api_key = os.getenv("OPEN_ROUTER_API_KEY")


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="mistralai/mistral-nemo:free",
  messages=[
    {
      "role": "user",
      "content": "расскажи анекдот"
    }
  ]
)
print(completion.choices[0].message.content)