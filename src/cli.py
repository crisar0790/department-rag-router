
"""Provide a command-line interface for the department RAG system."""

import argparse

from src.orchestrator import process_question


def _display_result(result: dict) -> None:
    """Display the generated answer and its document sources."""
    print(f"\nDepartment: {result['department']}")
    print(f"Routing reason: {result['routing_reason']}")
    print(f"\nAnswer:\n{result['answer']}")

    sources = {
        (item["document_id"], item["source"])
        for item in result["sources"]
    }

    if sources:
        print("\nSources:")
        for document_id, source in sorted(sources):
            print(f"- {document_id}: {source}")

    if "answer_quality_score" in result:
        print(f"\nAnswer quality: {result['answer_quality_score']}/10")
        print(f"Judge justification: {result['judge_justification']}")


def _run_interactive(k: int, judge: bool = False) -> None:
    """Process questions until the user exits the session."""
    print("AR Cloud Department RAG")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            result = process_question(
                question,
                k=k,
                judge=judge,
            )
            _display_result(result)
        except Exception as exc:
            print(f"Error: {exc}")

        print()


def main() -> None:
    """Parse CLI arguments and execute the requested mode."""
    parser = argparse.ArgumentParser(
        description="Ask questions about AR Cloud departments."
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Process a single question.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=3,
        help="Number of document chunks to retrieve (default: 3).",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="Evaluate the generated answer using the LLM judge.",
    )

    args = parser.parse_args()

    if args.k < 1:
        parser.error("--k must be at least 1.")

    if args.question is None:
        _run_interactive(args.k, judge=args.judge)
        return

    try:
        result = process_question(
            args.question,
            k=args.k,
            judge=args.judge,
        )
        _display_result(result)
    except Exception as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
