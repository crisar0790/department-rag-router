
"""Build persistent vector indexes for department documents."""

import argparse
import hashlib

from langchain_chroma import Chroma

from src.config import CHROMA_PERSIST_DIRECTORY
from src.models import create_embedding_model
from src.retrieval.chunking import (
    DEPARTMENT_FOLDERS,
    load_department_chunks,
)


def _chunk_id(department: str, document_id: str, index: int) -> str:
    """Create a stable identifier for a document chunk."""
    value = f"{department}:{document_id}:{index}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def index_department(department: str, embeddings) -> int:
    """Rebuild a department's persistent vector collection."""
    chunks = load_department_chunks(department)
    collection_name = f"{department}_documents"

    store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PERSIST_DIRECTORY),
    )

    # Remove the previous index to avoid stale or duplicate chunks.
    existing_ids = store.get(include=[])["ids"]
    if existing_ids:
        store.delete(ids=existing_ids)

    document_counts = {}
    ids = []

    for chunk in chunks:
        document_id = chunk.metadata["document_id"]
        index = document_counts.get(document_id, 0)
        ids.append(_chunk_id(department, document_id, index))
        document_counts[document_id] = index + 1

    store.add_documents(documents=chunks, ids=ids)
    return store._collection.count()


def main() -> None:
    """Index one department or rebuild all department indexes."""
    parser = argparse.ArgumentParser(
        description="Build persistent department vector indexes."
    )
    parser.add_argument(
        "--department",
        choices=[*DEPARTMENT_FOLDERS, "all"],
        default="all",
    )
    args = parser.parse_args()

    CHROMA_PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)
    embeddings = create_embedding_model()

    departments = (
        DEPARTMENT_FOLDERS
        if args.department == "all"
        else [args.department]
    )

    for department in departments:
        count = index_department(department, embeddings)
        print(f"{department}: {count} indexed chunks")


if __name__ == "__main__":
    main()
