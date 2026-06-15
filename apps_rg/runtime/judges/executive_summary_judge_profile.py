"""Enhanced X1D judge model profile for executive_summary (re-exports section_judge_profile)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from apps_rg.runtime.judges.section_judge_profile import (
    is_forbidden_proof_judge_model,
    resolve_section_proof_judge_model,
)

# NOTE: the enhanced judge-model profile for executive_summary is NOT redefined here. The single
# SSOT is provider_profiles.yaml judge_models + section_judge_profile._ENHANCED_PROFILE, resolved by
# resolve_section_proof_judge_model below. A previously-duplicated EXECUTIVE_SUMMARY_ENHANCED_MODEL_PROFILE
# dict (zero consumers, drifted from the SSOT) was removed to keep one source of truth.


@dataclass(frozen=True)
class ExecutiveSummaryJudgeModelResolution:
    provider_key: str
    model_requested: str
    model_actual: str
    model_source: str
    reasoning_effort: str | None = None
    blocked: bool = False
    block_reason: str | None = None
    advisory_only: bool = False


def resolve_executive_summary_proof_judge_model(
    provider_key: str,
    environ: Mapping[str, str] | None = None,
) -> ExecutiveSummaryJudgeModelResolution:
    r = resolve_section_proof_judge_model("executive_summary", provider_key, environ)
    return ExecutiveSummaryJudgeModelResolution(
        provider_key=r.provider_key,
        model_requested=r.model_requested,
        model_actual=r.model_actual,
        model_source=r.model_source,
        reasoning_effort=r.reasoning_effort,
        blocked=r.blocked,
        block_reason=r.block_reason,
        advisory_only=r.advisory_only,
    )


__all__ = [
    "ExecutiveSummaryJudgeModelResolution",
    "is_forbidden_proof_judge_model",
    "resolve_executive_summary_proof_judge_model",
]
