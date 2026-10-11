
"""Route user questions to the appropriate department agent."""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.models import create_chat_model


Department = Literal["hr", "technology", "finance"]


class RoutingDecision(BaseModel):
    """Represent a structured department routing decision."""

    department: Department = Field(
        description="Department responsible for the user question."
    )
    reason: str = Field(
        description="Brief explanation of the routing decision."
    )


ROUTER_PROMPT = """
You are the department router for AR Cloud.

Classify the user's question into exactly one department:

- hr: Employee policies, leave, onboarding, benefits,
  employment procedures, and human resources matters.

- technology: IT support, devices, software, accounts,
  access permissions, cybersecurity, and technical procedures.

- finance: Expenses, reimbursements, purchasing, invoices,
  budgets, payments, and financial procedures.

Rules:
- Select the department primarily responsible for the question.
- Use the user's intent rather than isolated keywords.
- Do not answer the question.
- Provide a brief reason for your classification.
- For ambiguous questions, select the most likely department.
- Return only the structured routing decision.
"""


def route_question(
    question: str,
    callbacks: list | None = None,
) -> RoutingDecision:
    """Classify a question and select its responsible department."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    model = create_chat_model().with_structured_output(
        RoutingDecision,
        method="json_schema",
    )

    return model.invoke(
        [
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=question),
        ],
        config={"callbacks": callbacks or []},
    )
