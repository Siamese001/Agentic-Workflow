"""Canonical apps_rg section judge policy matrix (apps_rg only; no agentic_core)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, FrozenSet


class GeneratorModelClass(str, Enum):
    QWEN = "QWEN"
    AGGREGATOR = "AGGREGATOR"


class JudgeTier(str, Enum):
    ENHANCED_REASONING = "ENHANCED_REASONING"
    STANDARD_REASONING = "STANDARD_REASONING"
    BULLET_REWRITE_QUALITY = "BULLET_REWRITE_QUALITY"
    OPTIONAL_ADVISORY_TAXONOMY_ONLY = "OPTIONAL_ADVISORY_TAXONOMY_ONLY"


class FallbackPolicy(str, Enum):
    FAIL_CLOSED = "FAIL_CLOSED"


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
    def x1d_required_for_x3_allow(self) -> bool:
        """When False, X3 may ALLOW without required proof judges passing (competencies)."""
        return self.judge_required_for_proof


# Cross-provider judges ONLY — never anthropic_claude. Claude Sonnet 4.6 is the GENERATOR for every
# lane, so a same-family judge has correlated blind spots (a self-judge that won't catch the
# generator's systematic errors). Recalibrated 2026-06-08 for the Claude base — the 3-provider panel
# was Qwen-era insurance against a weak local generator. See .claude/rules/judge-calibration-cadence.md.
_DUAL_JUDGE_PANEL: tuple[str, ...] = ("gemini_pro", "openai_chatgpt")
_SINGLE_JUDGE_PANEL: tuple[str, ...] = ("gemini_pro",)

# Legacy proof-harness alias: the global proof provider set is the union of recalibrated
# policy panels, not a separately maintained roster.
REQUIRED_JUDGE_PROVIDER_KEYS: tuple[str, ...] = _DUAL_JUDGE_PANEL

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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
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
        generator_model_class=GeneratorModelClass.QWEN,
        judge_required_for_proof=False,
        judge_tier=JudgeTier.OPTIONAL_ADVISORY_TAXONOMY_ONLY,
        required_judge_providers=(),
        proof_eligible_model_classes=frozenset(),
        advisory_model_classes=frozenset({"standard_frontier", "advisory", "flash", "mini"}),
        judge_packet_required=False,
        grade_only_required=True,
        replacement_generation_allowed=False,
    ),
    "professional_competencies": SectionJudgePolicy(
        section_name="professional_competencies",
        generator_model_class=GeneratorModelClass.QWEN,
        judge_required_for_proof=False,
        judge_tier=JudgeTier.OPTIONAL_ADVISORY_TAXONOMY_ONLY,
        required_judge_providers=(),
        proof_eligible_model_classes=frozenset(),
        advisory_model_classes=frozenset({"standard_frontier", "advisory", "flash", "mini"}),
        judge_packet_required=False,
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

_SECTION_ALIASES: dict[str, str] = {
    "professional_competencies": "competencies",
}


def normalize_section_id(section_id: str) -> str:
    sid = (section_id or "").strip().lower().replace("-", "_")
    return _SECTION_ALIASES.get(sid, sid)


def get_section_judge_policy(section_id: str) -> SectionJudgePolicy:
    sid = normalize_section_id(section_id)
    policy = _SECTION_POLICIES.get(sid)
    if policy is None:
        raise KeyError(f"Unknown apps_rg section for judge policy: {section_id!r}")
    return policy


def all_canonical_section_policies() -> dict[str, SectionJudgePolicy]:
    """Return primary section keys (excludes alias duplicate professional_competencies)."""
    return {k: v for k, v in _SECTION_POLICIES.items() if k != "professional_competencies"}


def policy_matrix_export() -> dict[str, dict[str, Any]]:
    """Serializable matrix for tests and proof bundles."""
    out: dict[str, dict[str, Any]] = {}
    for sid, p in all_canonical_section_policies().items():
        out[sid] = {
            "section_name": p.section_name,
            "generator_model_class": p.generator_model_class.value,
            "judge_required_for_proof": p.judge_required_for_proof,
            "judge_tier": p.judge_tier.value,
            "required_judge_providers": list(p.required_judge_providers),
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
    "REQUIRED_JUDGE_PROVIDER_KEYS",
    "SectionJudgePolicy",
    "all_canonical_section_policies",
    "get_section_judge_policy",
    "normalize_section_id",
    "policy_matrix_export",
]
