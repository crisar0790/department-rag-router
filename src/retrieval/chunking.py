"""Load departamental Markdown documents and split them into token chunks."""

import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SIZE_TOKENS,
    PROJECT_ROOT,
)


DEPARTMENT_FOLDERS = {
    "hr": "hr_docs",
    "technology": "tech_docs",
    "finance": "finance",
}

def _load_document(path: Path, department: str) -> Document:
    """Read a Markdown file and preserve its source identity."""
    text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Document is empty: {path.name}")

    match = re.search(r"^Document ID:\s*(\S+)\s*$", text, re.MULTILINE)
    if not match: 
        raise ValueError(f"Document ID is missing: {path.name}")

    return Document(
        page_content=text,
        metadata={
            "department": department,
            "document_id": match.group(1),
            "source": path.relative_to(PROJECT_ROOT).as_posix(),
        },
    )


def load_department_chunks(department: str) -> list[Document]:
    """Load and split one department without mixing document boundaries."""
    if department not in DEPARTMENT_FOLDERS:
        raise ValueError(f"Unsupported department: {department}")

    directory = PROJECT_ROOT / "data" / DEPARTMENT_FOLDERS[department]
    paths = sorted(directory.glob("*.md"))

    if not paths:
        raise ValueError(f"No Markdown documents found in {directory}")

    documents = [_load_document(path, department) for path in paths]
    document_ids = [doc.metadata["document_id"] for doc in documents]
    if len(document_ids) != len(set(document_ids)):
        raise ValueError(f"Duplicate document IDs in department: {department}")

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=CHUNK_SIZE_TOKENS,
        chunk_overlap=CHUNK_OVERLAP_TOKENS,
    )

    return splitter.split_documents(documents)