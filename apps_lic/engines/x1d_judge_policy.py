"""X1D judge profile and recipient-risk policy for apps_lic Exit."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping

import yaml

from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_REFERRAL_ASK,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
    MODIFIER_APPLICATION_STATUS_CLAIMED,
    MODIFIER_USES_COMPANY_TRIGGER,
    MODIFIER_USES_JD,
)
from apps_lic.engines.recipient_classification import (
    CLASS_CEO,
    CLASS_CTO,
    CLASS_C_LEVEL,
    CLASS_EXECUTIVE,
    CLASS_HIRING_MANAGER,
    CLASS_RECRUITER,
    CLASS_SENIOR_TA,
    CLASS_VP_ENG,
)


DEFAULT_X1D_JUDGE_MODEL = "Claude Sonnet 4.6"
DEFAULT_X1D_JUDGE_PROVIDER = "claude"
JUDGE_AVAILABLE = "available"
JUDGE_UNAVAILABLE = "unavailable"
INDEPENDENT_JUDGE = "independent_judge"
NON_INDEPENDENT_JUDGE = "non_independent_judge"
LIVE_CLAUDE_API_CALL = "live_claude_api_call"
ANTHROPIC_MESSAGES_API = "anthropic_messages_api"

JUDGE_LINKEDIN_TONE = "linkedin_tone_channel_quality_x1d"
JUDGE_LINKEDIN_TONE_NON_GENERIC = "linkedin_tone_non_generic_x1d"
JUDGE_EVIDENCE_SUPPORT = "evidence_claim_support_x1d"
JUDGE_CEO_ORIGINALITY = "ceo_attention_originality_x1d"
JUDGE_CEO_EVIDENCE_RISK = "ceo_evidence_overclaim_risk_x1d"

MODIFIER_PROVIDER_BACKED_GENERATION = "provider_backed_generation"
MODIFIER_SIMILARITY_GATE_FLAGGED = "similarity_gate_flagged"

TECHNICAL_PROOF_IDS = frozenset(
    {
        "sp_agentic_platform",
        "sp_runtime_reliability",
        "sp_cloud_ai_transformation",
    }
)

_VALIDATION_EXIT_CONFIG_PATH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "domain_contract"
    / "validation_exit.v1.yaml"
)


@dataclass(frozen=True)
class X1DJudgeProfilePolicy:
    judge_id: str
    rubric_id: str
    role: str
    threshold: float


def required_x1d_judge_ids_for_context(
    *,
    recipient_class: str,
    message_type: str,
    modifiers: Mapping[str, bool] | None = None,
    proof_ids: Iterable[str] = (),
) -> tuple[str, ...]:
    """Resolve the recipient/message-specific X1D judge policy."""
    modifier_map = dict(modifiers or {})
    recipient = _clean(recipient_class)
    message = _clean(message_type)
    proof_id_tuple = tuple(dict.fromkeys(_clean(item) for item in proof_ids if _clean(item)))
    uses_jd = message == MESSAGE_ROLE_SPECIFIC or bool(modifier_map.get(MODIFIER_USES_JD))
    uses_technical_proof = _uses_technical_proof(proof_id_tuple)
    uses_strategic_trigger = message == MESSAGE_TRIGGER_BASED_INSIGHT or bool(
        modifier_map.get(MODIFIER_USES_COMPANY_TRIGGER)
    )
    provider_backed = bool(modifier_map.get(MODIFIER_PROVIDER_BACKED_GENERATION))
    similarity_risk = bool(modifier_map.get(MODIFIER_SIMILARITY_GATE_FLAGGED))

    if recipient in {CLASS_CEO, CLASS_C_LEVEL, CLASS_CTO}:
        return (JUDGE_CEO_ORIGINALITY, JUDGE_CEO_EVIDENCE_RISK)

    judge_ids: list[str] = []
    if recipient in {CLASS_RECRUITER, CLASS_SENIOR_TA} and message == MESSAGE_ROLE_SPECIFIC:
        judge_ids.append(JUDGE_EVIDENCE_SUPPORT)
        if provider_backed or similarity_risk:
            judge_ids.append(JUDGE_LINKEDIN_TONE_NON_GENERIC)
        return tuple(dict.fromkeys(judge_ids))

    if recipient == CLASS_HIRING_MANAGER and message == MESSAGE_ROLE_SPECIFIC:
        return (JUDGE_EVIDENCE_SUPPORT, JUDGE_LINKEDIN_TONE_NON_GENERIC)

    if recipient == CLASS_HIRING_MANAGER and (uses_strategic_trigger or uses_technical_proof):
        return (JUDGE_EVIDENCE_SUPPORT, JUDGE_LINKEDIN_TONE_NON_GENERIC)

    if recipient in {CLASS_EXECUTIVE, CLASS_VP_ENG}:
        judge_ids.append(JUDGE_LINKEDIN_TONE)
        if uses_jd or uses_technical_proof or uses_strategic_trigger:
            judge_ids.append(JUDGE_EVIDENCE_SUPPORT)
        return tuple(dict.fromkeys(judge_ids))

    if message == MESSAGE_REFERRAL_ASK or modifier_map.get(MODIFIER_APPLICATION_STATUS_CLAIMED):
        return (JUDGE_EVIDENCE_SUPPORT,)
    if max(0, int(modifier_map.get("x1d_llm_judge_depth") or 0)) > 0:
        return (JUDGE_LINKEDIN_TONE,)
    return ()


@lru_cache(maxsize=1)
def x1d_judge_profile_policy() -> Mapping[str, X1DJudgeProfilePolicy]:
    """Load X1D judge profile policy from the validation-exit domain contract."""
    with _VALIDATION_EXIT_CONFIG_PATH.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    profiles = ((config.get("x1d") or {}).get("rubric_profiles") or {})
    if not isinstance(profiles, Mapping):
        raise ValueError("validation_exit.v1.yaml x1d.rubric_profiles must be a mapping")
    loaded: dict[str, X1DJudgeProfilePolicy] = {}
    for judge_id, raw_profile in profiles.items():
        profile = dict(raw_profile or {})
        rubric_id = _clean(profile.get("rubric_id"))
        role = _clean(profile.get("role"))
        try:
            threshold = float(profile.get("threshold"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid X1D judge threshold for {judge_id!r}") from exc
        if not rubric_id or not role:
            raise ValueError(f"Missing rubric_id or role for X1D judge profile {judge_id!r}")
        if threshold <= 0.0 or threshold > 1.0:
            raise ValueError(f"X1D judge threshold out of range for {judge_id!r}: {threshold}")
        loaded[str(judge_id)] = X1DJudgeProfilePolicy(
            judge_id=str(judge_id),
            rubric_id=rubric_id,
            role=role,
            threshold=threshold,
        )
    required = {
        JUDGE_CEO_ORIGINALITY,
        JUDGE_CEO_EVIDENCE_RISK,
        JUDGE_EVIDENCE_SUPPORT,
        JUDGE_LINKEDIN_TONE_NON_GENERIC,
        JUDGE_LINKEDIN_TONE,
    }
    missing = sorted(required.difference(loaded))
    if missing:
        raise ValueError(f"Missing X1D judge profiles in validation_exit.v1.yaml: {missing}")
    return loaded


def _uses_technical_proof(proof_ids: Iterable[str]) -> bool:
    return bool({item for item in proof_ids if _clean(item)} & TECHNICAL_PROOF_IDS)


def _clean(value: object) -> str:
    return str(value or "").strip()
