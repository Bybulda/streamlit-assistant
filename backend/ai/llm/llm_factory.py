from backend.ai.llm.impl.chat_gpt_model import GPTClient
from backend.ai.llm.impl.mistral_model import MistralClient
from backend.ai.llm.base_model import BaseLLM

def get_llm_client(model_name: str, request, chunks) -> BaseLLM:
    model_name = model_name.lower()
    if "gpt" in model_name:
        return GPTClient(request, chunks)
    elif "mistral" in model_name:
        return MistralClient(request, chunks)
    else:
        raise ValueError(f"Unknown model: {model_name}")
