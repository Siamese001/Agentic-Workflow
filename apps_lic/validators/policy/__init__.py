"""apps_lic.policy — declarative decision tables consumed by DecisionRouter.

This package replaces decision-tree HOPs (HOP4 Routing, HOP7 GateDecision,
plus imperative classifier chains inside HOP1 and HOP5) with YAML-driven
policies dispatched by a single generic primitive.

See `.windsurf/plans/decision-router-policy-tables-b3a4d2.md`.
"""
from apps_lic.validators.policy.decision_router import (
    DecisionRouter,
    PolicyMatch,
    PolicyLoadError,
    NoMatchError,
)
from apps_lic.validators.policy.judge_base import (
    JudgeBase,
    JudgeScorecard,
    Rubric,
    RubricLoadError,
    EvaluateFn,
)

__all__ = [
    "DecisionRouter",
    "PolicyMatch",
    "PolicyLoadError",
    "NoMatchError",
    "JudgeBase",
    "JudgeScorecard",
    "Rubric",
    "RubricLoadError",
    "EvaluateFn",
]
