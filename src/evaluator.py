
"""Evaluate RAG answers using an LLM judge and Langfuse scores."""

from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config import (
    MAX_OUTPUT_TOKENS,
    OPENAI_API_KEY,
    OPENAI_EVALUATOR_MODEL,
    OPENAI_MAX_RETRIES,
    OPENAI_REASONING_EFFORT,
    OPENAI_TIMEOUT,
)
from src.observability import create_langfuse_client


JUDGE_PROMPT = """
You are an independent evaluator of a retrieval-augmented answer.

Evaluate the answer using only the supplied document context.

Criteria:
- Faithfulness: Are factual claims supported by the context?
- Completeness: Does the answer address the user's question?
- Relevance: Is the answer focused on the question?

Assign an overall score from 1 to 10:
1 = unsupported or entirely incorrect.
5 = partially correct or incomplete.
10 = accurate, complete, and fully grounded.

Do not reward unsupported details.
If the context is insufficient, reward an honest acknowledgment
of missing information rather than an invented answer.

Provide a concise justification in English.
"""


class JudgeResult(BaseModel):
    """Structured evaluation produced by the judge model."""

    score: int = Field(ge=1, le=10)
    justification: str = Field(min_length=1)


def create_evaluator_model() -> ChatOpenAI:
    """Create the configured model for answer evaluation."""
    if not OPENAI_EVALUATOR_MODEL:
        raise ValueError("Set OPENAI_EVALUATOR_MODEL in your .env file.")

    return ChatOpenAI(
        model=OPENAI_EVALUATOR_MODEL,
        api_key=OPENAI_API_KEY,
        use_responses_api=True,
        reasoning_effort=OPENAI_REASONING_EFFORT,
        timeout=OPENAI_TIMEOUT,
        max_retries=OPENAI_MAX_RETRIES,
        max_tokens=MAX_OUTPUT_TOKENS,
    )


def evaluate_answer(
    question: str,
    answer: str,
    context: str,
) -> JudgeResult:
    """Score an answer against the retrieved document context."""
    model = create_evaluator_model().with_structured_output(
        JudgeResult,
        method="json_schema",
    )

    response = model.invoke(
        [
            SystemMessage(content=JUDGE_PROMPT),
            HumanMessage(
                content=(
                    f"Question:\n{question}\n\n"
                    f"Document context:\n{context}\n\n"
                    f"Answer:\n{answer}"
                )
            ),
        ]
    )

    return response


def record_evaluation_score(
    trace_id: str,
    result: JudgeResult,
) -> None:
    """Record an evaluation score in Langfuse."""
    langfuse = create_langfuse_client()

    try:
        langfuse.create_score(
            trace_id=trace_id,
            name="answer_quality",
            value=result.score,
            data_type="NUMERIC",
            comment=result.justification,
        )
    finally:
        langfuse.flush()
