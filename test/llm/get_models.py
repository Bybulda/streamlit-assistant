import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

models = client.models.list()

print("📋 Доступные модели:")
for m in models.data:
    print("-", m.id)
