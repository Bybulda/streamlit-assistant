import os

from dotenv import load_dotenv
from openai import OpenAI
from backend.ai.llm.base_model import BaseLLM

load_dotenv()

class GPTClient(BaseLLM):
    def __init__(self, request, chunks):
        super().__init__(request, chunks)
        self.client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

    def build_prompt(self):
        context = "\n\n".join([chunk["document"] for chunk in self.chunks])
        return [
            {"role": "system", "content": "Ты умный помощник. Отвечай строго на основе контекста."},
            {"role": "system", "content": f"Контекст:\n{context}"},
            {"role": "user", "content": self.request.message}
        ]

    def send(self) -> str:
        messages = self.build_prompt()
        response = self.client.chat.completions.create(
            model=self.request.model,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
