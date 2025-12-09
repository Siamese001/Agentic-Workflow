"""
Control plane decision logic for résumé processing safety enforcement.

Provides rule evaluation and verdict aggregation for comprehensive résumé improvement workflows.
"""

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field

from .models import PolicyRule


class RuleMatch(BaseModel):
    """
    Represents policy rule match for résumé processing safety evaluation.

    Enables systematic safety assessment for comprehensive résumé enhancement operations.
    """

    rule_id: str
    category: str
    severity: str
    is_pii: bool = False

    # Optional small snippet or structured payload.
    details: Dict[str, Any] = Field(default_factory=dict)


class RulesEngineResult(BaseModel):
    """
    Aggregates rule evaluation results for résumé processing safety decisions.

    Provides comprehensive safety assessment for résumé improvement workflows.
    """

    matches: List[RuleMatch] = Field(default_factory=list)
    max_severity: Optional[str] = None
    has_pii: bool = False


class JudgeVerdict(BaseModel):
    """
    Represents safety verdict for résumé processing control plane decisions.

    Enables structured safety validation for comprehensive résumé enhancement operations.
    """

    verdict: Literal["safe", "unsafe", "ambiguous"]
    explanation: str
    signals: Dict[str, Any] = Field(default_factory=dict)


class SafetyPipelineTrace(BaseModel):
    """
    Provides debugging trace for résumé processing safety pipeline execution.

    Enables observability and troubleshooting for résumé improvement safety workflows.
    """

    rules_engine: Dict[str, Any] = Field(default_factory=dict)
    judge: Dict[str, Any] = Field(default_factory=dict)


def aggregate_severity(levels: List[str]) -> Optional[str]:
    """
    Aggregates severity levels for résumé processing safety decisions.

    Ensures proper risk assessment for comprehensive résumé enhancement workflows.
    """

    order = {"low": 0, "medium": 1, "high": 2}
    best: Optional[str] = None
    best_score = -1
    for lvl in levels:
        score = order.get(lvl, -1)
        if score > best_score:
            best = lvl
            best_score = score
    return best


def enabled_rules(rules: List[PolicyRule]) -> List[PolicyRule]:
    """
    Filters enabled policy rules for résumé processing safety enforcement.

    Ensures only active rules are applied in résumé improvement workflows.
    """

    return [r for r in rules if getattr(r, "enabled", True)]



