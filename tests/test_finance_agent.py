
"""Unit tests for the Finance RAG agent."""

from unittest.mock import MagicMock, patch

from src.agents.finance_agent import (
    FINANCE_SPECIALIZATION,
    answer_finance_question,
)


@patch("src.agents.finance_agent.answer_department_question")
def test_finance_agent_uses_correct_department(mock_answer):
    """Route Finance questions to the correct knowledge base."""
    mock_answer.return_value = {
        "department": "finance",
        "answer": "Submit the expense report through the finance portal.",
        "sources": [],
    }

    result = answer_finance_question(
        "How do I request an expense reimbursement?"
    )

    mock_answer.assert_called_once_with(
        question="How do I request an expense reimbursement?",
        department="finance",
        k=3,
        callbacks=None,
        specialization=FINANCE_SPECIALIZATION,
    )

    assert result["department"] == "finance"


@patch("src.agents.finance_agent.answer_department_question")
def test_finance_agent_forwards_retrieval_settings(mock_answer):
    """Forward retrieval count and observability callbacks."""
    callback = MagicMock()

    answer_finance_question(
        question="How do I submit an invoice?",
        k=5,
        callbacks=[callback],
    )

    mock_answer.assert_called_once_with(
        question="How do I submit an invoice?",
        department="finance",
        k=5,
        callbacks=[callback],
        specialization=FINANCE_SPECIALIZATION,
    )


def test_finance_specialization_defines_responsibilities():
    """Define financial responsibilities and grounding restrictions."""
    assert "Finance" in FINANCE_SPECIALIZATION
    assert "reimbursement" in FINANCE_SPECIALIZATION
    assert "Invoice submission" in FINANCE_SPECIALIZATION
    assert "Do not invent" in FINANCE_SPECIALIZATION
    assert "Do not assume" in FINANCE_SPECIALIZATION
