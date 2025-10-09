import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_AI_API_KEY")

def get_client(provider="openai"):
    if provider == "deepseek":
        return OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
    else:
        return OpenAI(api_key=OPENAI_API_KEY)


def ask_model(messages, model="gpt-4o-mini", provider="openai"):
    client = get_client(provider)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return resp.choices[0].message.content
