"""Canonical apps_rg section judge policy matrix (apps_rg only; no agentic_core)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, FrozenSet, Mapping

from apps_rg.runtime.section_model_limits import runtime_limit_mapping


class GeneratorModelClass(str, Enum):
    # PROVIDER_MODEL/external model was removed from proof-bearing lane generation; real lanes use an
    # external provider selected by the per-section provider matrix.
    EXTERNAL_CLAUDE = "EXTERNAL_CLAUDE"
    EXTERNAL_OPENAI = "EXTERNAL_OPENAI"
    AGGREGATOR = "AGGREGATOR"


class JudgeTier(str, Enum):
    ENHANCED_REASONING = "ENHANCED_REASONING"
    STANDARD_REASONING = "STANDARD_REASONING"
    BULLET_REWRITE_QUALITY = "BULLET_REWRITE_QUALITY"
    OPTIONAL_ADVISORY_TAXONOMY_ONLY = "OPTIONAL_ADVISORY_TAXONOMY_ONLY"


@dataclass(frozen=True)
class JudgeRuntimeProfile:
    judge_weight: int
    max_output_tokens: int
    max_output_tokens_hard_cap: int
    max_attempts: int
    retry_backoff_base_seconds: float
    retry_backoff_max_seconds: float

    def resolved_max_output_tokens(self, *, attempt: int = 1) -> int:
        return min(self.max_output_tokens_hard_cap, self.max_output_tokens * min(max(1, attempt), 2))

    def resolved_retry_backoff_seconds(self, *, attempt: int) -> float:
        return min(
            self.retry_backoff_max_seconds,
            self.retry_backoff_base_seconds * (2 ** max(0, attempt - 1)),
        )


class FallbackPolicy(str, Enum):
    FAIL_CLOSED = "FAIL_CLOSED"


class SectionJudgePolicySSOTError(RuntimeError):
    """Raised when the section judge policy SSOT is missing or malformed."""


@dataclass(frozen=True)
class SectionJudgePolicy:
    section_name: str
    generator_model_class: GeneratorModelClass
    judge_required_for_proof: bool
    judge_tier: JudgeTier
    required_judge_providers: tuple[str, ...]
    proof_eligible_model_classes: FrozenSet[str]
    advisory_model_classes: FrozenSet[str]
    judge_packet_required: bool
    grade_only_required: bool
    replacement_generation_allowed: bool
    fallback_policy: FallbackPolicy = FallbackPolicy.FAIL_CLOSED

    @property
    def judge_runtime_profile(self) -> JudgeRuntimeProfile:
        return get_judge_runtime_profile(self.judge_tier)

    @property
    def x1d_required_for_x3_allow(self) -> bool:
        """Whether X3 may ALLOW only after required proof judges pass."""
        return self.judge_required_for_proof


# Default judges are calibrated against the per-section generator matrix, not a single global
# generator. Claude-backed lanes never use anthropic_claude as their default judge; competencies
# uses OpenAI as its required proof judge. Recalibrated 2026-06-08 from the older 3-provider
# PROVIDER_MODEL-era panel. See .codex/rules/judge-calibration-cadence.md.
_DUAL_JUDGE_PANEL: tuple[str, ...] = ("gemini_pro", "openai_chatgpt")
_SINGLE_JUDGE_PANEL: tuple[str, ...] = ("gemini_pro",)
_COMPETENCIES_JUDGE_PANEL: tuple[str, ...] = ("openai_chatgpt",)

REQUIRED_JUDGE_PROVIDER_KEYS: tuple[str, ...] = _DUAL_JUDGE_PANEL

_TIER_RUNTIME_PROFILE_KEY: dict[JudgeTier, str] = {
    JudgeTier.ENHANCED_REASONING: "enhanced_reasoning",
    JudgeTier.STANDARD_REASONING: "standard_reasoning",
    JudgeTier.BULLET_REWRITE_QUALITY: "bullet_rewrite_quality",
    JudgeTier.OPTIONAL_ADVISORY_TAXONOMY_ONLY: "optional_advisory_taxonomy_only",
}


def _parse_judge_runtime_profile(profile_key: str, raw: Mapping[str, Any]) -> JudgeRuntimeProfile:
    try:
        profile = JudgeRuntimeProfile(
            judge_weight=int(raw["judge_weight"]),
            max_output_tokens=int(raw["max_output_tokens"]),
            max_output_tokens_hard_cap=int(raw["max_output_tokens_hard_cap"]),
            max_attempts=int(raw["max_attempts"]),
            retry_backoff_base_seconds=float(raw["retry_backoff_base_seconds"]),
            retry_backoff_max_seconds=float(raw["retry_backoff_max_seconds"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SectionJudgePolicySSOTError(f"Invalid judge runtime profile: {profile_key}") from exc

    if profile.judge_weight < 1:
        raise SectionJudgePolicySSOTError(f"judge runtime profile {profile_key} must have judge_weight >= 1")
    if profile.max_output_tokens < 1:
        raise SectionJudgePolicySSOTError(f"judge runtime profile {profile_key} must have max_output_tokens >= 1")
    if profile.max_output_tokens_hard_cap < profile.max_output_tokens:
        raise SectionJudgePolicySSOTError(
            f"judge runtime profile {profile_key} hard cap must be >= max_output_tokens"
        )
    if profile.max_attempts < 1:
        raise SectionJudgePolicySSOTError(f"judge runtime profile {profile_key} must have max_attempts >= 1")
    if profile.retry_backoff_base_seconds < 0.0:
        raise SectionJudgePolicySSOTError(
            f"judge runtime profile {profile_key} must have non-negative retry_backoff_base_seconds"
        )
    if profile.retry_backoff_max_seconds < profile.retry_backoff_base_seconds:
        raise SectionJudgePolicySSOTError(
            f"judge runtime profile {profile_key} backoff max must be >= backoff base"
        )
    return profile


def _load_judge_runtime_profiles() -> dict[JudgeTier, JudgeRuntimeProfile]:
    raw_profiles = runtime_limit_mapping("judge.runtime_profiles")
    out: dict[JudgeTier, JudgeRuntimeProfile] = {}
    for tier, profile_key in _TIER_RUNTIME_PROFILE_KEY.items():
        raw = raw_profiles.get(profile_key)
        if not isinstance(raw, dict):
            raise SectionJudgePolicySSOTError(
                f"Missing judge.runtime_profiles.{profile_key} in provider profile SSOT"
            )
        out[tier] = _parse_judge_runtime_profile(profile_key, raw)

    standard = out[JudgeTier.STANDARD_REASONING]
    bullets = out[JudgeTier.BULLET_REWRITE_QUALITY]
    if standard != bullets:
        raise SectionJudgePolicySSOTError(
            "standard_reasoning and bullet_rewrite_quality runtime profiles must stay in sync"
        )
    advisory = out[JudgeTier.OPTIONAL_ADVISORY_TAXONOMY_ONLY]
    enhanced = out[JudgeTier.ENHANCED_REASONING]
    if not (
        advisory.max_output_tokens <= standard.max_output_tokens <= enhanced.max_output_tokens
        and advisory.max_output_tokens_hard_cap <= standard.max_output_tokens_hard_cap <= enhanced.max_output_tokens_hard_cap
        and advisory.max_attempts <= standard.max_attempts <= enhanced.max_attempts
        and advisory.judge_weight <= standard.judge_weight <= enhanced.judge_weight
        and advisory.retry_backoff_base_seconds <= standard.retry_backoff_base_seconds <= enhanced.retry_backoff_base_seconds
        and advisory.retry_backoff_max_seconds <= standard.retry_backoff_max_seconds <= enhanced.retry_backoff_max_seconds
    ):
        raise SectionJudgePolicySSOTError(
            "judge runtime profiles must be monotonic from advisory -> standard -> enhanced"
        )
    return out


_JUDGE_RUNTIME_PROFILES: dict[JudgeTier, JudgeRuntimeProfile] = _load_judge_runtime_profiles()


def get_judge_runtime_profile(tier: JudgeTier) -> JudgeRuntimeProfile:
    return _JUDGE_RUNTIME_PROFILES[tier]


def _enhanced_providers() -> tuple[str, ...]:
    # executive_summary + final_aggregate_resume: dual cross-provider (both must pass).
    return _DUAL_JUDGE_PANEL


def _standard_providers() -> tuple[str, ...]:
    # bullets + narratives: single cross-provider backstop — the deterministic C0.3 graph + X2
    # lineage gates carry the proof; the judge is a light independent check, not the proof itself.
    return _SINGLE_JUDGE_PANEL


_SECTION_POLICIES: dict[str, SectionJudgePolicy] = {
    "executive_summary": SectionJudgePolicy(
        section_name="executive_summary",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.ENHANCED_REASONING,
        required_judge_providers=_enhanced_providers(),
        proof_eligible_model_classes=frozenset({"enhanced_frontier", "enhanced_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "headline": SectionJudgePolicy(
        section_name="headline",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.STANDARD_REASONING,
        required_judge_providers=_DUAL_JUDGE_PANEL,
        proof_eligible_model_classes=frozenset({"standard_frontier", "standard_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "unify_bullets": SectionJudgePolicy(
        section_name="unify_bullets",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.BULLET_REWRITE_QUALITY,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "bullet_rewrite_quality"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "ibm_bullets": SectionJudgePolicy(
        section_name="ibm_bullets",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.BULLET_REWRITE_QUALITY,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "bullet_rewrite_quality"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "insurtech_bullets": SectionJudgePolicy(
        section_name="insurtech_bullets",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.BULLET_REWRITE_QUALITY,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "bullet_rewrite_quality"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "ey_bullets": SectionJudgePolicy(
        section_name="ey_bullets",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.BULLET_REWRITE_QUALITY,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "bullet_rewrite_quality"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "unify_narrative": SectionJudgePolicy(
        section_name="unify_narrative",
        generator_model_class=GeneratorModelClass.EXTERNAL_OPENAI,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.STANDARD_REASONING,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "standard_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "ibm_narrative": SectionJudgePolicy(
        section_name="ibm_narrative",
        generator_model_class=GeneratorModelClass.EXTERNAL_OPENAI,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.STANDARD_REASONING,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "standard_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "insurtech_narrative": SectionJudgePolicy(
        section_name="insurtech_narrative",
        generator_model_class=GeneratorModelClass.EXTERNAL_OPENAI,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.STANDARD_REASONING,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "standard_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "ey_narrative": SectionJudgePolicy(
        section_name="ey_narrative",
        generator_model_class=GeneratorModelClass.EXTERNAL_OPENAI,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.STANDARD_REASONING,
        required_judge_providers=_standard_providers(),
        proof_eligible_model_classes=frozenset({"standard_frontier", "standard_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "competencies": SectionJudgePolicy(
        section_name="competencies",
        generator_model_class=GeneratorModelClass.EXTERNAL_CLAUDE,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.STANDARD_REASONING,
        required_judge_providers=_COMPETENCIES_JUDGE_PANEL,
        proof_eligible_model_classes=frozenset({"standard_frontier", "standard_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "final_aggregate_resume": SectionJudgePolicy(
        section_name="final_aggregate_resume",
        generator_model_class=GeneratorModelClass.AGGREGATOR,
        judge_required_for_proof=True,
        judge_tier=JudgeTier.ENHANCED_REASONING,
        required_judge_providers=_enhanced_providers(),
        proof_eligible_model_classes=frozenset({"enhanced_frontier", "enhanced_reasoning"}),
        advisory_model_classes=frozenset({"flash", "mini", "haiku", "advisory", "mock", "stub"}),
        judge_packet_required=True,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
}

_SECTION_ID_NORMALIZATION_MAP: dict[str, str] = {
    # The full-resume coherence runner resolves through the final-aggregate resume policy.
    "full_resume_coherence": "final_aggregate_resume",
}


def normalize_section_id(section_id: str) -> str:
    sid = (section_id or "").strip().lower().replace("-", "_")
    return _SECTION_ID_NORMALIZATION_MAP.get(sid, sid)


def get_section_judge_policy(section_id: str) -> SectionJudgePolicy:
    sid = normalize_section_id(section_id)
    policy = _SECTION_POLICIES.get(sid)
    if policy is None:
        raise KeyError(f"Unknown apps_rg section for judge policy: {section_id!r}")
    return policy


def all_canonical_section_policies() -> dict[str, SectionJudgePolicy]:
    """Return the canonical section policy matrix."""
    return dict(_SECTION_POLICIES)


def policy_matrix_export() -> dict[str, dict[str, Any]]:
    """Serializable matrix for tests and proof bundles."""
    out: dict[str, dict[str, Any]] = {}
    for sid, p in all_canonical_section_policies().items():
        rp = p.judge_runtime_profile
        out[sid] = {
            "section_name": p.section_name,
            "generator_model_class": p.generator_model_class.value,
            "judge_required_for_proof": p.judge_required_for_proof,
            "judge_tier": p.judge_tier.value,
            "required_judge_providers": list(p.required_judge_providers),
            "judge_runtime_profile": {
                "judge_weight": rp.judge_weight,
                "max_output_tokens": rp.max_output_tokens,
                "max_output_tokens_hard_cap": rp.max_output_tokens_hard_cap,
                "max_attempts": rp.max_attempts,
                "retry_backoff_base_seconds": rp.retry_backoff_base_seconds,
                "retry_backoff_max_seconds": rp.retry_backoff_max_seconds,
            },
            "judge_packet_required": p.judge_packet_required,
            "grade_only_required": p.grade_only_required,
            "replacement_generation_allowed": p.replacement_generation_allowed,
            "fallback_policy": p.fallback_policy.value,
        }
    return out


__all__ = [
    "FallbackPolicy",
    "GeneratorModelClass",
    "JudgeTier",
    "JudgeRuntimeProfile",
    "REQUIRED_JUDGE_PROVIDER_KEYS",
    "SectionJudgePolicy",
    "SectionJudgePolicySSOTError",
    "get_judge_runtime_profile",
    "all_canonical_section_policies",
    "get_section_judge_policy",
    "normalize_section_id",
    "policy_matrix_export",
]
