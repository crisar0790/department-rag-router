
"""Retrieve relevant documents from department vector indexes."""

from langfuse import get_client
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
    """Retrieve relevant chunks and trace the vector search."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if k < 1:
        raise ValueError("Retrieval count must be at least 1.")

    langfuse = get_client()

    with langfuse.start_as_current_observation(
        name="department-retrieval",
        as_type="retriever",
        input={
            "question": question,
            "department": department,
            "k": k,
        },
    ) as observation:
        store = get_department_store(department)

        if store._collection.count() == 0:
            raise ValueError(
                f"No indexed documents found for department: {department}"
            )

        retriever = store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

        documents = retriever.invoke(question)

        observation.update(
            output=[
                {
                    "document_id": document.metadata.get("document_id"),
                    "source": document.metadata.get("source"),
                }
                for document in documents
            ],
            metadata={
                "department": department,
                "retrieved_count": len(documents),
                "collection": f"{department}_documents",
            },
        )

        return documents
