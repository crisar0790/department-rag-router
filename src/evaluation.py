
"""Evaluate department routing and document retrieval."""

import argparse
import json
from pathlib import Path

from src.orchestrator import process_question


DEFAULT_QUERIES_PATH = Path("test_queries.json")


def load_test_queries(path: Path) -> list[dict]:
    """Load and validate the evaluation dataset."""
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    queries = data["queries"]

    if not isinstance(queries, list) or not queries:
        raise ValueError("Evaluation queries must be a non-empty list.")

    return queries


def evaluate_query(query: dict, k: int = 3) -> dict:
    """Evaluate routing and retrieval for one question."""
    result = process_question(query["question"], k=k)
    expected = query["expected_department"]
    expected_ids = set(query["expected_document_ids"])
    retrieved_ids = {
        source["document_id"] for source in result["sources"]
    }

    return {
        "id": query["id"],
        "category": query["category"],
        "expected_department": expected,
        "predicted_department": result["department"],
        "routing_correct": (
            result["department"] == expected
            if expected is not None else None
        ),
        "expected_document_ids": sorted(expected_ids),
        "retrieved_document_ids": sorted(retrieved_ids),
        "retrieval_hit": (
            bool(expected_ids & retrieved_ids)
            if expected_ids else None
        ),
        "answer": result["answer"],
    }


def calculate_metrics(results: list[dict]) -> dict:
    """Calculate accuracy over applicable evaluation cases."""
    routing = [
        case["routing_correct"]
        for case in results
        if case["routing_correct"] is not None
    ]
    retrieval = [
        case["retrieval_hit"]
        for case in results
        if case["retrieval_hit"] is not None
    ]

    return {
        "total_queries": len(results),
        "routing_evaluated": len(routing),
        "routing_accuracy": sum(routing) / len(routing) if routing else None,
        "retrieval_evaluated": len(retrieval),
        "retrieval_hit_rate": (
            sum(retrieval) / len(retrieval) if retrieval else None
        ),
    }


def run_evaluation(path: Path, k: int = 3) -> dict:
    """Run all queries and return results with aggregate metrics."""
    queries = load_test_queries(path)
    results = []

    for query in queries:
        print(f"Evaluating {query['id']}...", flush=True)
        results.append(evaluate_query(query, k=k))

    return {
        "metrics": calculate_metrics(results),
        "results": results,
    }


def main() -> None:
    """Run the evaluation from the command line."""
    parser = argparse.ArgumentParser(
        description="Evaluate department routing and retrieval."
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=DEFAULT_QUERIES_PATH,
    )
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/report.json"),
    )
    args = parser.parse_args()

    if args.k < 1:
        parser.error("--k must be at least 1")

    report = run_evaluation(args.queries, k=args.k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
