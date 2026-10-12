
"""Unit tests for the Human Resources RAG agent."""

from unittest.mock import MagicMock, patch

from src.agents.hr_agent import (
    HR_SPECIALIZATION,
    answer_hr_question,
)


@patch("src.agents.hr_agent.answer_department_question")
def test_hr_agent_uses_correct_department(mock_answer):
    """Route HR questions to the Human Resources collection."""
    mock_answer.return_value = {
        "department": "hr",
        "answer": "Submit the request through the employee portal.",
        "sources": [],
    }

    result = answer_hr_question("How do I request annual leave?")

    mock_answer.assert_called_once_with(
        question="How do I request annual leave?",
        department="hr",
        k=3,
        callbacks=None,
        specialization=HR_SPECIALIZATION,
    )

    assert result["department"] == "hr"


@patch("src.agents.hr_agent.answer_department_question")
def test_hr_agent_forwards_retrieval_settings(mock_answer):
    """Forward retrieval count and observability callbacks."""
    callback = MagicMock()

    answer_hr_question(
        question="What benefits are available?",
        k=5,
        callbacks=[callback],
    )

    mock_answer.assert_called_once_with(
        question="What benefits are available?",
        department="hr",
        k=5,
        callbacks=[callback],
        specialization=HR_SPECIALIZATION,
    )


def test_hr_specialization_defines_responsibilities():
    """Provide explicit HR responsibilities and grounding rules."""
    assert "Human Resources" in HR_SPECIALIZATION
    assert "onboarding" in HR_SPECIALIZATION
    assert "Annual leave" in HR_SPECIALIZATION
    assert "Do not invent" in HR_SPECIALIZATION
