"""Create reusable reasoning models through the LangChain integration."""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import (
    MAX_OUTPUT_TOKENS,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
    OPENAI_MAX_RETRIES,
    OPENAI_REASONING_EFFORT,
    OPENAI_TIMEOUT,
    OPENAI_EMBEDDING_MODEL,
)


def create_chat_model() -> ChatOpenAI:
    """Validate configuration and create the application reasoning model."""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-key-here":
        raise ValueError("Set a valid OPENAI_API_KEY in your .env file.")

    if not OPENAI_CHAT_MODEL:
        raise ValueError("Set OPENAI_CHAT_MODEL in your .env file.")

    return ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        use_responses_api=True,
        reasoning_effort=OPENAI_REASONING_EFFORT,
        timeout=OPENAI_TIMEOUT,
        max_retries=OPENAI_MAX_RETRIES,
        max_tokens=MAX_OUTPUT_TOKENS,
    )


def create_embedding_model() -> OpenAIEmbeddings:
    """Validate configuration and create the document embedding model."""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-key-here":
        raise ValueError("Set a valid OPENAI_API_KEY in your .env file.")

    if not OPENAI_EMBEDDING_MODEL:
        raise ValueError("Set OPENAI_EMBEDDING_MODEL in your .env file.")

    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
        request_timeout=OPENAI_TIMEOUT,
        max_retries=OPENAI_MAX_RETRIES,
    )
