
"""Unit tests for specialized department agents."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.department_agent import (
    _extract_response_text,
    _format_context,
    answer_department_question,
)


@pytest.fixture
def sample_documents():
    """Create sample retrieved documents with source metadata."""
    return [
        Document(
            page_content="Employees receive 20 working days of annual leave.",
            metadata={
                "document_id": "HR-001",
                "source": "data/hr_docs/vacation_policy.md",
            },
        ),
        Document(
            page_content="Leave requests must be submitted through the portal.",
            metadata={
                "document_id": "HR-002",
                "source": "data/hr_docs/leave_policy.md",
            },
        ),
    ]


def test_format_context_includes_document_metadata(sample_documents):
    """Include document identifiers, sources, and content."""
    context = _format_context(sample_documents)

    assert "Document ID: HR-001" in context
    assert "Document ID: HR-002" in context
    assert "data/hr_docs/vacation_policy.md" in context
    assert "20 working days" in context
    assert "submitted through the portal" in context


def test_format_context_handles_empty_documents():
    """Return an empty context when no documents are retrieved."""
    assert _format_context([]) == ""


def test_extract_response_text_from_string():
    """Preserve plain-text model responses."""
    assert _extract_response_text("Example answer") == "Example answer"


def test_extract_response_text_from_blocks():
    """Combine supported text blocks into a single response."""
    content = [
        {"type": "text", "text": "First paragraph."},
        {"type": "reasoning", "summary": []},
        {"type": "text", "text": "Second paragraph."},
    ]

    assert _extract_response_text(content) == (
        "First paragraph.\nSecond paragraph."
    )


def test_extract_response_text_ignores_invalid_blocks():
    """Ignore blocks without valid text content."""
    content = [
        {"type": "text", "text": None},
        {"type": "image", "url": "example"},
        "unexpected block",
    ]

    assert _extract_response_text(content) == ""


@pytest.mark.parametrize("department", ["hr", "technology", "finance"])
@patch("src.agents.department_agent.create_chat_model")
@patch("src.agents.department_agent.retrieve_documents")
def test_agent_uses_selected_department(
    mock_retrieve, mock_create_model, department
):
    """Retrieve documents from the selected department."""
    mock_retrieve.return_value = []
    mock_create_model.return_value.invoke.return_value = MagicMock(
        content="No relevant information found."
    )

    result = answer_department_question(
        question="Example question",
        department=department,
        k=2,
    )

    mock_retrieve.assert_called_once_with(
        "Example question", department, k=2
    )
    assert result["department"] == department
    assert result["answer"] == "No relevant information found."


@patch("src.agents.department_agent.create_chat_model")
@patch("src.agents.department_agent.retrieve_documents")
def test_agent_returns_answer_and_sources(
    mock_retrieve, mock_create_model, sample_documents
):
    """Return the generated answer and retrieved document sources."""
    mock_retrieve.return_value = sample_documents
    mock_create_model.return_value.invoke.return_value = MagicMock(
        content="Employees receive 20 working days of annual leave."
    )

    result = answer_department_question(
        question="How many vacation days do employees receive?",
        department="hr",
    )

    assert result["question"] == (
        "How many vacation days do employees receive?"
    )
    assert "20 working days" in result["answer"]
    assert len(result["sources"]) == 2
    assert result["sources"][0]["document_id"] == "HR-001"
    assert result["sources"][1]["document_id"] == "HR-002"
    assert "Document ID: HR-001" in result["context"]


@patch("src.agents.department_agent.create_chat_model")
@patch("src.agents.department_agent.retrieve_documents")
def test_agent_builds_grounded_prompt(
    mock_retrieve, mock_create_model, sample_documents
):
    """Send the retrieved context and question to the model."""
    mock_retrieve.return_value = sample_documents
    mock_create_model.return_value.invoke.return_value = MagicMock(
        content="Example answer"
    )

    answer_department_question("How do I request leave?", "hr")

    args, kwargs = mock_create_model.return_value.invoke.call_args
    messages = args[0]

    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert "hr specialist" in messages[0].content
    assert "Document ID: HR-001" in messages[1].content
    assert "How do I request leave?" in messages[1].content
    assert kwargs["config"] == {"callbacks": []}


@patch("src.agents.department_agent.create_chat_model")
@patch("src.agents.department_agent.retrieve_documents")
def test_agent_forwards_langfuse_callbacks(
    mock_retrieve, mock_create_model
):
    """Forward observability callbacks to the language model."""
    mock_retrieve.return_value = []
    mock_create_model.return_value.invoke.return_value = MagicMock(
        content="Example answer"
    )

    callback = MagicMock()

    answer_department_question(
        question="How do I request leave?",
        department="hr",
        callbacks=[callback],
    )

    assert mock_create_model.return_value.invoke.call_args.kwargs[
        "config"
    ] == {"callbacks": [callback]}
