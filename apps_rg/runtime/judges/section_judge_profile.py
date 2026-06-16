"""Section-tier proof judge model resolution (apps_rg only)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Mapping

from agentic_core.config.google_ai_env import google_ai_pro_model_id
from agentic_core.L0_routing.config.model_catalog import (
    OPENAI_NON_CHAT_COMPLETIONS_MODELS,
)

from pathlib import Path

from apps_rg.runtime.section_judge_policy import JudgeTier, get_section_judge_policy, normalize_section_id

# Provider-profiles SSOT (apps_rg/config/provider_profiles.yaml). This module lives at
# apps_rg/runtime/judges/, so parents[2] == apps_rg. The YAML ``judge_models`` block is the
# SSOT-of-record for per-tier judge models.
_PROVIDER_PROFILES_PATH = Path(__file__).resolve().parents[2] / "config" / "provider_profiles.yaml"


class SectionJudgeProfileSSOTError(RuntimeError):
    """Raised when apps_rg judge-model SSOT cannot be loaded."""


def _yaml_judge_models() -> dict:
    """Per-tier judge models from provider_profiles.yaml ``judge_models``."""
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(_PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
        jm = (data or {}).get("judge_models") or {}
    except Exception as exc:  # guardian: strict SSOT load; caller must see the broken source
        raise SectionJudgeProfileSSOTError(f"Cannot load apps_rg judge-model SSOT: {_PROVIDER_PROFILES_PATH}") from exc
    if not isinstance(jm, dict):
        raise SectionJudgeProfileSSOTError(f"Invalid judge_models block in {_PROVIDER_PROFILES_PATH}")
    return jm


def _tier_yaml_label(tier: JudgeTier) -> str:
    return "enhanced" if tier == JudgeTier.ENHANCED_REASONING else "standard"

_FORBIDDEN_PROOF_MODEL_RE = re.compile(
    r"(?:^|[/_-])(flash|mini|haiku)(?:[/_-]|$)|"
    r"gemini-2\.0-flash|gemini-1\.|gpt-4o-mini|gpt-3(?:\.|$|-|/)|(?:^|/)gpt-4o$",
    re.IGNORECASE,
)

# OpenAI ids that reject v1/chat/completions (completions-only product SKUs).
_OPENAI_NON_CHAT_COMPLETIONS_MODELS = OPENAI_NON_CHAT_COMPLETIONS_MODELS


def openai_chat_completions_eligible(model_id: str) -> bool:
    """False when the model id is known to fail chat/completions (judge transport)."""
    return str(model_id or "").strip().lower() not in _OPENAI_NON_CHAT_COMPLETIONS_MODELS

_ENHANCED_PROFILE: dict[str, dict[str, Any]] = {
    "gemini_pro": {
        "env_primary": (
            "APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED",
            "APPS_RG_GOOGLE_JUDGE_MODEL",
            "APPS_RG_GEMINI_JUDGE_MODEL",
        ),
        "env_tier": (),
    },
    "openai_chatgpt": {
        "env_primary": (
            "APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED",
            "APPS_RG_OPENAI_JUDGE_MODEL",
        ),
        "env_tier": (),
        "reasoning_effort_env": "APPS_RG_OPENAI_JUDGE_REASONING_EFFORT",
        "default_reasoning_effort": "high",
    },
    "anthropic_claude": {
        "env_primary": (
            "APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED",
            "APPS_RG_ANTHROPIC_JUDGE_MODEL",
        ),
        "env_tier": (),
    },
}

_STANDARD_PROFILE: dict[str, dict[str, Any]] = {
    "gemini_pro": {
        "env_primary": (
            "APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD",
            "APPS_RG_GOOGLE_JUDGE_MODEL",
            "APPS_RG_GEMINI_JUDGE_MODEL",
        ),
        "env_tier": ("GOOGLE_AI_PRO_MODEL",),
    },
    "openai_chatgpt": {
        "env_primary": (
            "APPS_RG_OPENAI_JUDGE_MODEL_STANDARD",
            "APPS_RG_OPENAI_JUDGE_MODEL",
        ),
        "env_tier": (),
    },
    "anthropic_claude": {
        "env_primary": (
            "APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD",
            "APPS_RG_ANTHROPIC_JUDGE_MODEL",
        ),
        "env_tier": (),
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
    if provider_key == "gemini_pro" and tier != JudgeTier.ENHANCED_REASONING:
        pro_id, pro_src = google_ai_pro_model_id(env)
        if pro_id and not any(c[0] == pro_id for c in candidates):
            candidates.append((pro_id, pro_src or "profile_default"))
    yaml_tier = _yaml_judge_models().get(_tier_yaml_label(tier)) or {}
    yaml_model = yaml_tier.get(provider_key) if isinstance(yaml_tier, dict) else None
    if not yaml_model:
        raise SectionJudgeProfileSSOTError(
            f"Missing judge_models.{_tier_yaml_label(tier)}.{provider_key} in {_PROVIDER_PROFILES_PATH}"
        )
    if not any(c[0] == str(yaml_model) for c in candidates):
        candidates.append((str(yaml_model), "yaml_judge_models"))

    reasoning_effort: str | None = None
    if provider_key == "openai_chatgpt" and tier == JudgeTier.ENHANCED_REASONING:
        effort_env = str(profile.get("reasoning_effort_env") or "APPS_RG_OPENAI_JUDGE_REASONING_EFFORT")
        reasoning_effort = (
            str(env.get(effort_env) or "").strip()
            or str(profile.get("default_reasoning_effort") or "high")
        )

    for model_id, source in candidates:
        forbidden = is_forbidden_proof_judge_model(model_id)
        if provider_key == "openai_chatgpt" and not openai_chat_completions_eligible(model_id):
            continue
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
            f"tier={tier.value}. Set env overrides or provider_profiles.yaml judge_models; "
            "flash/mini/haiku are advisory-only."
        ),
        proof_eligible_judge=False,
    )


__all__ = [
    "SectionJudgeModelResolution",
    "SectionJudgeProfileSSOTError",
    "is_forbidden_proof_judge_model",
    "openai_chat_completions_eligible",
    "resolve_section_proof_judge_model",
]
