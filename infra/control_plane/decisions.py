from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field

from .models import PolicyRule


class RuleMatch(BaseModel):
    """Single rule match produced by the deterministic rules engine."""

    rule_id: str
    category: str
    severity: str
    is_pii: bool = False

    # Optional small snippet or structured payload.
    details: Dict[str, Any] = Field(default_factory=dict)


class RulesEngineResult(BaseModel):
    """Aggregate result of evaluating all rules against a SafetyContext."""

    matches: List[RuleMatch] = Field(default_factory=list)
    max_severity: Optional[str] = None
    has_pii: bool = False


class JudgeVerdict(BaseModel):
    """Guard-model style verdict used by judge_engine.

    Initial implementation is deterministic and does not call LLMs.
    """

    verdict: Literal["safe", "unsafe", "ambiguous"]
    explanation: str
    signals: Dict[str, Any] = Field(default_factory=dict)


class SafetyPipelineTrace(BaseModel):
    """Optional trace object used for debugging / observability."""

    rules_engine: Dict[str, Any] = Field(default_factory=dict)
    judge: Dict[str, Any] = Field(default_factory=dict)


def aggregate_severity(levels: List[str]) -> Optional[str]:
    """Return the highest severity from a list of levels.

    Ordering is: low < medium < high. Unknown levels are ignored.
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
    """Filter down to enabled rules only."""

    return [r for r in rules if getattr(r, "enabled", True)]
