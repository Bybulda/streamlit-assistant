import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from backend.ai.llm.base_model import BaseLLM

load_dotenv()


class GPTClient(BaseLLM):
    def __init__(self, request, chunks):
        super().__init__(request, chunks)
        self.client = AsyncOpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

    def build_prompt(self):
        context = "\n\n".join([chunk["document"] for chunk in self.chunks])
        return [
            {"role": "system",
             "content": "Ты умный помощник. Отвечай строго на основе контекста. Если ответа нет в контексте, так и скажи."},
            {"role": "system", "content": f"Контекст:\n{context}"},
            {"role": "user", "content": self.request.message}
        ]

    async def send(self) -> str:
        messages = self.build_prompt()
        response = await self.client.chat.completions.create(
            model=self.request.model,
            messages=messages,
            temperature=0.7,
            timeout=120.0
        )
        return response.choices[0].message.content.strip()
