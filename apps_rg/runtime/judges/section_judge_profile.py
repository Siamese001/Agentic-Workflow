"""Section-tier proof judge model resolution (apps_rg only)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.config.google_ai_env import google_ai_pro_model_id

from apps_rg.runtime.section_judge_policy import JudgeTier, get_section_judge_policy, normalize_section_id

_FORBIDDEN_PROOF_MODEL_RE = re.compile(
    r"(?:^|[/_-])(flash|mini|haiku)(?:[/_-]|$)|"
    r"gemini-2\.0-flash|gemini-1\.|gpt-4o-mini|gpt-3(?:\.|$|-|/)|(?:^|/)gpt-4o$",
    re.IGNORECASE,
)

_ENHANCED_PROFILE: dict[str, dict[str, Any]] = {
    "gemini_pro": {
        "env_primary": ("APPS_RG_GOOGLE_JUDGE_MODEL", "APPS_RG_GEMINI_JUDGE_MODEL"),
        "env_tier": ("GOOGLE_AI_PRO_MODEL",),
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

_STANDARD_PROFILE: dict[str, dict[str, Any]] = {
    "gemini_pro": {
        "env_primary": ("APPS_RG_GOOGLE_JUDGE_MODEL", "APPS_RG_GEMINI_JUDGE_MODEL"),
        "env_tier": ("GOOGLE_AI_PRO_MODEL",),
        "profile_defaults": ("gemini-2.5-pro", "gemini-3.1-pro-preview"),
    },
    "openai_chatgpt": {
        "env_primary": ("APPS_RG_OPENAI_JUDGE_MODEL",),
        "env_tier": ("OPENAI_MODEL",),
        "profile_defaults": ("gpt-5.5", "gpt-5.4"),
    },
    "anthropic_claude": {
        "env_primary": ("APPS_RG_ANTHROPIC_JUDGE_MODEL",),
        "env_tier": ("ANTHROPIC_MODEL",),
        "profile_defaults": ("claude-sonnet-4-6", "claude-sonnet-4-5"),
    },
}


@dataclass(frozen=True)
class SectionJudgeModelResolution:
    provider_key: str
    section_id: str
    judge_tier: str
    model_requested: str
    model_actual: str
    model_source: str
    model_tier: str
    reasoning_effort: str | None = None
    blocked: bool = False
    block_reason: str | None = None
    advisory_only: bool = False
    proof_eligible_judge: bool = False
    fallback_used: bool = False


def is_forbidden_proof_judge_model(model_id: str) -> bool:
    mid = (model_id or "").strip()
    if not mid:
        return True
    return bool(_FORBIDDEN_PROOF_MODEL_RE.search(mid))


def _profile_for_tier(tier: JudgeTier) -> dict[str, dict[str, Any]]:
    if tier in (JudgeTier.ENHANCED_REASONING,):
        return _ENHANCED_PROFILE
    return _STANDARD_PROFILE


def _model_tier_label(tier: JudgeTier, model_id: str) -> str:
    if is_forbidden_proof_judge_model(model_id):
        return "advisory_weak"
    if tier == JudgeTier.ENHANCED_REASONING:
        return "enhanced_reasoning"
    if tier == JudgeTier.BULLET_REWRITE_QUALITY:
        return "bullet_rewrite_quality"
    if tier == JudgeTier.STANDARD_REASONING:
        return "standard_reasoning"
    return "advisory_taxonomy"


def resolve_section_proof_judge_model(
    section_id: str,
    provider_key: str,
    environ: Mapping[str, str] | None = None,
) -> SectionJudgeModelResolution:
    """Resolve proof judge model for a section; fail closed on missing or weak tiers."""
    env = dict(os.environ if environ is None else environ)
    sid = normalize_section_id(section_id)
    policy = get_section_judge_policy(sid)
    tier = policy.judge_tier
    profile = _profile_for_tier(tier).get(provider_key)
    if not profile:
        return SectionJudgeModelResolution(
            provider_key=provider_key,
            section_id=sid,
            judge_tier=tier.value,
            model_requested="",
            model_actual="",
            model_source="unknown_provider",
            model_tier="unknown",
            blocked=True,
            block_reason=f"Unknown judge provider key: {provider_key}",
            proof_eligible_judge=False,
        )

    candidates: list[tuple[str, str]] = []
    for name in profile.get("env_primary") or ():
        raw = str(env.get(name) or "").strip()
        if raw:
            candidates.append((raw, name))
    for name in profile.get("env_tier") or ():
        raw = str(env.get(name) or "").strip()
        if raw:
            candidates.append((raw, name))
    if provider_key == "gemini_pro":
        pro_id, pro_src = google_ai_pro_model_id(env)
        if pro_id and not any(c[0] == pro_id for c in candidates):
            candidates.append((pro_id, pro_src or "GOOGLE_AI_PRO_MODEL"))
    for default in profile.get("profile_defaults") or ():
        candidates.append((str(default), "profile_default"))

    reasoning_effort: str | None = None
    if provider_key == "openai_chatgpt" and tier == JudgeTier.ENHANCED_REASONING:
        effort_env = str(profile.get("reasoning_effort_env") or "APPS_RG_OPENAI_JUDGE_REASONING_EFFORT")
        reasoning_effort = (
            str(env.get(effort_env) or "").strip()
            or str(profile.get("default_reasoning_effort") or "high")
        )

    for model_id, source in candidates:
        forbidden = is_forbidden_proof_judge_model(model_id)
        mt = _model_tier_label(tier, model_id)
        if forbidden:
            continue
        proof_eligible = policy.judge_required_for_proof and not forbidden
        return SectionJudgeModelResolution(
            provider_key=provider_key,
            section_id=sid,
            judge_tier=tier.value,
            model_requested=model_id,
            model_actual=model_id,
            model_source=source,
            model_tier=mt,
            reasoning_effort=reasoning_effort,
            blocked=False,
            advisory_only=not policy.judge_required_for_proof,
            proof_eligible_judge=proof_eligible,
        )

    return SectionJudgeModelResolution(
        provider_key=provider_key,
        section_id=sid,
        judge_tier=tier.value,
        model_requested="",
        model_actual="",
        model_source="none_allowed",
        model_tier="blocked",
        blocked=True,
        block_reason=(
            f"No proof-eligible judge model configured for section={sid} provider={provider_key} "
            f"tier={tier.value}. Set env overrides or profile defaults; flash/mini/haiku are advisory-only."
        ),
        proof_eligible_judge=False,
    )


__all__ = [
    "SectionJudgeModelResolution",
    "is_forbidden_proof_judge_model",
    "resolve_section_proof_judge_model",
]
