
"""Unit tests for department routing."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from src.router import RoutingDecision, route_question


@pytest.mark.parametrize("question", ["", " ", "\n\t"])
def test_route_question_rejects_empty_input(question):
    """Reject questions without meaningful content."""
    with pytest.raises(ValueError, match="Question cannot be empty"):
        route_question(question)


@pytest.mark.parametrize(
    "department",
    ["hr", "technology", "finance"],
)
def test_routing_decision_accepts_valid_departments(department):
    """Accept all supported department identifiers."""
    decision = RoutingDecision(
        department=department,
        reason="The department handles this request.",
    )

    assert decision.department == department
    assert decision.reason


def test_routing_decision_rejects_unknown_department():
    """Reject unsupported department identifiers."""
    with pytest.raises(ValidationError):
        RoutingDecision(
            department="marketing",
            reason="Unsupported department.",
        )


@pytest.mark.parametrize(
    "question, department",
    [
        ("How do I request annual leave?", "hr"),
        ("How do I reset my password?", "technology"),
        ("How do I submit an expense?", "finance"),
    ],
)
@patch("src.router.create_chat_model")
def test_route_question_returns_structured_decision(
    mock_create_model, question, department
):
    """Return the structured decision produced by the mocked model."""
    structured_model = MagicMock()
    structured_model.invoke.return_value = RoutingDecision(
        department=department,
        reason="Relevant department.",
    )

    mock_create_model.return_value.with_structured_output.return_value = (
        structured_model
    )

    result = route_question(question)

    assert result.department == department
    assert result.reason == "Relevant department."

    mock_create_model.return_value.with_structured_output.assert_called_once_with(
        RoutingDecision,
        method="json_schema",
    )

    args, kwargs = structured_model.invoke.call_args

    assert isinstance(args[0][0], SystemMessage)
    assert isinstance(args[0][1], HumanMessage)
    assert args[0][1].content == question
    assert kwargs["config"] == {"callbacks": []}


@patch("src.router.create_chat_model")
def test_route_question_forwards_callbacks(mock_create_model):
    """Forward tracing callbacks to the model invocation."""
    structured_model = MagicMock()
    structured_model.invoke.return_value = RoutingDecision(
        department="hr",
        reason="Employee policy.",
    )

    mock_create_model.return_value.with_structured_output.return_value = (
        structured_model
    )

    callback = MagicMock()

    route_question(
        "How do I request annual leave?",
        callbacks=[callback],
    )

    assert structured_model.invoke.call_args.kwargs["config"] == {
        "callbacks": [callback],
    }
