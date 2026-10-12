
"""Unit tests for the Technology RAG agent."""

from unittest.mock import MagicMock, patch

from src.agents.tech_agent import (
    TECH_SPECIALIZATION,
    answer_tech_question,
)


@patch("src.agents.tech_agent.answer_department_question")
def test_tech_agent_uses_correct_department(mock_answer):
    """Route Technology questions to the correct knowledge base."""
    mock_answer.return_value = {
        "department": "technology",
        "answer": "Contact the internal IT support team.",
        "sources": [],
    }

    result = answer_tech_question(
        "How do I reset my corporate password?"
    )

    mock_answer.assert_called_once_with(
        question="How do I reset my corporate password?",
        department="technology",
        k=3,
        callbacks=None,
        specialization=TECH_SPECIALIZATION,
    )

    assert result["department"] == "technology"


@patch("src.agents.tech_agent.answer_department_question")
def test_tech_agent_forwards_retrieval_settings(mock_answer):
    """Forward retrieval count and observability callbacks."""
    callback = MagicMock()

    answer_tech_question(
        question="How do I request software installation?",
        k=5,
        callbacks=[callback],
    )

    mock_answer.assert_called_once_with(
        question="How do I request software installation?",
        department="technology",
        k=5,
        callbacks=[callback],
        specialization=TECH_SPECIALIZATION,
    )


def test_tech_specialization_defines_responsibilities():
    """Define technical responsibilities and security restrictions."""
    assert "Technology" in TECH_SPECIALIZATION
    assert "Software installation" in TECH_SPECIALIZATION
    assert "Cybersecurity" in TECH_SPECIALIZATION
    assert "Do not suggest bypassing" in TECH_SPECIALIZATION
    assert "Do not invent" in TECH_SPECIALIZATION
