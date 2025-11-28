"""
Control plane models for résumé processing safety and policy management.

Provides structured data models for comprehensive résumé improvement workflow control.
"""

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field

from core.models.models import ExecutionProfile


class SafetyContext(BaseModel):
    """
    Provides safety context for résumé processing control plane operations.

    Ensures secure and compliant execution of comprehensive résumé enhancement workflows.
    """

    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    task_type: Optional[str] = None

    # Free-form text being evaluated (prompt, draft, or combined surface).
    input_text: str = ""

    # Logical tools the agent intends to use for this task.
    tools: List[str] = Field(default_factory=list)

    # Optional execution profile snapshot for routing/telemetry.
    execution_profile: Optional[ExecutionProfile] = None

    # Arbitrary structured metadata (already-safe fields only).
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PolicyRule(BaseModel):
    """
    Defines policy rule for résumé processing safety enforcement.

    Enables systematic safety validation for comprehensive résumé improvement operations.
    """

    id: str
    description: str

    # High-level safety category (e.g. "pii", "violence", "self_harm").
    category: str

    # Coarse severity level used for tagging and aggregation.
    severity: Literal["low", "medium", "high"]

    # Optional regex pattern applied to SafetyContext.input_text.
    pattern: Optional[str] = None

    # Optional tool name flag (for high-risk tool calls).
    tool_name: Optional[str] = None

    # Mark rule as PII-related for downstream aggregation.
    is_pii_rule: bool = False

    enabled: bool = True


class PolicyDecision(BaseModel):
    """
    Represents final safety decision for résumé processing workflows.

    Provides structured control-plane outcomes for comprehensive résumé enhancement operations.
    """

    action: Literal["allow", "deny", "revise", "escalate"]
    verdict: Literal["safe", "unsafe", "ambiguous"]
    reason: str

    # IDs of rules that contributed to this decision.
    rule_ids: List[str] = Field(default_factory=list)

    # Aggregated severity for quick inspection.
    max_severity: Optional[str] = None

    # Free-form, structured details (e.g., matched snippets, tool flags).
    details: Dict[str, Any] = Field(default_factory=dict)



