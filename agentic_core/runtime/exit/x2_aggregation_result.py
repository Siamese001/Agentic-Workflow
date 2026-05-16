"""AG-5 X2 aggregation result carrier (structured)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class X2AggregationResult:
    """Roll-up of X1 into a disposition candidate for X3 emission."""

    disposition_candidate: str
    decisive_failures: tuple[str, ...] = field(default_factory=tuple)
    unknown_material_fields: tuple[str, ...] = field(default_factory=tuple)
    policy_ref: str = ""
    emits_final_x3: bool = False
    deterministic_blocked: bool = False


__all__ = ["X2AggregationResult"]
