
"""Coordinate question routing and department-specific RAG agents."""

from src.agents.department_agent import answer_department_question
from src.router import route_question


def process_question(question: str, k: int = 3) -> dict:
    """Route a question and generate a grounded department answer."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if k < 1:
        raise ValueError("Retrieval count must be at least 1.")

    routing = route_question(question)

    result = answer_department_question(
        question=question,
        department=routing.department,
        k=k,
    )

    return {
        "question": question,
        "department": routing.department,
        "routing_reason": routing.reason,
        "answer": result["answer"],
        "sources": result["sources"],
    }
