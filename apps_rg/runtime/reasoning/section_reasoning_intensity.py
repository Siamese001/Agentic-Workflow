"""Declarative reasoning intensity intents per apps_rg Qwen lane (HTTP singleton).

Executive summary declares the strongest knobs (temperature, branching, reflexion samples).
Orchestration actually executing multiple samples/branches remains a separate runner — the
ReasoningExecutionReceipt honestly records IGNORED orch rows for singleton HTTP calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final


class ReasoningIntensityTier(str, Enum):
    """Declared tiers. T1_SIMPLE_REWRITE is reserved — no dispatched lane binds it yet."""

    T0_LOCKED_FACT = "T0_LOCKED_FACT"
    T1_SIMPLE_REWRITE = "T1_SIMPLE_REWRITE"
    T2_QUALITY_SECTION = "T2_QUALITY_SECTION"
    T3_CRITICAL_SECTION = "T3_CRITICAL_SECTION"


@dataclass(frozen=True)
class SectionReasoningProfile:
    """Numeric intent profile for declarative QA + receipts."""

    tier: ReasoningIntensityTier
    temperature: float
    tot_branches: int
    tot_depth: int
    self_consistency_samples: float
    reflexion_loops: float
    executive_lane: bool = False


def profile_to_requested_kw(p: SectionReasoningProfile) -> dict[str, Any]:
    """Keys align with generic resolver knobs (omit duplicate cot_paths field)."""
    return {
        "temperature": p.temperature,
        "tot_branches": float(p.tot_branches),
        "tot_depth": float(p.tot_depth),
        "self_consistency_samples": p.self_consistency_samples,
        "reflexion_loops": p.reflexion_loops,
    }


# --- Tier presets (frozen defaults).
_T0_LOCKED = SectionReasoningProfile(
    tier=ReasoningIntensityTier.T0_LOCKED_FACT,
    temperature=0.15,
    tot_branches=1,
    tot_depth=1,
    self_consistency_samples=1.0,
    reflexion_loops=0.0,
    executive_lane=False,
)

_T3_NON_EXEC = SectionReasoningProfile(
    tier=ReasoningIntensityTier.T3_CRITICAL_SECTION,
    temperature=0.39,
    tot_branches=3,
    tot_depth=2,
    self_consistency_samples=4.0,
    reflexion_loops=1.0,
    executive_lane=False,
)

_EXEC_SUMMARY_PROFILE = SectionReasoningProfile(
    tier=ReasoningIntensityTier.T3_CRITICAL_SECTION,
    temperature=0.42,
    tot_branches=3,
    tot_depth=2,
    self_consistency_samples=5.0,
    reflexion_loops=2.0,
    executive_lane=True,
)

_T2_QUALITY = SectionReasoningProfile(
    tier=ReasoningIntensityTier.T2_QUALITY_SECTION,
    temperature=0.32,
    tot_branches=2,
    tot_depth=2,
    self_consistency_samples=3.0,
    reflexion_loops=1.0,
    executive_lane=False,
)

_lane_map: Final[dict[str, SectionReasoningProfile]] = {
    "education": _T0_LOCKED,
    "certifications": _T0_LOCKED,
    "headline": _T3_NON_EXEC,
    "executive_summary": _EXEC_SUMMARY_PROFILE,
    "competencies": _T3_NON_EXEC,
    "unify_narrative": _T3_NON_EXEC,
    "unify_bullets": _T3_NON_EXEC,
    "ibm_narrative": _T2_QUALITY,
    "ibm_bullets": _T2_QUALITY,
}


def section_reasoning_profile(section_lane: str | None) -> SectionReasoningProfile:
    lane = str(section_lane or "").strip().lower()
    alias = {"ibm": "ibm_narrative"}.get(lane, lane)
    if alias in _lane_map:
        return _lane_map[alias]
    return _T2_QUALITY


def executive_summary_must_dominate_lesser_sections() -> None:
    es = profile_to_requested_kw(section_reasoning_profile("executive_summary"))
    head_kw = profile_to_requested_kw(section_reasoning_profile("headline"))
    assert float(es["self_consistency_samples"]) > float(head_kw["self_consistency_samples"])
    assert float(es["reflexion_loops"]) > float(head_kw["reflexion_loops"])

    lesser_lanes = ("ibm_bullets", "ibm_narrative", "education")
    for lane in lesser_lanes:
        ot = profile_to_requested_kw(section_reasoning_profile(lane))
        assert float(es["self_consistency_samples"]) > float(
            ot["self_consistency_samples"]
        ), f"exec summary needs higher self_consistency than {lane}"
        assert float(es["tot_branches"]) >= float(ot["tot_branches"]), lane
        assert float(es["reflexion_loops"]) >= float(ot["reflexion_loops"]), lane
    es_temp = float(es["temperature"])
    non_exec = profile_to_requested_kw(section_reasoning_profile("ibm_bullets"))
    assert es_temp >= float(non_exec["temperature"])


__all__ = [
    "ReasoningIntensityTier",
    "SectionReasoningProfile",
    "executive_summary_must_dominate_lesser_sections",
    "profile_to_requested_kw",
    "section_reasoning_profile",
]
