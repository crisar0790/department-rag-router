"""Load enviroment variables and centralize application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

# REsolve paths from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Existing enviroment variables take precedence over the .env file.
load_dotenv(PROJECT_ROOT / ".env", override=False)

# OpenAI credencials and model names.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "").strip()
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "").strip()
OPENAI_EVALUATOR_MODEL = os.getenv("OPENAI_EVALUATOR_MODEL", "").strip()

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
