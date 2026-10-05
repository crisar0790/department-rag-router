"""Configure Langfuse tracing for the application."""

from langfuse import Langfuse

from src.config import (
    LANGFUSE_HOST,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
)


def create_langfuse_client() -> Langfuse:
    """Validate tracing credentials and initialize the shared client."""
    if not LANGFUSE_PUBLIC_KEY or LANGFUSE_PUBLIC_KEY == "pk-lf-xxx":
        raise ValueError("Set a valid LANGFUSE_PUBLIC_KEY in your .env file.")

    if not LANGFUSE_SECRET_KEY or LANGFUSE_SECRET_KEY == "sk-lf-xxx":
        raise ValueError("Set a valid LANGFUSE_SECRET_KEY in your .env file.")

    if not LANGFUSE_HOST:
        raise ValueError("Set LANGFUSE_HOST in your .env file.")

    return Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        base_url=LANGFUSE_HOST,
    )