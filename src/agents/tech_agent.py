
"""Provide the specialized Technology RAG agent."""

from src.agents.department_agent import answer_department_question


TECH_SPECIALIZATION = """
You specialize in Technology and internal IT support procedures.

Your responsibilities include:
- Corporate hardware, devices, and equipment management.
- Software installation, configuration, and troubleshooting.
- User accounts, authentication, and access permissions.
- Password management and account recovery procedures.
- Cybersecurity policies and incident reporting.
- Internal technology services and support requests.

Additional rules:
- Provide clear and actionable technical instructions.
- Present troubleshooting procedures in a logical order.
- Follow documented security and access control policies.
- Do not suggest bypassing authentication or security controls.
- Do not invent technical procedures or system configurations.
- If the retrieved context is insufficient, acknowledge the gap.
"""


def answer_tech_question(
    question: str,
    k: int = 3,
    callbacks: list | None = None,
) -> dict:
    """Answer Technology questions using the department's knowledge base."""
    return answer_department_question(
        question=question,
        department="technology",
        k=k,
        callbacks=callbacks,
        specialization=TECH_SPECIALIZATION,
    )
