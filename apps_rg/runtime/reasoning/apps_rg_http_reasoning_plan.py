"""Build ReasoningExecutionPlan for apps_rg singleton HTTP lanes.

IBM-style lanes (tier **T2**) soften orchestration **QUALITY_REQUIRED** and **reflexion POLICY_REQUIRED**
to **OPTIONAL** so singleton HTTP receipts stay honest without spurious aggregate BLOCK from deferred loops.

Executive summary and other **T3** critical lanes preserve full Sovereign QUALITY semantics.
**T1_SIMPLE_REWRITE** exists only as a reserved enum tier — **no `_reasoning_section_lane` bind yet**,
so singleton softening applies only where `SectionReasoningProfile.tier == T2_QUALITY_SECTION`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from agentic_core.runtime.reasoning.reasoning_control_requirement import AllowedSurface, RequirementLevel
from agentic_core.runtime.reasoning.reasoning_control_resolver import canonical_plan_digest, default_gateway_control_requirements
from agentic_core.runtime.reasoning.reasoning_execution_plan import ReasoningExecutionPlan

from apps_rg.runtime.reasoning.section_reasoning_intensity import ReasoningIntensityTier, SectionReasoningProfile


def _coerce_requested_values(src: Mapping[str, Any]) -> dict[str, float | int | str | bool | None]:
    casted: dict[str, float | int | str | bool | None] = {}
    for k, v in src.items():
        casted[k] = v  # type: ignore[assignment]
    return casted


def build_apps_rg_http_reasoning_plan(
    *,
    merged_requested_kw: Mapping[str, Any],
    profile: SectionReasoningProfile,
) -> ReasoningExecutionPlan:
    kw = dict(merged_requested_kw)
    reqs = tuple(default_gateway_control_requirements(kw))

    if profile.executive_lane or profile.tier in (
        ReasoningIntensityTier.T0_LOCKED_FACT,
        ReasoningIntensityTier.T3_CRITICAL_SECTION,
    ):
        resolved = reqs
    elif profile.tier is ReasoningIntensityTier.T2_QUALITY_SECTION:
        softened: list[Any] = []
        for req in reqs:
            if req.control_name == "reflexion_loops" and req.requirement_level == RequirementLevel.POLICY_REQUIRED:
                softened.append(replace(req, requirement_level=RequirementLevel.OPTIONAL))
            elif req.allowed_surfaces == frozenset({AllowedSurface.ORCHESTRATION}) and req.requirement_level == RequirementLevel.QUALITY_REQUIRED:
                softened.append(replace(req, requirement_level=RequirementLevel.OPTIONAL))
            else:
                softened.append(req)
        resolved = tuple(softened)
    else:
        resolved = reqs

    digest = canonical_plan_digest({k: kw[k] for k in sorted(kw)})
    return ReasoningExecutionPlan(
        plan_digest=digest,
        control_requirements=resolved,
        requested_values=_coerce_requested_values(kw),
    )


__all__ = ["build_apps_rg_http_reasoning_plan"]