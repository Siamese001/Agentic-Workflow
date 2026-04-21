"""L5 runtime HITL exit-control policy plane.

Per ADR-023, this module owns:
- Escalation class taxonomy (``hitl_classes``)
- Policy classification, approver-pool resolution, timeout, fallback (``hitl_policy``)

This is the RUNTIME HITL (v30 step [5] ESCALATE) — NOT the developer-loop
Author-Gate. The two are disjoint per ADR-023 §2.
"""

from agentic_core.L5_safety.exit_control.hitl_classes import (
    HitlClass,
    HitlClassName,
)
from agentic_core.L5_safety.exit_control.hitl_policy import (
    HitlPolicy,
    PolicyLoadError,
    classify_escalation_class,
    load_policy,
    resolve_approver_pool,
    set_fallback,
    set_timeout,
)

__all__ = [
    "HitlClass",
    "HitlClassName",
    "HitlPolicy",
    "PolicyLoadError",
    "classify_escalation_class",
    "load_policy",
    "resolve_approver_pool",
    "set_fallback",
    "set_timeout",
]
