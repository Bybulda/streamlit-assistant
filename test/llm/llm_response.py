from llm_client import ask_model

response = ask_model(
    [
        {"role": "system", "content": "Ты полезный ассистент."},
        {"role": "user", "content": "Привет, расскажи анекдот."}
    ],
    model="gpt-4o-mini",
    provider="openai"
)
print(response)
