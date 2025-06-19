import inspect
from langchain_core.language_models.chat_models import BaseChatModel


def list_implementations() -> list:
    return [
        name for name, func in globals().items()
        if inspect.isfunction(func) and name != "list_implementations"
    ]

def gpt35_turbo(temperature: float = 0.7, max_tokens: int = 1500) -> BaseChatModel:
    """
    class: OpenAIChat
    Initializes a chat model using OpenAI's API with specified parameters.
    """
    from langchain_openai import OpenAIChat
    return OpenAIChat(
        model_name="gpt-3.5-turbo",
        temperature=temperature,
        max_tokens=max_tokens
    )