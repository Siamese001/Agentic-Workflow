"""Enhanced X1D judge model profile for executive_summary (re-exports section_judge_profile)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from apps_rg.runtime.judges.section_judge_profile import (
    is_forbidden_proof_judge_model,
    resolve_section_proof_judge_model,
)

EXECUTIVE_SUMMARY_ENHANCED_MODEL_PROFILE = {
    "gemini_pro": {
        "env_primary": ("APPS_RG_GOOGLE_JUDGE_MODEL", "APPS_RG_GEMINI_JUDGE_MODEL"),
        "env_tier": ("GOOGLE_AI_PRO_MODEL", "GEMINI_PRO_MODEL"),
        "profile_defaults": ("gemini-3.1-pro-preview", "gemini-2.5-pro"),
    },
    "openai_chatgpt": {
        "env_primary": ("APPS_RG_OPENAI_JUDGE_MODEL",),
        "env_tier": ("OPENAI_MODEL",),
        "profile_defaults": ("gpt-5.5-pro", "gpt-5.5", "gpt-5.4"),
        "reasoning_effort_env": "APPS_RG_OPENAI_JUDGE_REASONING_EFFORT",
        "default_reasoning_effort": "high",
    },
    "anthropic_claude": {
        "env_primary": ("APPS_RG_ANTHROPIC_JUDGE_MODEL",),
        "env_tier": ("ANTHROPIC_MODEL",),
        "profile_defaults": ("claude-opus-4-6", "claude-opus-4-5", "claude-sonnet-4-6"),
    },
}


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
    "EXECUTIVE_SUMMARY_ENHANCED_MODEL_PROFILE",
    "ExecutiveSummaryJudgeModelResolution",
    "is_forbidden_proof_judge_model",
    "resolve_executive_summary_proof_judge_model",
]
