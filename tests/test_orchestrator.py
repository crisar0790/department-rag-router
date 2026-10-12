
"""Unit tests for the multi-agent RAG orchestrator."""

from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest

from src.orchestrator import process_question
from src.router import RoutingDecision

from src.evaluator import JudgeResult


@pytest.fixture
def mocked_workflow():
    """Mock routing, department agent, and Langfuse dependencies."""
    with (
        patch("src.orchestrator.create_langfuse_client") as mock_client,
        patch("src.orchestrator.create_langfuse_handler") as mock_handler,
        patch("src.orchestrator.route_question") as mock_router,
        patch(
            "src.orchestrator.answer_department_question"
        ) as mock_agent,
    ):
        client = mock_client.return_value
        trace = MagicMock()
        client.start_as_current_observation.return_value = nullcontext(
            trace
        )
        client.get_current_trace_id.return_value = "test-trace-123"

        mock_router.return_value = RoutingDecision(
            department="hr",
            reason="Employee policy question.",
        )
        mock_agent.return_value = {
            "answer": "Submit the request through the employee portal.",
            "sources": [
                {
                    "document_id": "HR-001",
                    "source": "data/hr_docs/vacation_policy.md",
                }
            ],
            "context": "Annual leave policy context.",
        }

        yield {
            "client": client,
            "handler": mock_handler.return_value,
            "router": mock_router,
            "agent": mock_agent,
            "trace": trace,
        }


@pytest.mark.parametrize("question", ["", " ", "\n\t"])
def test_rejects_empty_questions(question):
    """Reject empty questions before initializing external services."""
    with patch(
        "src.orchestrator.create_langfuse_client"
    ) as mock_client:
        with pytest.raises(
            ValueError, match="Question cannot be empty"
        ):
            process_question(question)

        mock_client.assert_not_called()


@pytest.mark.parametrize("k", [0, -1, -5])
def test_rejects_invalid_retrieval_count(k):
    """Require a positive retrieval count."""
    with patch(
        "src.orchestrator.create_langfuse_client"
    ) as mock_client:
        with pytest.raises(
            ValueError, match="Retrieval count must be at least 1"
        ):
            process_question("How do I request leave?", k=k)

        mock_client.assert_not_called()


@pytest.mark.parametrize(
    "department",
    ["hr", "technology", "finance"],
)
def test_routes_to_correct_agent(mocked_workflow, department):
    """Send the question to the department selected by the router."""
    mocked_workflow["router"].return_value = RoutingDecision(
        department=department,
        reason="Department selected.",
    )

    result = process_question("Example question", k=2)

    mocked_workflow["agent"].assert_called_once_with(
        question="Example question",
        department=department,
        k=2,
        callbacks=[mocked_workflow["handler"]],
    )
    assert result["department"] == department


def test_returns_expected_response(mocked_workflow):
    """Return the public response without internal evaluation data."""
    result = process_question("How do I request leave?")

    assert result == {
        "question": "How do I request leave?",
        "department": "hr",
        "routing_reason": "Employee policy question.",
        "answer": "Submit the request through the employee portal.",
        "sources": [
            {
                "document_id": "HR-001",
                "source": "data/hr_docs/vacation_policy.md",
            }
        ],
    }
    assert "context" not in result
    assert "trace_id" not in result


def test_includes_evaluation_data_when_requested(mocked_workflow):
    """Expose context and trace ID only for evaluation workflows."""
    result = process_question(
        "How do I request leave?",
        include_evaluation_data=True,
    )

    assert result["context"] == "Annual leave policy context."
    assert result["trace_id"] == "test-trace-123"
    assert result["department"] == "hr"


def test_passes_callback_to_router(mocked_workflow):
    """Forward the Langfuse callback to the routing model."""
    process_question("How do I request leave?")

    mocked_workflow["router"].assert_called_once_with(
        "How do I request leave?",
        callbacks=[mocked_workflow["handler"]],
    )


def test_creates_trace_with_question_metadata(mocked_workflow):
    """Create a root observation with the question and retrieval count."""
    process_question("How do I request leave?", k=4)

    mocked_workflow[
        "client"
    ].start_as_current_observation.assert_called_once_with(
        name="department-rag-query",
        as_type="span",
        input={
            "question": "How do I request leave?",
            "k": 4,
        },
    )


def test_updates_trace_with_response(mocked_workflow):
    """Store the final answer and department in the trace."""
    result = process_question("How do I request leave?")

    mocked_workflow["trace"].update.assert_called_once_with(
        output=result,
        metadata={"department": "hr"},
    )


def test_flushes_langfuse_after_success(mocked_workflow):
    """Flush pending telemetry after successful processing."""
    process_question("How do I request leave?")

    mocked_workflow["client"].flush.assert_called_once()


def test_flushes_langfuse_after_agent_failure(mocked_workflow):
    """Flush telemetry even when the department agent fails."""
    mocked_workflow["agent"].side_effect = RuntimeError(
        "Agent execution failed."
    )

    with pytest.raises(
        RuntimeError, match="Agent execution failed"
    ):
        process_question("How do I request leave?")

    mocked_workflow["client"].flush.assert_called_once()


@patch("src.orchestrator.record_evaluation_score")
@patch("src.orchestrator.evaluate_answer")
def test_optional_judge_evaluates_response(
    mock_evaluate,
    mock_record,
    mocked_workflow,
):
    """Evaluate and record answer quality when the judge is enabled."""
    judgment = JudgeResult(
        score=9,
        justification="The answer is grounded in the provided context.",
    )
    mock_evaluate.return_value = judgment

    result = process_question(
        "How do I request leave?",
        judge=True,
    )

    assert result["answer_quality_score"] == 9
    assert result["judge_justification"] == judgment.justification

    mock_evaluate.assert_called_once_with(
        question="How do I request leave?",
        answer="Submit the request through the employee portal.",
        context="Annual leave policy context.",
    )

    mock_record.assert_called_once_with(
        "test-trace-123",
        judgment,
    )


@patch("src.orchestrator.record_evaluation_score")
@patch("src.orchestrator.evaluate_answer")
def test_judge_is_not_called_by_default(
    mock_evaluate,
    mock_record,
    mocked_workflow,
):
    """Keep answer evaluation disabled by default."""
    result = process_question("How do I request leave?")

    assert "answer_quality_score" not in result
    assert "judge_justification" not in result

    mock_evaluate.assert_not_called()
    mock_record.assert_not_called()


@patch("src.orchestrator.record_evaluation_score")
@patch("src.orchestrator.evaluate_answer")
def test_judge_failure_still_flushes_langfuse(
    mock_evaluate,
    mock_record,
    mocked_workflow,
):
    """Flush Langfuse even when answer evaluation fails."""
    mock_evaluate.side_effect = RuntimeError(
        "Evaluation failed."
    )

    with pytest.raises(RuntimeError, match="Evaluation failed"):
        process_question(
            "How do I request leave?",
            judge=True,
        )

    mock_record.assert_not_called()
    mocked_workflow["client"].flush.assert_called_once()


@patch("src.orchestrator.record_evaluation_score")
@patch("src.orchestrator.evaluate_answer")
def test_judge_requires_trace_id(
    mock_evaluate,
    mock_record,
    mocked_workflow,
):
    """Prevent score registration without a valid trace identifier."""
    mocked_workflow["client"].get_current_trace_id.return_value = None

    with pytest.raises(ValueError, match="Langfuse trace ID"):
        process_question(
            "How do I request leave?",
            judge=True,
        )

    mock_evaluate.assert_not_called()
    mock_record.assert_not_called()
    mocked_workflow["client"].flush.assert_called_once()
