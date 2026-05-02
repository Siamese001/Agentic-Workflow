"""apps_lic.policy — declarative decision tables consumed by DecisionRouter.

This package replaces decision-tree HOPs (HOP4 Routing, HOP7 GateDecision,
plus imperative classifier chains inside HOP1 and HOP5) with YAML-driven
policies dispatched by a single generic primitive.

See `.windsurf/plans/decision-router-policy-tables-b3a4d2.md`.
"""
from apps_lic.policy.decision_router import (
    DecisionRouter,
    PolicyMatch,
    PolicyLoadError,
    NoMatchError,
)

__all__ = ["DecisionRouter", "PolicyMatch", "PolicyLoadError", "NoMatchError"]
