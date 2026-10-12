
"""Evaluate department routing, retrieval, and answer quality."""

import argparse
import json
from pathlib import Path

from src.evaluator import evaluate_answer, record_evaluation_score
from src.orchestrator import process_question


DEFAULT_QUERIES_PATH = Path("test_queries.json")


def load_test_queries(path: Path) -> list[dict]:
    """Load and validate the evaluation dataset."""
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    queries = data["queries"]
    if not isinstance(queries, list) or not queries:
        raise ValueError("Evaluation queries must be a non-empty list.")

    valid_departments = {
        "hr",
        "technology",
        "finance",
        "out_of_scope",
    }

    for query in queries:
        if query.get("expected_department") not in valid_departments:
            raise ValueError(
                f"Invalid expected department for query {query.get('id')}"
            )

    return queries


def _evaluate_quality(query: dict, result: dict) -> dict:
    """Judge an answer and attach its score to the RAG trace."""
    if query["category"] == "out_of_scope":
        return {"answer_quality_score": None, "judge_justification": None}

    if not result.get("trace_id"):
        raise ValueError("A Langfuse trace ID is required for scoring.")

    judgment = evaluate_answer(
        question=query["question"],
        answer=result["answer"],
        context=result["context"],
    )
    record_evaluation_score(result["trace_id"], judgment)

    return {
        "answer_quality_score": judgment.score,
        "judge_justification": judgment.justification,
    }


def evaluate_query(query: dict, k: int = 3, judge: bool = True) -> dict:
    """Evaluate one question using the complete RAG workflow."""
    result = process_question(
        query["question"], k=k, include_evaluation_data=judge
    )
    expected = query["expected_department"]
    expected_ids = set(query["expected_document_ids"])
    retrieved_ids = {
        source["document_id"] for source in result["sources"]
    }

    evaluation = {
        "id": query["id"],
        "category": query["category"],
        "expected_department": expected,
        "predicted_department": result["department"],
        "routing_correct": result["department"] == expected,
        "expected_document_ids": sorted(expected_ids),
        "retrieved_document_ids": sorted(retrieved_ids),
        "retrieval_hit": bool(expected_ids & retrieved_ids)
        if expected_ids else None,
        "answer": result["answer"],
    }
    if judge:
        evaluation.update(_evaluate_quality(query, result))
    return evaluation


def _calculate_rate(results: list[dict], key: str) -> tuple[int, float | None]:
    """Calculate the proportion of successful applicable cases."""
    values = [case[key] for case in results if case.get(key) is not None]
    return len(values), sum(values) / len(values) if values else None


def calculate_metrics(results: list[dict]) -> dict:
    """Calculate aggregate routing, retrieval, and quality metrics."""
    routing_count, routing_rate = _calculate_rate(results, "routing_correct")
    retrieval_count, retrieval_rate = _calculate_rate(results, "retrieval_hit")
    scores = [
        case["answer_quality_score"]
        for case in results
        if case.get("answer_quality_score") is not None
    ]

    return {
        "total_queries": len(results),
        "routing_evaluated": routing_count,
        "routing_accuracy": routing_rate,
        "retrieval_evaluated": retrieval_count,
        "retrieval_hit_rate": retrieval_rate,
        "quality_evaluated": len(scores),
        "average_answer_quality": sum(scores) / len(scores) if scores else None,
    }


def run_evaluation(path: Path, k: int = 3, judge: bool = True) -> dict:
    """Run all evaluation cases and aggregate their results."""
    queries = load_test_queries(path)
    results = []

    for query in queries:
        print(f"Evaluating {query['id']}...", flush=True)
        results.append(evaluate_query(query, k=k, judge=judge))

    return {"metrics": calculate_metrics(results), "results": results}


def main() -> None:
    """Run the evaluation from the command line."""
    parser = argparse.ArgumentParser(description="Evaluate the RAG system.")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES_PATH)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument(
        "--no-judge",
        action="store_false",
        dest="judge",
        help="Skip LLM quality evaluation (routing and retrieval only).",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("evaluation/report.json")
    )
    args = parser.parse_args()

    if args.k < 1:
        parser.error("--k must be at least 1")

    report = run_evaluation(args.queries, k=args.k, judge=args.judge)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
