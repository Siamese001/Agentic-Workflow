"""
Control plane routing for résumé processing safety policy selection.

Provides deterministic rule resolution for comprehensive résumé improvement workflows.
"""

from typing import List

from .models import PolicyRule, SafetyContext


def default_rules_for(agent_id: str | None, task_type: str | None) -> List[PolicyRule]:
    """
    Returns default safety rules for résumé processing agent and task combinations.

    Ensures appropriate policy enforcement for comprehensive résumé enhancement operations.
    """

    rules: List[PolicyRule] = []

    aid = (agent_id or "").lower()
    task = (task_type or "").lower()

    # Basic PII rule for any text-generation task.
    rules.append(
        PolicyRule(
            id="pii_email_basic",
            description="Flag potential email addresses as PII.",
            category="pii",
            severity="medium",
            pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            is_pii_rule=True,
        )
    )

    # Heavier rule set for safety agents.
    if "safety" in aid or task in {"safety_check", "safety"}:
        rules.append(
            PolicyRule(
                id="violence_keywords",
                description="Flag obvious violence keywords.",
                category="violence",
                severity="high",
                pattern=r"kill|murder|suicide|self[- ]harm",
            )
        )

    # High-risk tool usage (generic flag, does not depend on provider impls).
    rules.append(
        PolicyRule(
            id="high_risk_tool_write_file",
            description="Flag use of high-risk write_file tools.",
            category="tools_high_risk",
            severity="medium",
            tool_name="write_file",
        )
    )

    return rules


def resolve_rules_for_context(ctx: SafetyContext) -> List[PolicyRule]:
    """
    Resolves safety rules for résumé processing context.

    Provides appropriate policy selection for comprehensive résumé enhancement workflows.
    """

    return default_rules_for(ctx.agent_id, ctx.task_type)



