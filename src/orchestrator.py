
"""Coordinate department routing, RAG agents, and Langfuse tracing."""

from src.agents.department_agent import answer_department_question
from src.observability import create_langfuse_client, create_langfuse_handler
from src.router import route_question


def process_question(question: str, k: int = 3) -> dict:
    """Route a question and generate a traced, grounded answer."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if k < 1:
        raise ValueError("Retrieval count must be at least 1.")

    langfuse = create_langfuse_client()
    handler = create_langfuse_handler()

    try:
        with langfuse.start_as_current_observation(
            name="department-rag-query",
            as_type="span",
            input={"question": question, "k": k},
        ) as trace:
            routing = route_question(
                question,
                callbacks=[handler],
            )

            result = answer_department_question(
                question=question,
                department=routing.department,
                k=k,
                callbacks=[handler],
            )

            output = {
                "question": question,
                "department": routing.department,
                "routing_reason": routing.reason,
                "answer": result["answer"],
                "sources": result["sources"],
            }

            trace.update(
                output=output,
                metadata={"department": routing.department},
            )

            return output
    finally:
        langfuse.flush()
