from langchain_openai.chat_models.base import ChatOpenAI


def gpt35_turbo(temperature: float = 0.7, max_tokens: int = 1500) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=temperature,
        max_tokens=max_tokens
    )