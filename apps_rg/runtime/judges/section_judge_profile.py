"""Section-tier proof judge model resolution (apps_rg only)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

from agentic_core.L0_routing.config.model_catalog import (
    GEMINI_20_FLASH_MODEL_ID,
    OPENAI_GPT3_MODEL_ID,
    OPENAI_GPT4O_MINI_MODEL_ID,
    OPENAI_GPT4O_MODEL_ID,
    OPENAI_NON_CHAT_COMPLETIONS_MODELS,
)

from pathlib import Path

from apps_rg.runtime.section_judge_policy import JudgeTier, get_section_judge_policy, normalize_section_id
from apps_rg.runtime.section_model_limits import runtime_limit_str

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
    except ImportError as exc:  # guardian: strict SSOT load; caller must see the broken source
        raise SectionJudgeProfileSSOTError(f"Cannot load apps_rg judge-model SSOT: {_PROVIDER_PROFILES_PATH}") from exc
    except (AttributeError, OSError, TypeError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        raise SectionJudgeProfileSSOTError(f"Cannot load apps_rg judge-model SSOT: {_PROVIDER_PROFILES_PATH}") from exc
    if not isinstance(jm, dict):
        raise SectionJudgeProfileSSOTError(f"Invalid judge_models block in {_PROVIDER_PROFILES_PATH}")
    return jm


def _tier_yaml_label(tier: JudgeTier) -> str:
    return "enhanced" if tier == JudgeTier.ENHANCED_REASONING else "standard"

_FORBIDDEN_PROOF_MODEL_RE = re.compile(
    r"(?:^|[/_-])(flash|mini|haiku)(?:[/_-]|$)|"
    rf"{re.escape(GEMINI_20_FLASH_MODEL_ID)}|"
    r"gemini-[1]\.|"
    rf"{re.escape(OPENAI_GPT4O_MINI_MODEL_ID)}|"
    rf"{re.escape(OPENAI_GPT3_MODEL_ID)}(?:\.|$|-|/)|"
    rf"(?:^|/){re.escape(OPENAI_GPT4O_MODEL_ID)}$",
    re.IGNORECASE,
)

# OpenAI ids that reject v1/chat/completions (completions-only product SKUs).
_OPENAI_NON_CHAT_COMPLETIONS_MODELS = OPENAI_NON_CHAT_COMPLETIONS_MODELS


def openai_chat_completions_eligible(model_id: str) -> bool:
    """False when the model id is known to fail chat/completions (judge transport)."""
    return str(model_id or "").strip().lower() not in _OPENAI_NON_CHAT_COMPLETIONS_MODELS

_SUPPORTED_PROVIDER_KEYS = frozenset({"gemini_pro", "openai_chatgpt", "anthropic_claude"})
_ENHANCED_PROFILE = {provider_key: {} for provider_key in _SUPPORTED_PROVIDER_KEYS}
_STANDARD_PROFILE = {provider_key: {} for provider_key in _SUPPORTED_PROVIDER_KEYS}


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
    _ = environ
    sid = normalize_section_id(section_id)
    policy = get_section_judge_policy(sid)
    tier = policy.judge_tier
    if provider_key not in _SUPPORTED_PROVIDER_KEYS:
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
    if provider_key not in policy.required_judge_providers:
        return SectionJudgeModelResolution(
            provider_key=provider_key,
            section_id=sid,
            judge_tier=tier.value,
            model_requested="",
            model_actual="",
            model_source="not_section_proof_provider",
            model_tier="advisory_or_blocked",
            blocked=True,
            block_reason=(
                f"Provider {provider_key} is not a proof judge for section={sid}; "
                "selector/advisory providers cannot satisfy X1D proof."
            ),
            advisory_only=True,
            proof_eligible_judge=False,
        )

    yaml_tier = _yaml_judge_models().get(_tier_yaml_label(tier)) or {}
    yaml_model = yaml_tier.get(provider_key) if isinstance(yaml_tier, dict) else None
    if not yaml_model:
        raise SectionJudgeProfileSSOTError(
            f"Missing judge_models.{_tier_yaml_label(tier)}.{provider_key} in {_PROVIDER_PROFILES_PATH}"
        )
    candidates: list[tuple[str, str]] = [(str(yaml_model), "yaml_judge_models")]

    reasoning_effort: str | None = None
    if provider_key == "openai_chatgpt" and tier == JudgeTier.ENHANCED_REASONING:
        reasoning_effort = runtime_limit_str("judge.openai_enhanced_reasoning_effort")

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
            f"tier={tier.value}. Set provider_profiles.yaml judge_models; "
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
