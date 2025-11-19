from abc import ABC, abstractmethod
from typing import List, Dict
from backend.app.models.chat import ChatRequest

class BaseLLM(ABC):
    def __init__(self, request: ChatRequest, chunks: List[Dict]):
        self.request = request
        self.chunks = chunks

    @abstractmethod
    def build_prompt(self) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    async def send(self) -> str:
        pass
