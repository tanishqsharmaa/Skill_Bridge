from langchain_deepseek import ChatDeepSeek
from src.core.config import settings


def get_llm(temperature: float = 0.2) -> ChatDeepSeek:
    """Return a configured DeepSeek LLM instance.

    Args:
        temperature: Sampling temperature. Use 0.0–0.2 for structured output,
                     0.3–0.5 for quiz generation, 0.7–0.8 for creative content.
    """
    return ChatDeepSeek(
        model="deepseek-chat",
        temperature=temperature,
        api_key=settings.deepseek_api_key,
    )
