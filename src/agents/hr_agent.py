
"""Provide the specialized Human Resources RAG agent."""

from src.agents.department_agent import answer_department_question


HR_SPECIALIZATION = """
You specialize in Human Resources policies and employee procedures.

Your responsibilities include:
- Employee onboarding and offboarding procedures.
- Annual leave, sick leave, and other absence policies.
- Employee benefits and eligibility requirements.
- Human Resources documentation and internal processes.
- Employment-related questions covered by HR documents.

Additional rules:
- Explain procedures clearly and in a practical order.
- Mention requirements or approval steps only when documented.
- Do not invent employment policies or legal obligations.
- Do not provide unsupported legal advice.
- If the retrieved context is insufficient, acknowledge the gap.
"""


def answer_hr_question(
    question: str,
    k: int = 3,
    callbacks: list | None = None,
) -> dict:
    """Answer HR questions using the department's knowledge base."""
    return answer_department_question(
        question=question,
        department="hr",
        k=k,
        callbacks=callbacks,
        specialization=HR_SPECIALIZATION,
    )
