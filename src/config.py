"""Load enviroment variables and centralize application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

# REsolve paths from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Existing enviroment variables take precedence over the .env file.
load_dotenv(PROJECT_ROOT / ".env", override=False)

def _read_integer(name: str, default: int, minimum: int) -> int:
    """Read an integer setting and validate its minimun value."""
    raw_value = os.getenv(name, str(default))

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")

    return value


def _read_reasoning_effort() -> str:
    """Read and validate the reasoning effort supported by GPT-5.5."""
    value = os.getenv("OPENAI_REASONING_EFFORT", "low").strip()
    allowed_values = {"none", "low", "medium", "high", "xhigh"}

    if value not in allowed_values:
        raise ValueError(
            "OPENAI_REASONING_EFFORT must be none, low, medium, high, or xhigh."
        )

    return value


# OpenAI credencials and model names.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "").strip()
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "").strip()
OPENAI_EVALUATOR_MODEL = os.getenv("OPENAI_EVALUATOR_MODEL", "").strip()

# Chat generation settings.
OPENAI_REASONING_EFFORT = _read_reasoning_effort()
OPENAI_TIMEOUT = _read_integer("OPENAI_TIMEOUT", 60, minimum=1)
OPENAI_MAX_RETRIES = _read_integer("OPENAI_MAX_RETRIES", 0, minimum=0)
MAX_OUTPUT_TOKENS = _read_integer("MAX_OUTPUT_TOKENS", 2048, minimum=1)

# Langfue credencials and endpoint.
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
LANGFUSE_HOST = os.getenv(
    "LANGFUSE_HOST",
    "https://cloud.langfuse.com",
).strip()

# Resolve relative database paths from the repository root.
_chroma_directory = Path(
    os.getenv("CHROMA_PERSIST_DIRECTORY", "storage/choma")
).expanduser()

CHROMA_PERSIST_DIRECTORY = (
    _chroma_directory
    if _chroma_directory.is_absolute()
    else PROJECT_ROOT / _chroma_directory
).resolve()
