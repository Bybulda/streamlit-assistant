import os

import httpx
from dotenv import load_dotenv

from backend.ai.llm.base_model import BaseLLM

load_dotenv()

class MistralClient(BaseLLM):
    def __init__(self, request, chunks):
        super().__init__(request, chunks)
        self.MISTRAL_API_KEY = os.getenv('OPEN_ROUTER_API_KEY')
        self.CLIENT_URL = os.getenv('OPEN_ROUTER_UR')

    def build_prompt(self):
        context = "\n\n".join([chunk["document"] for chunk in self.chunks])
        return [
            {"role": "system", "content": "Ты помощник. Используй предоставленный контекст для ответа."},
            {"role": "system", "content": f"Контекст:\n{context}"},
            {"role": "user", "content": self.request.message}
        ]

    async def send(self) -> str:
        messages = self.build_prompt()
        headers = {"Authorization": f"Bearer {self.MISTRAL_API_KEY}"}
        data = {"model": "mistralai/mistral-nemo:free", "messages": messages}

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.CLIENT_URL, headers=headers, json=data)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()

