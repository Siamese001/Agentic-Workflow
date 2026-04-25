"""IntentFrame + AmbiguityRegister — typed L1 PARSE INTENT outputs.

Implements the doctrine of `02_L1_Reasoning_Plan_Generation_v4.md` § PARSE
INTENT (I1-I4).  L1 must turn the stamped ingress slip into a typed
intent frame *before* any plan drafting begins, and explicitly capture
what is known vs assumed vs unresolved in an AmbiguityRegister.

Layer authority: L1 (cognition plane). These types are read by L1's plan
drafter (P1-P4) and by L1's semantic validators (V1-V5). They are NOT
imported into L0 — the cross-layer artifact is `L1PlanContractV2`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.routing_features import WorkClass

__all__ = [
    "AmbiguityRegister",
    "AmbiguityResolutionStrategy",
    "ConstraintBinding",
    "IntentFrame",
    "IntentFrameViolation",
    "OutputTargetKind",
    "WorkClass",
]


class IntentFrameViolation(ValueError):
    """Raised when an :class:`IntentFrame` fails validation."""


class OutputTargetKind(str, Enum):
    """What kind of deliverable the patron asked for (I1)."""

    ANSWER = "answer"
    PLAN = "plan"
    ARTIFACT = "artifact"
    ACTION = "action"
    CLARIFICATION = "clarification"


class AmbiguityResolutionStrategy(str, Enum):
    """How L1 expects an unresolved item to be reconciled (I-merge → V5)."""

    CLARIFY = "clarify"        # ask the user
    ASSUME = "assume"          # declare assumption and proceed
    GROUND = "ground"          # require C0 retrieval to resolve
    ABSTAIN = "abstain"        # bounded completion impossible
    DEFER = "defer"            # punt to a later turn / wave


@dataclass(frozen=True)
class ConstraintBinding:
    """A single rule/constraint surfaced by I2.

    ``severity`` mirrors the doc's ``must / should / avoid`` taxonomy.
    """

    statement: str
    severity: str  # "must" | "should" | "avoid"
    source: str = "user"  # "user" | "policy" | "schema" | "prior"

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "severity": self.severity,
            "source": self.source,
        }


@dataclass(frozen=True)
class AmbiguityRegister:
    """What is known + what is assumed + what is unresolved.

    Mirrors the second sub-output of doc § PARSE INTENT (line 40):
    ``ambiguity_register = what is known + what is assumed + what would
    require clarification or fallback``.
    """

    known: tuple = ()
    assumed: tuple = ()
    unresolved: tuple = ()
    resolution_strategy: AmbiguityResolutionStrategy = AmbiguityResolutionStrategy.ASSUME

    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    def to_dict(self) -> dict[str, Any]:
        return {
            "known": list(self.known),
            "assumed": list(self.assumed),
            "unresolved": list(self.unresolved),
            "resolution_strategy": self.resolution_strategy.value,
        }


@dataclass(frozen=True)
class IntentFrame:
    """Typed L1 PARSE INTENT output (I1 + I2 + I3 + I4 → merged frame).

    Doc reference: ``02_L1_Reasoning_Plan_Generation_v4.md`` line 37::

        clear intent frame = goal + constraints + details + output target
        + work class + success condition

    All textual fields are pre-stripped, non-empty (except where
    explicitly Optional/empty-tuple-allowed).
    """

    request_id: str
    goal: str                                 # I1 primary objective
    success_condition: str                    # I1 success / outcome definition
    constraints: tuple                        # I2 (ConstraintBinding,)
    details: tuple                            # I3 entities/numbers/format hints (str,)
    output_target_kind: OutputTargetKind      # I3 deliverable shape
    work_class: WorkClass                     # I4 work class
    audience: str = "user"                    # I1 audience / user need
    high_risk: bool = False                   # I4 high-risk vs low-risk
    ambiguity: AmbiguityRegister = field(default_factory=AmbiguityRegister)

    _REQUIRED_STRINGS: tuple = field(
        default=("request_id", "goal", "success_condition"),
        init=False,
        repr=False,
        compare=False,
    )

    def validate(self) -> None:
        """Raise :class:`IntentFrameViolation` on shape / semantic errors."""
        for fname in self._REQUIRED_STRINGS:
            val = getattr(self, fname, None)
            if not isinstance(val, str) or not val.strip():
                raise IntentFrameViolation(
                    f"{fname} must be a non-empty string."
                )
        if not isinstance(self.work_class, WorkClass):
            raise IntentFrameViolation(
                f"work_class must be WorkClass enum, got {type(self.work_class)}"
            )
        if not isinstance(self.output_target_kind, OutputTargetKind):
            raise IntentFrameViolation(
                f"output_target_kind must be OutputTargetKind, got {type(self.output_target_kind)}"
            )
        if isinstance(self.constraints, str) or not hasattr(self.constraints, "__iter__"):
            raise IntentFrameViolation("constraints must be a tuple of ConstraintBinding.")
        for idx, c in enumerate(self.constraints):
            if not isinstance(c, ConstraintBinding):
                raise IntentFrameViolation(
                    f"constraints[{idx}] must be ConstraintBinding, got {type(c)}"
                )
        if isinstance(self.details, str) or not hasattr(self.details, "__iter__"):
            raise IntentFrameViolation("details must be a tuple of str.")
        for idx, d in enumerate(self.details):
            if not isinstance(d, str):
                raise IntentFrameViolation(
                    f"details[{idx}] must be str, got {type(d)}"
                )
        if not isinstance(self.ambiguity, AmbiguityRegister):
            raise IntentFrameViolation(
                f"ambiguity must be AmbiguityRegister, got {type(self.ambiguity)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "goal": self.goal,
            "success_condition": self.success_condition,
            "constraints": [c.to_dict() for c in self.constraints],
            "details": list(self.details),
            "output_target_kind": self.output_target_kind.value,
            "work_class": self.work_class.value,
            "audience": self.audience,
            "high_risk": self.high_risk,
            "ambiguity": self.ambiguity.to_dict(),
        }
