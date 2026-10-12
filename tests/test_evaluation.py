
"""Unit tests for RAG evaluation and quality scoring."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.evaluation import (
    calculate_metrics,
    evaluate_query,
    load_test_queries,
    run_evaluation,
)
from src.evaluator import JudgeResult, record_evaluation_score


@pytest.fixture
def sample_query():
    """Create a standard HR evaluation query."""
    return {
        "id": "HR-01",
        "question": "How do I request annual leave?",
        "expected_department": "hr",
        "expected_document_ids": ["HR-001"],
        "category": "standard",
    }


@pytest.fixture
def sample_result():
    """Create a simulated RAG response."""
    return {
        "department": "hr",
        "answer": "Submit the request through the employee portal.",
        "sources": [
            {
                "document_id": "HR-001",
                "source": "data/hr_docs/vacation_policy.md",
            }
        ],
        "context": "Employees submit leave requests through the portal.",
        "trace_id": "test-trace-123",
    }


def test_load_test_queries_reads_valid_dataset(tmp_path):
    """Load evaluation questions from a JSON file."""
    path = tmp_path / "queries.json"
    path.write_text(
        json.dumps({
            "queries": [
                {
                    "id": "HR-01",
                    "expected_department": "hr",
                }
            ]
        }),
        encoding="utf-8",
    )

    queries = load_test_queries(path)

    assert len(queries) == 1
    assert queries[0]["id"] == "HR-01"


@pytest.mark.parametrize("queries", [[], "invalid", None])
def test_load_test_queries_rejects_invalid_dataset(tmp_path, queries):
    """Reject datasets without a non-empty query list."""
    path = tmp_path / "queries.json"
    path.write_text(
        json.dumps({"queries": queries}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty list"):
        load_test_queries(path)


def test_project_dataset_contains_fifteen_queries():
    """Verify the committed evaluation dataset."""
    queries = load_test_queries(Path("test_queries.json"))

    assert len(queries) == 15
    assert {query["category"] for query in queries} == {
        "standard",
        "cross_department",
        "out_of_scope",
    }


@patch("src.evaluation.process_question")
def test_evaluate_query_correct_routing_and_retrieval(
    mock_process, sample_query, sample_result
):
    """Recognize correct routing and retrieval."""
    mock_process.return_value = sample_result

    result = evaluate_query(sample_query, judge=False)

    assert result["routing_correct"] is True
    assert result["retrieval_hit"] is True
    assert result["retrieved_document_ids"] == ["HR-001"]

    mock_process.assert_called_once_with(
        sample_query["question"],
        k=3,
        include_evaluation_data=False,
    )


@patch("src.evaluation.process_question")
def test_evaluate_query_detects_incorrect_routing(
    mock_process, sample_query, sample_result
):
    """Detect routing predictions that differ from expectations."""
    mock_process.return_value = {
        **sample_result,
        "department": "finance",
    }

    result = evaluate_query(sample_query, judge=False)

    assert result["routing_correct"] is False


@patch("src.evaluation.process_question")
def test_evaluate_query_detects_retrieval_miss(
    mock_process, sample_query, sample_result
):
    """Detect retrieval without an expected document."""
    mock_process.return_value = {
        **sample_result,
        "sources": [
            {
                "document_id": "HR-999",
                "source": "other.md",
            }
        ],
    }

    result = evaluate_query(sample_query, judge=False)

    assert result["retrieval_hit"] is False



@patch("src.evaluation.process_question")
def test_out_of_scope_query_counts_as_correct_routing(
    mock_process, sample_result
):
    """Count correct rejection as routing success without retrieval."""
    mock_process.return_value = {
        **sample_result,
        "department": "out_of_scope",
        "answer": "This question is outside the supported domains.",
        "sources": [],
    }

    query = {
        "id": "EDGE-03",
        "question": "What will the weather be tomorrow?",
        "expected_department": "out_of_scope",
        "expected_document_ids": [],
        "category": "out_of_scope",
    }

    result = evaluate_query(query)

    assert result["routing_correct"] is True
    assert result["retrieval_hit"] is None
    assert result["predicted_department"] == "out_of_scope"
    assert result["retrieved_document_ids"] == []


@patch("src.evaluation.process_question")
def test_out_of_scope_query_detects_incorrect_routing(
    mock_process, sample_result
):
    """Detect out-of-scope questions routed to a department."""
    mock_process.return_value = {
        **sample_result,
        "department": "hr",
    }

    query = {
        "id": "EDGE-03",
        "question": "What will the weather be tomorrow?",
        "expected_department": "out_of_scope",
        "expected_document_ids": [],
        "category": "out_of_scope",
    }

    result = evaluate_query(query)

    assert result["routing_correct"] is False
    assert result["retrieval_hit"] is None


def test_calculate_metrics_with_mixed_results():
    """Calculate metrics using only applicable cases."""
    results = [
        {
            "routing_correct": True,
            "retrieval_hit": True,
            "answer_quality_score": 10,
        },
        {
            "routing_correct": False,
            "retrieval_hit": True,
            "answer_quality_score": 8,
        },
        {
            "routing_correct": None,
            "retrieval_hit": None,
            "answer_quality_score": None,
        },
    ]

    metrics = calculate_metrics(results)

    assert metrics["total_queries"] == 3
    assert metrics["routing_evaluated"] == 2
    assert metrics["routing_accuracy"] == 0.5
    assert metrics["retrieval_evaluated"] == 2
    assert metrics["retrieval_hit_rate"] == 1.0
    assert metrics["quality_evaluated"] == 2
    assert metrics["average_answer_quality"] == 9.0


def test_calculate_metrics_handles_empty_results():
    """Handle empty evaluation results without division errors."""
    metrics = calculate_metrics([])

    assert metrics["total_queries"] == 0
    assert metrics["routing_accuracy"] is None
    assert metrics["retrieval_hit_rate"] is None
    assert metrics["average_answer_quality"] is None


@patch("src.evaluation.record_evaluation_score")
@patch("src.evaluation.evaluate_answer")
@patch("src.evaluation.process_question")
def test_evaluate_query_with_llm_judge(
    mock_process,
    mock_evaluate_answer,
    mock_record_score,
    sample_query,
    sample_result,
):
    """Evaluate answer quality and register its Langfuse score."""
    mock_process.return_value = sample_result
    judgment = JudgeResult(
        score=9,
        justification="The answer is supported by the context.",
    )
    mock_evaluate_answer.return_value = judgment

    result = evaluate_query(sample_query, judge=True)

    assert result["answer_quality_score"] == 9
    assert result["judge_justification"] == judgment.justification

    mock_evaluate_answer.assert_called_once_with(
        question=sample_query["question"],
        answer=sample_result["answer"],
        context=sample_result["context"],
    )
    mock_record_score.assert_called_once_with(
        "test-trace-123",
        judgment,
    )
    assert mock_process.call_args.kwargs["include_evaluation_data"] is True


@patch("src.evaluation.process_question")
def test_judge_requires_langfuse_trace(
    mock_process, sample_query, sample_result
):
    """Require a trace identifier when judge scoring is enabled."""
    mock_process.return_value = {
        **sample_result,
        "trace_id": None,
    }

    with pytest.raises(ValueError, match="Langfuse trace ID"):
        evaluate_query(sample_query, judge=True)


@pytest.mark.parametrize("score", [0, -1, 11])
def test_judge_result_rejects_invalid_scores(score):
    """Reject quality scores outside the supported range."""
    with pytest.raises(ValidationError):
        JudgeResult(score=score, justification="Invalid score.")


@pytest.mark.parametrize("score", [1, 5, 10])
def test_judge_result_accepts_valid_scores(score):
    """Accept quality scores within the supported range."""
    result = JudgeResult(
        score=score,
        justification="Valid evaluation score.",
    )

    assert result.score == score


@patch("src.evaluator.create_langfuse_client")
def test_record_evaluation_score(mock_create_client):
    """Send the judge score to Langfuse and flush the client."""
    judgment = JudgeResult(
        score=10,
        justification="Fully supported answer.",
    )

    record_evaluation_score("trace-123", judgment)

    client = mock_create_client.return_value
    client.create_score.assert_called_once_with(
        trace_id="trace-123",
        name="answer_quality",
        value=10,
        data_type="NUMERIC",
        comment="Fully supported answer.",
    )
    client.flush.assert_called_once()


@patch("src.evaluation.evaluate_query")
@patch("src.evaluation.load_test_queries")
def test_run_evaluation_aggregates_results(
    mock_load_queries, mock_evaluate_query, tmp_path
):
    """Run every query and aggregate the resulting metrics."""
    mock_load_queries.return_value = [
        {"id": "HR-01"},
        {"id": "FIN-01"},
    ]
    mock_evaluate_query.side_effect = [
        {"routing_correct": True, "retrieval_hit": True},
        {"routing_correct": False, "retrieval_hit": True},
    ]

    report = run_evaluation(tmp_path / "queries.json", k=2, judge=False)

    assert report["metrics"]["total_queries"] == 2
    assert report["metrics"]["routing_accuracy"] == 0.5
    assert report["metrics"]["retrieval_hit_rate"] == 1.0
    assert len(report["results"]) == 2
    assert mock_evaluate_query.call_count == 2


@patch("src.evaluator.create_evaluator_model")
def test_evaluate_answer_forwards_callbacks(mock_create_model):
    """Forward Langfuse callbacks to the evaluator model."""
    from unittest.mock import MagicMock

    from src.evaluator import evaluate_answer

    judgment = JudgeResult(
        score=9,
        justification="The answer is grounded in the context.",
    )

    structured_model = MagicMock()
    structured_model.invoke.return_value = judgment

    mock_create_model.return_value.with_structured_output.return_value = (
        structured_model
    )

    callback = MagicMock()

    result = evaluate_answer(
        question="How do I request annual leave?",
        answer="Use the employee portal.",
        context="Leave requests use the employee portal.",
        callbacks=[callback],
    )

    assert result == judgment
    assert structured_model.invoke.call_args.kwargs["config"] == {
        "callbacks": [callback],
    }


@patch("src.evaluation._evaluate_quality")
@patch("src.evaluation.process_question")
def test_evaluate_query_runs_judge_by_default(
    mock_process,
    mock_quality,
    sample_query,
    sample_result,
):
    """Enable answer quality evaluation by default."""
    mock_process.return_value = sample_result
    mock_quality.return_value = {
        "answer_quality_score": 9,
        "judge_justification": "The answer is grounded.",
    }

    result = evaluate_query(sample_query)

    assert result["answer_quality_score"] == 9
    mock_quality.assert_called_once_with(
        sample_query,
        sample_result,
    )
    mock_process.assert_called_once_with(
        sample_query["question"],
        k=3,
        include_evaluation_data=True,
    )


@patch("src.evaluation._evaluate_quality")
@patch("src.evaluation.process_question")
def test_evaluate_query_can_skip_judge(
    mock_process,
    mock_quality,
    sample_query,
    sample_result,
):
    """Allow routing-only evaluation without an LLM judge."""
    mock_process.return_value = sample_result

    result = evaluate_query(sample_query, judge=False)

    assert "answer_quality_score" not in result
    mock_quality.assert_not_called()
    mock_process.assert_called_once_with(
        sample_query["question"],
        k=3,
        include_evaluation_data=False,
    )



@patch("src.evaluation._evaluate_quality")
@patch("src.evaluation.process_question")
def test_out_of_scope_skips_quality_scoring_by_default(
    mock_process,
    mock_quality,
):
    """Exclude out-of-scope responses from LLM quality scoring."""
    query = {
        "id": "EDGE-03",
        "question": "What will the weather be tomorrow?",
        "expected_department": "out_of_scope",
        "expected_document_ids": [],
        "category": "out_of_scope",
    }

    mock_process.return_value = {
        "department": "out_of_scope",
        "answer": "This question is outside the supported domains.",
        "sources": [],
        "context": "",
        "trace_id": "test-trace-123",
    }

    mock_quality.return_value = {
        "answer_quality_score": None,
        "judge_justification": None,
    }

    result = evaluate_query(query)

    assert result["routing_correct"] is True
    assert result["retrieval_hit"] is None
    assert result["answer_quality_score"] is None
    assert result["judge_justification"] is None

    mock_quality.assert_called_once_with(
        query,
        mock_process.return_value,
    )


@patch("src.evaluation.evaluate_answer")
@patch("src.evaluation.record_evaluation_score")
def test_out_of_scope_does_not_invoke_llm_judge(
    mock_record,
    mock_evaluate,
):
    """Avoid judge API calls for out-of-scope questions."""
    from src.evaluation import _evaluate_quality

    query = {"category": "out_of_scope"}
    result = {"trace_id": "test-trace-123"}

    quality = _evaluate_quality(query, result)

    assert quality == {
        "answer_quality_score": None,
        "judge_justification": None,
    }
    mock_evaluate.assert_not_called()
    mock_record.assert_not_called()
