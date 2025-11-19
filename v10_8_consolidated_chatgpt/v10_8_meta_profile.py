"""Meta profile definitions."""

from dataclasses import dataclass, field
from typing import Any, Dict

from observability import compute_optimization_hint
from self_correction import SelfCorrectionSurface


@dataclass
class MetaProfile:
    routing_bias: Dict[str, Any] = field(default_factory=dict)
    planning_bias: Dict[str, Any] = field(default_factory=dict)


META_PROFILE = MetaProfile()


def update_meta_profile_from_spans_and_self_correction(spans, sc):
    """Update in-memory meta profile using spans and self-correction signals."""

    optimization_hint = compute_optimization_hint(spans or [])
    if optimization_hint.get("suggestion") == "reroute_fast":
        META_PROFILE.routing_bias["prefer_fast"] = True

    sc = sc or {}
    surface = sc.get("surface")
    recommendation = sc.get("recommendation") if isinstance(sc, dict) else None
    if (
        surface == SelfCorrectionSurface.QA_RECHECK.value
        and isinstance(recommendation, dict)
        and recommendation.get("needs_retry")
    ):
        META_PROFILE.planning_bias["conservative"] = True
