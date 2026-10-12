
"""Coordinate department routing, RAG agents, and Langfuse tracing."""

from src.agents.hr_agent import answer_hr_question
from src.agents.tech_agent import answer_tech_question
from src.agents.finance_agent import answer_finance_question
from src.evaluator import evaluate_answer, record_evaluation_score
from src.observability import create_langfuse_client, create_langfuse_handler
from src.router import route_question


DEPARTMENT_AGENTS = {
    "hr": answer_hr_question,
    "technology": answer_tech_question,
    "finance": answer_finance_question,
}

OUT_OF_SCOPE_ANSWER = (
    "This assistant can only answer questions about "
    "AR Cloud's Human Resources, Technology, and Finance "
    "policies and procedures."
)


def _judge_response(
    question: str,
    result: dict,
    trace_id: str,
    callbacks: list | None = None,
) -> dict:
    """Evaluate a generated answer and record its quality score."""
    if not trace_id:
        raise ValueError("A Langfuse trace ID is required for scoring.")

    judgment = evaluate_answer(
        question=question,
        answer=result["answer"],
        context=result["context"],
        callbacks=callbacks,
    )

    record_evaluation_score(trace_id, judgment)

    return {
        "answer_quality_score": judgment.score,
        "judge_justification": judgment.justification,
    }


def process_question(
    question: str,
    k: int = 3,
    include_evaluation_data: bool = False,
    judge: bool = False,
) -> dict:
    """Route a question and optionally evaluate the generated answer."""
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
            trace_id = langfuse.get_current_trace_id()

            routing = route_question(
                question,
                callbacks=[handler],
            )

            if routing.department == "out_of_scope":
                output = {
                    "question": question,
                    "department": routing.department,
                    "routing_reason": routing.reason,
                    "answer": OUT_OF_SCOPE_ANSWER,
                    "sources": [],
                }

                trace.update(
                    output=output,
                    metadata={"department": routing.department},
                )

                if include_evaluation_data:
                    return {
                        **output,
                        "context": "",
                        "trace_id": trace_id,
                    }

                return output

            agent = DEPARTMENT_AGENTS[routing.department]

            result = agent(
                question=question,
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

            if judge:
                output.update(
                    _judge_response(
                        question,
                        result,
                        trace_id,
                        callbacks=[handler],
                    )
                )

            trace.update(
                output=output,
                metadata={"department": routing.department},
            )

            if include_evaluation_data:
                return {
                    **output,
                    "context": result["context"],
                    "trace_id": trace_id,
                }

            return output
    finally:
        langfuse.flush()
