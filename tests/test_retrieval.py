
"""Unit tests for department document retrieval."""

from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from src.retrieval.retriever import (
    get_department_store,
    retrieve_documents,
)


@pytest.fixture
def sample_documents():
    """Create sample documents returned by vector search."""
    return [
        Document(
            page_content="Annual leave requests use the employee portal.",
            metadata={
                "department": "hr",
                "document_id": "HR-001",
                "source": "data/hr_docs/vacation_policy.md",
            },
        ),
        Document(
            page_content="Leave requests require advance notice.",
            metadata={
                "department": "hr",
                "document_id": "HR-002",
                "source": "data/hr_docs/leave_policy.md",
            },
        ),
    ]


@pytest.fixture
def mocked_retrieval(sample_documents):
    """Mock vector storage and Langfuse tracing."""
    with (
        patch(
            "src.retrieval.retriever.get_department_store"
        ) as mock_get_store,
        patch(
            "src.retrieval.retriever.get_client"
        ) as mock_get_client,
    ):
        store = mock_get_store.return_value
        store._collection.count.return_value = 53
        store.as_retriever.return_value.invoke.return_value = sample_documents

        client = mock_get_client.return_value
        observation = MagicMock()
        client.start_as_current_observation.return_value = (
            nullcontext(observation)
        )

        yield {
            "store": store,
            "client": client,
            "observation": observation,
            "get_store": mock_get_store,
        }


@pytest.mark.parametrize(
    "department",
    ["hr", "technology", "finance"],
)
@patch("src.retrieval.retriever.Chroma")
@patch("src.retrieval.retriever.create_embedding_model")
@patch("src.retrieval.retriever.CHROMA_PERSIST_DIRECTORY")
def test_get_department_store_uses_correct_collection(
    mock_directory, mock_embeddings, mock_chroma, department
):
    """Open the collection associated with the selected department."""
    mock_directory.is_dir.return_value = True
    mock_directory.__str__.return_value = "/tmp/test-chroma"

    result = get_department_store(department)

    mock_chroma.assert_called_once_with(
        collection_name=f"{department}_documents",
        embedding_function=mock_embeddings.return_value,
        persist_directory="/tmp/test-chroma",
    )
    assert result is mock_chroma.return_value


@pytest.mark.parametrize(
    "department",
    ["marketing", "sales", "", "unknown"],
)
def test_get_department_store_rejects_unknown_departments(department):
    """Reject departments outside the supported domain list."""
    with pytest.raises(ValueError, match="Unsupported department"):
        get_department_store(department)


@patch("src.retrieval.retriever.CHROMA_PERSIST_DIRECTORY")
def test_get_department_store_requires_existing_index(mock_directory):
    """Reject retrieval when the vector index directory is missing."""
    mock_directory.is_dir.return_value = False

    with pytest.raises(FileNotFoundError, match="Vector indexes not found"):
        get_department_store("hr")


@pytest.mark.parametrize("question", ["", " ", "\n\t"])
def test_retrieve_documents_rejects_empty_questions(question):
    """Reject empty questions before creating a trace."""
    with patch("src.retrieval.retriever.get_client") as mock_client:
        with pytest.raises(ValueError, match="Question cannot be empty"):
            retrieve_documents(question, "hr")

        mock_client.assert_not_called()


@pytest.mark.parametrize("k", [0, -1, -5])
def test_retrieve_documents_rejects_invalid_k(k):
    """Require a positive number of retrieved chunks."""
    with patch("src.retrieval.retriever.get_client") as mock_client:
        with pytest.raises(ValueError, match="Retrieval count must be at least 1"):
            retrieve_documents("How do I request leave?", "hr", k=k)

        mock_client.assert_not_called()


def test_retrieve_documents_returns_matching_chunks(mocked_retrieval):
    """Return documents from the selected department store."""
    result = retrieve_documents(
        "How do I request leave?",
        "hr",
        k=2,
    )

    assert len(result) == 2
    assert result[0].metadata["document_id"] == "HR-001"
    assert result[1].metadata["document_id"] == "HR-002"

    mocked_retrieval["get_store"].assert_called_once_with("hr")
    mocked_retrieval["store"].as_retriever.assert_called_once_with(
        search_type="similarity",
        search_kwargs={"k": 2},
    )

    mocked_retrieval[
        "store"
    ].as_retriever.return_value.invoke.assert_called_once_with(
        "How do I request leave?"
    )


def test_retrieve_documents_rejects_empty_collection(mocked_retrieval):
    """Raise an error when the selected collection has no documents."""
    mocked_retrieval["store"]._collection.count.return_value = 0

    with pytest.raises(ValueError, match="No indexed documents found"):
        retrieve_documents("How do I request leave?", "hr")

    mocked_retrieval["store"].as_retriever.assert_not_called()


def test_retrieval_creates_langfuse_observation(mocked_retrieval):
    """Trace the department, question, and retrieval count."""
    retrieve_documents("How do I request leave?", "hr", k=3)

    mocked_retrieval[
        "client"
    ].start_as_current_observation.assert_called_once_with(
        name="department-retrieval",
        as_type="retriever",
        input={
            "question": "How do I request leave?",
            "department": "hr",
            "k": 3,
        },
    )


def test_retrieval_records_sources_and_metadata(mocked_retrieval):
    """Record retrieved sources and collection metadata in Langfuse."""
    retrieve_documents("How do I request leave?", "hr", k=2)

    mocked_retrieval["observation"].update.assert_called_once_with(
        output=[
            {
                "document_id": "HR-001",
                "source": "data/hr_docs/vacation_policy.md",
            },
            {
                "document_id": "HR-002",
                "source": "data/hr_docs/leave_policy.md",
            },
        ],
        metadata={
            "department": "hr",
            "retrieved_count": 2,
            "collection": "hr_documents",
        },
    )
