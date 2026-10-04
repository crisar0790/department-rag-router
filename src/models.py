"""Create reusable chat models through the LangChain integration."""

from langchain_openai import ChatOpenAI

from src.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL


def create_chat_model() -> ChatOpenAI:
    """Validate local configuration and create the application chat model."""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-key-here":
        raise ValueError("Set a valid OPENAI_API_KEY in your .env file.")

    if not OPENAI_CHAT_MODEL:
        raise ValueError("Set OPENAI_CHAT_MODEL in your .env file.")

    return ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
        timeout=30,
        max_retries=0,
    )