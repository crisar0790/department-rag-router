
"""Retrieve relevant documents from department vector indexes."""

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import CHROMA_PERSIST_DIRECTORY
from src.models import create_embedding_model
from src.retrieval.chunking import DEPARTMENT_FOLDERS


def get_department_store(department: str) -> Chroma:
    """Open the persistent vector collection for a department."""
    if department not in DEPARTMENT_FOLDERS:
        raise ValueError(f"Unsupported department: {department}")

    if not CHROMA_PERSIST_DIRECTORY.is_dir():
        raise FileNotFoundError(
            "Vector indexes not found. Run the indexing command first."
        )

    return Chroma(
        collection_name=f"{department}_documents",
        embedding_function=create_embedding_model(),
        persist_directory=str(CHROMA_PERSIST_DIRECTORY),
    )


def retrieve_documents(
    question: str,
    department: str,
    k: int = 3,
) -> list[Document]:
    """Retrieve the most relevant chunks from one department."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if k < 1:
        raise ValueError("Retrieval count must be at least 1.")

    store = get_department_store(department)

    if store._collection.count() == 0:
        raise ValueError(
            f"No indexed documents found for department: {department}"
        )

    return store.similarity_search(question, k=k)
