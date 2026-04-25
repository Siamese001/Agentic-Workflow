"""PlanBundle + RuleAwarePlanningFrame — typed L1 PLAN BUNDLE outputs.

Implements the doctrine of `02_L1_Reasoning_Plan_Generation_v4.md`
§ "GATHERING RULES, EXAMPLES, AND PRIORS" (M1-M4) and the resulting
``rule_aware_planning_frame``.

Read-only with respect to L4. The bundle aggregates four feeds:

* **M1 Standard Checklist** — task schemas, route heuristics, output
  contracts, validation rubric, artifact templates.
* **M2 Safety / Policy** — policy bounds, escalation thresholds,
  disallowed actions, HITL trigger hints.
* **M3 Past Examples** — prior good answers, SOPs, exemplars, success
  modes, edge cases.
* **M4 Pre-Approved Templates** — bound plan archetypes, safe decomp
  habits, retry boundaries, abstain patterns.

Layer authority: L1. Bundle producers may read from L4 archive, but the
bundle itself is an L1-owned, frozen, hash-stable artifact.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "PlanBundle",
    "PlanBundleViolation",
    "RuleAwarePlanningFrame",
]


class PlanBundleViolation(ValueError):
    """Raised when a :class:`PlanBundle` fails validation."""


@dataclass(frozen=True)
class PlanBundle:
    """Bundled rules, examples, and priors visible to the L1 planner.

    Doc reference: line 64::

        plan_bundle = schemas + policy + exemplars + priors
                    + approved patterns + limits

    Each member is a tuple-of-strings keyed by section name (M1..M4) so
    the bundle is hash-stable and serializable. Callers that need
    structured records should pre-serialize them (e.g. to JSON) before
    placing them into the tuple.
    """

    schemas: tuple = ()                   # M1 task schemas
    route_heuristics: tuple = ()          # M1 route heuristics
    output_contracts: tuple = ()          # M1 output contracts
    validation_rubric: tuple = ()         # M1 validation rubric
    policy_bounds: tuple = ()             # M2 compliance bounds
    escalation_thresholds: tuple = ()     # M2 escalation thresholds
    disallowed_actions: tuple = ()        # M2 disallowed actions
    hitl_triggers: tuple = ()             # M2 HITL trigger hints
    exemplars: tuple = ()                 # M3 prior good answers / SOPs
    edge_cases: tuple = ()                # M3 known edge cases
    approved_templates: tuple = ()        # M4 pre-approved plan archetypes
    stopping_rules: tuple = ()            # M4 stopping rules
    retry_boundaries: tuple = ()          # M4 retry boundaries
    abstain_patterns: tuple = ()          # M4 abstain patterns
    max_steps: int = 10                   # M4 max-effort bound
    max_wallclock_ms: int = 60_000        # M4 max-effort bound
    bundle_hash: str = ""                 # auto-computed if empty

    _STR_TUPLE_FIELDS: tuple = field(
        default=(
            "schemas",
            "route_heuristics",
            "output_contracts",
            "validation_rubric",
            "policy_bounds",
            "escalation_thresholds",
            "disallowed_actions",
            "hitl_triggers",
            "exemplars",
            "edge_cases",
            "approved_templates",
            "stopping_rules",
            "retry_boundaries",
            "abstain_patterns",
        ),
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        for fname in self._STR_TUPLE_FIELDS:
            val = getattr(self, fname)
            if isinstance(val, str) or not hasattr(val, "__iter__"):
                raise PlanBundleViolation(f"{fname} must be a tuple of str.")
            for idx, item in enumerate(val):
                if not isinstance(item, str):
                    raise PlanBundleViolation(
                        f"{fname}[{idx}] must be str, got {type(item)}"
                    )
        if self.max_steps <= 0:
            raise PlanBundleViolation("max_steps must be positive")
        if self.max_wallclock_ms <= 0:
            raise PlanBundleViolation("max_wallclock_ms must be positive")
        if not self.bundle_hash:
            digest = hashlib.sha256(self._canonical_bytes()).hexdigest()
            object.__setattr__(self, "bundle_hash", digest)

    def _canonical_bytes(self) -> bytes:
        payload: dict[str, Any] = {
            fname: list(getattr(self, fname)) for fname in self._STR_TUPLE_FIELDS
        }
        payload["max_steps"] = self.max_steps
        payload["max_wallclock_ms"] = self.max_wallclock_ms
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            fname: list(getattr(self, fname)) for fname in self._STR_TUPLE_FIELDS
        }
        d["max_steps"] = self.max_steps
        d["max_wallclock_ms"] = self.max_wallclock_ms
        d["bundle_hash"] = self.bundle_hash
        return d


@dataclass(frozen=True)
class RuleAwarePlanningFrame:
    """Output of the M1-M4 merge stage.

    Doc reference: line 67::

        rule-aware planning frame = what can be proposed
            + what must be grounded
            + what must be escalated

    Each member is a tuple of human-readable predicates the planner
    attaches to the candidate plan during P1-P4 drafting.
    """

    can_be_proposed: tuple = ()
    must_be_grounded: tuple = ()
    must_be_escalated: tuple = ()

    def __post_init__(self) -> None:
        for fname in ("can_be_proposed", "must_be_grounded", "must_be_escalated"):
            val = getattr(self, fname)
            if isinstance(val, str) or not hasattr(val, "__iter__"):
                raise PlanBundleViolation(f"{fname} must be a tuple of str.")
            for idx, item in enumerate(val):
                if not isinstance(item, str):
                    raise PlanBundleViolation(
                        f"{fname}[{idx}] must be str, got {type(item)}"
                    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "can_be_proposed": list(self.can_be_proposed),
            "must_be_grounded": list(self.must_be_grounded),
            "must_be_escalated": list(self.must_be_escalated),
        }
