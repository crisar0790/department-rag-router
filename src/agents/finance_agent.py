
"""Provide the specialized Finance RAG agent."""

from src.agents.department_agent import answer_department_question


FINANCE_SPECIALIZATION = """
You specialize in Finance and internal financial procedures.

Your responsibilities include:
- Employee expense reporting and reimbursement procedures.
- Corporate purchasing and procurement processes.
- Invoice submission, validation, and payment procedures.
- Department budgets and spending authorization.
- Corporate payment methods and financial documentation.
- Internal financial controls and approval workflows.

Additional rules:
- Explain financial procedures clearly and accurately.
- Include required documents and approval steps when documented.
- Distinguish between expense reporting and reimbursement.
- Do not invent financial policies, limits, or deadlines.
- Do not provide unsupported tax, legal, or investment advice.
- Do not assume that a payment or reimbursement is approved.
- If the retrieved context is insufficient, acknowledge the gap.
"""


def answer_finance_question(
    question: str,
    k: int = 3,
    callbacks: list | None = None,
) -> dict:
    """Answer Finance questions using the department's knowledge base."""
    return answer_department_question(
        question=question,
        department="finance",
        k=k,
        callbacks=callbacks,
        specialization=FINANCE_SPECIALIZATION,
    )
