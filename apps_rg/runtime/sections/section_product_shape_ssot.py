"""Canonical product-shape numbers for generated lanes (SSOT for prompts + drift audit).

Values are imported from existing X2 validators / rigor modules — do not duplicate magic numbers here.
Drift audit and PRODUCT_SHAPE compile blocks read this module only; extend patterns/gates here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.competencies_rigor import (
    CANDIDATE_CATEGORY_COUNT,
    MAX_CATEGORY_COUNT,
    MAX_ITEMS_PER_CATEGORY,
    MIN_CATEGORY_COUNT,
    MIN_ITEMS_PER_CATEGORY,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_SENTENCES,
    EXEC_SUMMARY_MAX_WORDS,
    EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE,
    EXEC_SUMMARY_MIN_SENTENCES,
    EXPECTED_PROMPT_ID as EXEC_SUMMARY_PROMPT_ID,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import SC_PATH_COUNT_BY_LANE

# Headline (aligned with headline_x2 headline_runtime_self_check_truth)
HEADLINE_WORD_MIN = 10
HEADLINE_WORD_MAX = 13
HEADLINE_MAX_CHARS = 140
HEADLINE_SEGMENT_PREFIX = "SVP Engineering"
HEADLINE_PIPE_SEPARATORS = 3
HEADLINE_SEGMENT_COUNT = 4

NARRATIVE_MAX_WORDS = 58
NARRATIVE_MAX_CHARS = 360
NARRATIVE_PREFERRED_WORD_MIN = 34
NARRATIVE_PREFERRED_WORD_MAX = 48

JD_ALIGNMENT_PROOF_FIELDS: tuple[str, ...] = (
    "targeting_only",
    "jd_used_as_proof",
    "briefing_used_as_proof",
    "companion_context_used_as_proof",
    "companion_used_as_proof",
)

# Shared template drift guards (forbidden in PA YAML — not model output)
FORBIDDEN_LEGACY_EXEC_SUMMARY: tuple[str, ...] = (
    r"2\s*[-–]\s*3\s+dense\s+sentences\s+by\s+default",
    r"default\s+2\s+or\s+3\s+sentences",
    r"2\s*[-–]\s*3\s+sentences\s+\(sovereign",
    r"Hold to\s+2\s+or\s+3\s+sentences",
    r"section budget explicitly allows",
    r"95-160 words",
    r"hard minimum 95",
    r"4\s*[-–]\s*5\s+sentences",
    r"4 or 5 sentences",
    r"max\s+220\s+words",
)
FORBIDDEN_LEGACY_HEADLINE: tuple[str, ...] = (
    r"8\s*[-–]\s*11",
    r"8 to 11",
)
FORBIDDEN_LEGACY_COMPETENCIES: tuple[str, ...] = (
    r"exactly\s+6\s+(?:executive\s+capability\s+)?categor",
    r"emit\s+exactly\s+6",
    r"across\s+the\s+6\s+categories",
    r"graph_10x6",
)
FORBIDDEN_LEGACY_NARRATIVE: tuple[str, ...] = (
    r"250-character",
    r"max 250",
    r"two\s+sentences",
)

# Retired X2 gate IDs — must not appear in run_x2_gates output (old proof bundles may still list them).
RETIRED_EXEC_SUMMARY_X2_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_exec_summary_sentence_count_2_3",
        "x2_exec_summary_srfs_density_word_count",
        "x2_exec_summary_sentence_count_4_5",
        "x2_exec_summary_sentence_count_5_6",
        "x2_exec_summary_srfs_sentence_count_4_5",
        "x2_exec_summary_srfs_sentence_responsibility_shape",
        "x2_exec_summary_paragraph_word_bounds",
    }
)

RETIRED_UNIFY_BULLETS_X2_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_unify_max_heavy_3",
        "x2_unify_rewrite_distribution_valid",
        "x2_unify_min_light_protected_1",
        "x2_unify_intensity_per_bullet_ssot",
        "x2_unify_metric_bullets_not_heavy",
        "x2_unify_protected_bullet_preserved_or_justified",
    }
)

RETIRED_IBM_BULLETS_X2_GATE_IDS: frozenset[str] = frozenset(
    {
        "x2_ibm_rewrite_distribution_valid",
        "x2_ibm_heavy_rewrites_zero",
    }
)

# W3: legacy SRFS slice membership gate IDs — superseded by *_active_proof_pool_source_fact_ids.
RETIRED_PROOF_POOL_SLICE_X2_GATE_IDS: frozenset[str] = frozenset(
    {
        f"x2_{section_id}_source_fact_ids_within_srfs_slice"
        for section_id in (
            "headline",
            "executive_summary",
            "unify_bullets",
            "unify_narrative",
            "ibm_bullets",
            "ibm_narrative",
            "competencies",
        )
    }
)


def is_retired_exec_summary_x2_gate(gate_id: str) -> bool:
    return str(gate_id or "").strip() in RETIRED_EXEC_SUMMARY_X2_GATE_IDS


def _merge_gate_ids(*groups: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for group in groups:
        for gate_id in group:
            if gate_id not in seen:
                seen.add(gate_id)
                out.append(gate_id)
    return tuple(out)


@dataclass(frozen=True)
class SectionProductShape:
    section_id: str
    template_ref: str
    x2_module_ref: str
    display_field: str
    shape_summary: str
    bounds_gate_ids: tuple[str, ...]
    proof_gate_ids: tuple[str, ...]
    style_gate_ids: tuple[str, ...]
    required_any_text_patterns: tuple[str, ...]
    required_all_text_patterns: tuple[str, ...]
    forbidden_text_patterns: tuple[str, ...]
    jd_alignment_proof_fields: tuple[str, ...]
    compile_hints: tuple[str, ...]

    @property
    def required_gate_ids(self) -> tuple[str, ...]:
        return _merge_gate_ids(self.bounds_gate_ids, self.proof_gate_ids, self.style_gate_ids)


def _exec_summary_shape() -> SectionProductShape:
    return SectionProductShape(
        section_id="executive_summary",
        template_ref="apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml",
        x2_module_ref="apps_rg/runtime/validators/executive_summary_x2.py",
        display_field="resume_display_text",
        shape_summary=(
            f"exactly {EXEC_SUMMARY_MIN_SENTENCES} sentences; "
            f"max {EXEC_SUMMARY_MAX_WORDS} words; "
            f"max {EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE} words/sentence; "
            "fit_to_evidence; claim_ledger required; no inline source tags in display text"
        ),
        bounds_gate_ids=(
            "x2_exec_summary_sentence_count_6",
            "x2_exec_summary_paragraph_max_words",
            "x2_exec_summary_evidence_utilization",
        ),
        proof_gate_ids=(
            "x2_exec_summary_jd_alignment_proof_flags",
            "x2_claim_ledger_row_count_matches_sentence_count",
            "x2_self_check_claim_ledger_consistent",
            "x2_claim_field_maps_to_display_sentence",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_claim_ledger_orphan_zero",
            "x2_exec_summary_prompt_template_authority",
            "x2_exec_summary_display_roundtrip_integrity",
            "x2_exec_summary_cross_sentence_metric_dedup",
            "x2_exec_summary_c03_selected_fact_ids_claimable_subset_allowed_fact_ids",
            "x2_exec_summary_allowed_fact_utilization",
        ),
        style_gate_ids=(
            "x2_first_person_zero",
            "x2_em_dash_count_zero",
            "x2_exec_summary_no_mechanism_inventory",
            "x2_exec_summary_no_credential_dump",
        ),
        required_any_text_patterns=(
            r"exactly\s+6",
            r"\b6\s+sentences\b",
        ),
        required_all_text_patterns=(
            "fit_to_evidence",
            "jd_used_as_proof",
            "targeting_only",
            EXEC_SUMMARY_PROMPT_ID,
        ),
        forbidden_text_patterns=FORBIDDEN_LEGACY_EXEC_SUMMARY,
        jd_alignment_proof_fields=JD_ALIGNMENT_PROOF_FIELDS,
        compile_hints=(
            f"template_id={EXEC_SUMMARY_PROMPT_ID}",
            f"sentence_count={EXEC_SUMMARY_MIN_SENTENCES}",
            f"max_words={EXEC_SUMMARY_MAX_WORDS}",
            "x2_exec_summary_paragraph_max_words",
            "x2_exec_summary_evidence_utilization",
            "legacy 2-3 sentence band retired",
        ),
    )


def _headline_shape() -> SectionProductShape:
    return SectionProductShape(
        section_id="headline",
        template_ref="apps_rg/prompt_assembly/templates/headline_tailor_v1.yaml",
        x2_module_ref="apps_rg/runtime/validators/headline_x2.py",
        display_field="headline_line",
        shape_summary=(
            f"{HEADLINE_SEGMENT_COUNT} segments; prefix {HEADLINE_SEGMENT_PREFIX!r}; "
            f"{HEADLINE_PIPE_SEPARATORS} pipe separators; "
            f"{HEADLINE_WORD_MIN}-{HEADLINE_WORD_MAX} words total; one line only"
        ),
        bounds_gate_ids=(
            "x2_headline_exactly_one_line",
            "x2_headline_pipe_four_segments",
            "x2_headline_word_count_10_to_13",
            "x2_headline_executive_length",
        ),
        proof_gate_ids=(
            "x2_headline_claim_ledger_rows_present",
            "x2_headline_claim_ledger_segment_decomposition",
            "x2_headline_text_claim_coverage_integrity",
            "x2_headline_source_supported",
        ),
        style_gate_ids=(
            "x2_headline_segments_quality",
            "x2_headline_self_check_consistent",
            "x2_headline_raw_model_schema_valid",
        ),
        required_any_text_patterns=(
            r"10\s*[-–]\s*13",
            r"10 to 13",
        ),
        required_all_text_patterns=(
            "SVP Engineering",
            "jd_used_as_proof",
            "briefing_used_as_proof",
            "companion_used_as_proof",
            "targeting_only",
        ),
        forbidden_text_patterns=FORBIDDEN_LEGACY_HEADLINE,
        jd_alignment_proof_fields=JD_ALIGNMENT_PROOF_FIELDS,
        compile_hints=(
            f"word_band={HEADLINE_WORD_MIN}-{HEADLINE_WORD_MAX}",
            f"segments={HEADLINE_SEGMENT_COUNT}",
            f"pipes={HEADLINE_PIPE_SEPARATORS}",
            "X/Y/Z are fresh phrases not JD/briefing copy",
        ),
    )


def _competencies_shape() -> SectionProductShape:
    return SectionProductShape(
        section_id="competencies",
        template_ref="apps_rg/prompt_assembly/templates/competency_selector_v2.yaml",
        x2_module_ref="apps_rg/runtime/validators/competencies_x2.py",
        display_field="competencies",
        shape_summary=(
            f"graph_8x8: top {MIN_CATEGORY_COUNT} of {CANDIDATE_CATEGORY_COUNT} categories; "
            f"{MIN_ITEMS_PER_CATEGORY}-{MAX_ITEMS_PER_CATEGORY} terms/category; "
            "compact noun phrases; augmented_skills_graph authority"
        ),
        bounds_gate_ids=(
            "x2_competencies_min_category_count",
            "x2_competencies_min_items_per_category",
            "x2_competencies_approved_category_labels",
        ),
        proof_gate_ids=(
            "x2_competency_companion_context_not_proof",
            "x2_competencies_term_support_ids_present",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_gate_rows_are_internally_consistent",
        ),
        style_gate_ids=(
            "x2_competencies_no_fragment_or_one_word_terms",
            "x2_competencies_no_low_rigor_two_word_items",
            "x2_competencies_no_credential_relisting",
            "x2_competencies_no_reserved_certification_category",
            "x2_competencies_no_metrics_as_skills_without_capability_context",
            "x2_competencies_role_alignment_terms",
            "x2_competencies_no_all_generic_skill_phrase",
            "x2_competencies_keyword_repetition_limit",
        ),
        required_any_text_patterns=(
            r"graph_8x8",
            r"VERIFIED_SKILL_INVENTORY_PROJECTION",
            "augmented_skills_graph",
            str(CANDIDATE_CATEGORY_COUNT),
        ),
        required_all_text_patterns=(
            str(MIN_CATEGORY_COUNT),
            str(MAX_CATEGORY_COUNT),
            str(MIN_ITEMS_PER_CATEGORY),
            str(MAX_ITEMS_PER_CATEGORY),
            "companion_context_used_as_proof",
            "targeting_only",
            "source_fact_ids",
        ),
        forbidden_text_patterns=FORBIDDEN_LEGACY_COMPETENCIES,
        jd_alignment_proof_fields=JD_ALIGNMENT_PROOF_FIELDS,
        compile_hints=(
            "terms are objects with text + source_fact_id + source_fact_ids[]",
            "no_full_sentences in competency display",
            "no inline citation tags in display text",
        ),
    )


def _unify_bullets_shape() -> SectionProductShape:
    pool_n = SC_PATH_COUNT_BY_LANE["unify_bullets"]
    return SectionProductShape(
        section_id="unify_bullets",
        template_ref="apps_rg/prompt_assembly/templates/unify_bullet_tailor_v1.yaml",
        x2_module_ref="apps_rg/runtime/validators/unify_bullets_x2.py",
        display_field="bullets",
        shape_summary=(
            f"6 bullets from {pool_n}-path self-consistency pool; Claude pool selector picks top-6 passing score; "
            "bul_unify_* fact ids only"
        ),
        bounds_gate_ids=(
            "x2_unify_bullet_count_6",
            "x2_unify_bullet_single_thought",
            "x2_unify_bullet_no_embedded_newline",
            "x2_unify_bullet_no_paragraph_block",
            "x2_unify_at_most_one_mechanism_dense_bullet",
            "x2_unify_protected_bullet_metrics_preserved",
        ),
        proof_gate_ids=(
            "x2_text_claim_coverage_integrity",
            "x2_unify_metric_anchor_bullet_ownership",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_unify_no_rewrite_intensity_model",
            "x2_unify_track_ranked_selection_method",
            "x2_unify_not_legacy_six_pack_allocation",
            "x2_unify_no_archive_claim_verbatim",
        ),
        style_gate_ids=(),
        required_any_text_patterns=(
            r"exactly\s+6",
            r"pool",
            r"self[- ]consistency",
            r"Claude.*select",
        ),
        required_all_text_patterns=(
            "bul_unify_",
            "min_selection_score",
        ),
        forbidden_text_patterns=(
            r"exactly\s+5\s+bullets",
            r"7\s+bullets",
            r"bul_ibm_",
            r"HEAVY:\s*2",
            r"rewrite_intensity",
            r"LIGHT_PROTECTED",
        ),
        jd_alignment_proof_fields=("targeting_only", "jd_used_as_proof"),
        compile_hints=(
            f"sc_pool_paths={pool_n}; claude_top_n=6; min_score gate",
            "companion_context_allowed=false",
        ),
    )


def _unify_narrative_shape() -> SectionProductShape:
    return SectionProductShape(
        section_id="unify_narrative",
        template_ref="apps_rg/prompt_assembly/templates/unify_position_narrative_v1.yaml",
        x2_module_ref="apps_rg/runtime/validators/unify_narrative_x2.py",
        display_field="narrative_sentence",
        shape_summary=(
            f"exactly 1 sentence; <= {NARRATIVE_MAX_WORDS} words; <= {NARRATIVE_MAX_CHARS} chars; "
            f"preferred {NARRATIVE_PREFERRED_WORD_MIN}-{NARRATIVE_PREFERRED_WORD_MAX} words; "
            "requires finalized unify bullets"
        ),
        bounds_gate_ids=(
            "x2_unify_narrative_exactly_one_sentence",
            "x2_unify_narrative_exactly_one_sentence_mechanical",
            "x2_unify_narrative_forbidden_opener",
            "x2_unify_narrative_metric_cap",
            "x2_unify_narrative_bullet_overlap_threshold",
            "x2_unify_narrative_word_budget",
        ),
        proof_gate_ids=(
            "x2_unify_narrative_requires_finalized_bullets",
            "x2_claim_ledger_claim_text_non_empty",
        ),
        style_gate_ids=(),
        required_any_text_patterns=(r"Exactly\s+one\s+sentence", r"exactly one sentence"),
        required_all_text_patterns=(
            r"58\s+words",
            r"360",
            "bul_unify_",
            "targeting only",
        ),
        forbidden_text_patterns=FORBIDDEN_LEGACY_NARRATIVE + (r"bul_ibm_", r"bul_insurtech_", r"bul_ey_"),
        jd_alignment_proof_fields=("targeting_only", "jd_used_as_proof"),
        compile_hints=(
            f"word_max={NARRATIVE_MAX_WORDS}",
            f"char_max={NARRATIVE_MAX_CHARS}",
            "no bullet characters in narrative_sentence",
        ),
    )


def _ibm_bullets_shape() -> SectionProductShape:
    pool_n = SC_PATH_COUNT_BY_LANE["ibm_bullets"]
    return SectionProductShape(
        section_id="ibm_bullets",
        template_ref="apps_rg/prompt_assembly/templates/ibm_bullet_tailor_v1.yaml",
        x2_module_ref="apps_rg/runtime/validators/ibm_bullets_x2.py",
        display_field="bullets",
        shape_summary=(
            f"5 bullets from {pool_n}-path self-consistency pool; Claude pool selector picks top-5 passing score; "
            "bul_ibm_* only"
        ),
        bounds_gate_ids=(
            "x2_ibm_bullet_count_5",
            "x2_ibm_bullet_single_thought",
            "x2_ibm_bullet_no_embedded_newline",
            "x2_ibm_bullet_no_paragraph_block",
            "x2_ibm_narrative_slot_reservation",
        ),
        proof_gate_ids=(
            "x2_text_claim_coverage_integrity",
            "x2_ibm_metric_anchor_bullet_ownership",
            "x2_claim_ledger_claim_text_non_empty",
            "x2_ibm_no_rewrite_intensity_model",
        ),
        style_gate_ids=("x2_no_unify_runtime_terms",),
        required_any_text_patterns=(
            r"exactly\s+5",
            r"pool",
            r"self[- ]consistency",
        ),
        required_all_text_patterns=(
            "bul_ibm_",
            "min_selection_score",
        ),
        forbidden_text_patterns=(
            r"exactly\s+6",
            r"bul_unify_",
            r"rewrite_intensity",
            r"\bHEAVY\b",
            r"LIGHT_PROTECTED",
        ),
        jd_alignment_proof_fields=("targeting_only", "jd_used_as_proof"),
        compile_hints=(
            f"sc_pool_paths={pool_n}; claude_top_n=5; min_score gate",
            "IBM_BULLETS_FOUNDATION slice",
        ),
    )


def _ibm_narrative_shape() -> SectionProductShape:
    return SectionProductShape(
        section_id="ibm_narrative",
        template_ref="apps_rg/prompt_assembly/templates/ibm_position_narrative_v1.yaml",
        x2_module_ref="apps_rg/runtime/validators/ibm_narrative_x2.py",
        display_field="narrative_sentence",
        shape_summary=(
            f"exactly 1 sentence; <= {NARRATIVE_MAX_WORDS} words; <= {NARRATIVE_MAX_CHARS} chars; "
            "requires finalized ibm bullets; no meta disclaimer in display"
        ),
        bounds_gate_ids=(
            "x2_ibm_narrative_exactly_one_sentence",
            "x2_ibm_narrative_exactly_one_sentence_mechanical",
            "x2_ibm_narrative_forbidden_opener",
            "x2_ibm_narrative_metric_cap",
            "x2_ibm_narrative_bullet_overlap_threshold",
            "x2_ibm_narrative_word_budget",
        ),
        proof_gate_ids=(
            "x2_ibm_narrative_requires_finalized_bullets",
            "x2_ibm_narrative_claim_ledger_clause_decomposition",
            "x2_claim_ledger_claim_text_non_empty",
        ),
        style_gate_ids=("x2_ibm_narrative_no_meta_disclaimer_in_display",),
        required_any_text_patterns=(r"Exactly\s+one\s+sentence", r"exactly one sentence"),
        required_all_text_patterns=(r"58\s+words", r"360", "bul_ibm_"),
        forbidden_text_patterns=FORBIDDEN_LEGACY_NARRATIVE + (r"bul_unify_", r"bul_insurtech_", r"bul_ey_"),
        jd_alignment_proof_fields=("targeting_only", "jd_used_as_proof"),
        compile_hints=(
            f"word_max={NARRATIVE_MAX_WORDS}",
            f"char_max={NARRATIVE_MAX_CHARS}",
            "companion optional; never proof",
        ),
    )


def _role_bullets_shape(section_id: str, *, employer_label: str, bullet_prefix: str) -> SectionProductShape:
    pool_n = SC_PATH_COUNT_BY_LANE.get(section_id, 4)
    return SectionProductShape(
        section_id=section_id,
        template_ref=f"apps_rg/prompt_assembly/templates/{section_id}_tailor_v1.yaml",
        x2_module_ref="apps_rg/runtime/sections/role_episode_lane.py",
        display_field="bullets",
        shape_summary=(
            f"3 {employer_label} bullets from {pool_n}-path pool when proof exists; "
            f"{bullet_prefix}_* source ids only; fail closed on missing upstream evidence"
        ),
        bounds_gate_ids=(
            f"x2_{section_id}_bullet_count_3",
            f"x2_{section_id}_bullet_single_thought",
            f"x2_{section_id}_bullet_no_embedded_newline",
        ),
        proof_gate_ids=(
            f"x2_{section_id}_allowed_fact_ids_non_empty",
            f"x2_{section_id}_source_fact_ids_supported",
            "x2_claim_ledger_claim_text_non_empty",
        ),
        style_gate_ids=("x2_no_first_person", "x2_no_em_dash"),
        required_any_text_patterns=(r"exactly\s+3", r"3\s+bullets"),
        required_all_text_patterns=(bullet_prefix, "targeting_only", "source_fact_ids"),
        forbidden_text_patterns=(r"JD_ONLY", r"BRIEFING_ONLY", r"TARGET_ONLY"),
        jd_alignment_proof_fields=("targeting_only", "jd_used_as_proof"),
        compile_hints=(
            f"qwen_pool_paths={pool_n}; final_bullets=3",
            "upstream evidence required; retries cannot repair missing proof",
        ),
    )


def _role_narrative_shape(section_id: str, *, employer_label: str, bullet_prefix: str) -> SectionProductShape:
    return SectionProductShape(
        section_id=section_id,
        template_ref=f"apps_rg/prompt_assembly/templates/{section_id}_v1.yaml",
        x2_module_ref="apps_rg/runtime/sections/role_episode_lane.py",
        display_field="narrative_sentence",
        shape_summary=(
            f"exactly 1 {employer_label} sentence; <= {NARRATIVE_MAX_WORDS} words; "
            f"<= {NARRATIVE_MAX_CHARS} chars; requires finalized {bullet_prefix} bullets"
        ),
        bounds_gate_ids=(
            f"x2_{section_id}_exactly_one_sentence",
            f"x2_{section_id}_word_budget",
            f"x2_{section_id}_char_budget",
        ),
        proof_gate_ids=(
            f"x2_{section_id}_allowed_fact_ids_non_empty",
            f"x2_{section_id}_source_fact_ids_supported",
            "x2_claim_ledger_claim_text_non_empty",
        ),
        style_gate_ids=("x2_no_first_person", "x2_no_em_dash"),
        required_any_text_patterns=(r"Exactly\s+one\s+sentence", r"exactly one sentence"),
        required_all_text_patterns=(bullet_prefix, "targeting_only"),
        forbidden_text_patterns=FORBIDDEN_LEGACY_NARRATIVE,
        jd_alignment_proof_fields=("targeting_only", "jd_used_as_proof"),
        compile_hints=(f"word_max={NARRATIVE_MAX_WORDS}", f"char_max={NARRATIVE_MAX_CHARS}"),
    )


_SECTION_BUILDERS: dict[str, Any] = {
    "executive_summary": _exec_summary_shape,
    "headline": _headline_shape,
    "competencies": _competencies_shape,
    "unify_bullets": _unify_bullets_shape,
    "unify_narrative": _unify_narrative_shape,
    "ibm_bullets": _ibm_bullets_shape,
    "ibm_narrative": _ibm_narrative_shape,
    "insurtech_bullets": lambda: _role_bullets_shape(
        "insurtech_bullets",
        employer_label="InsurTech",
        bullet_prefix="bul_insurtech",
    ),
    "ey_bullets": lambda: _role_bullets_shape(
        "ey_bullets",
        employer_label="EY",
        bullet_prefix="bul_ey",
    ),
    "insurtech_narrative": lambda: _role_narrative_shape(
        "insurtech_narrative",
        employer_label="InsurTech",
        bullet_prefix="bul_insurtech",
    ),
    "ey_narrative": lambda: _role_narrative_shape(
        "ey_narrative",
        employer_label="EY",
        bullet_prefix="bul_ey",
    ),
}


def section_product_shape(section_id: str) -> SectionProductShape:
    if section_id not in _SECTION_BUILDERS:
        raise KeyError(f"no product shape SSOT for section_id={section_id!r}")
    return _SECTION_BUILDERS[section_id]()


def all_generated_lane_shapes() -> tuple[SectionProductShape, ...]:
    return tuple(section_product_shape(lane) for lane in GENERATED_LANES)


def product_shape_gate_ids_for_lane(section_id: str) -> frozenset[str]:
    """Gate IDs owned by product-shape SSOT (bounds + proof + style)."""
    return frozenset(section_product_shape(section_id).required_gate_ids)


def product_shape_gate_ids_by_lane() -> dict[str, frozenset[str]]:
    return {lane: product_shape_gate_ids_for_lane(lane) for lane in GENERATED_LANES}


def _format_gate_group(label: str, gate_ids: tuple[str, ...]) -> str:
    if not gate_ids:
        return ""
    lines = "\n".join(f"  - {gid}" for gid in gate_ids)
    return f"{label}:\n{lines}\n"


def format_product_shape_prompt_block(section_id: str) -> str:
    """Runtime compile appendix: same numbers and gate IDs as deterministic X2."""
    shape = section_product_shape(section_id)
    jd_fields = ", ".join(shape.jd_alignment_proof_fields)
    hints = "\n".join(f"- hint: {h}" for h in shape.compile_hints) if shape.compile_hints else ""
    forbidden = (
        "\n".join(f"- forbidden in prompts: /{p}/" for p in shape.forbidden_text_patterns[:6])
        if shape.forbidden_text_patterns
        else ""
    )
    return (
        "PRODUCT_SHAPE (deterministic X2 authority — match these bounds; prompts must not contradict):\n"
        f"- section: {shape.section_id}\n"
        f"- display_field: {shape.display_field}\n"
        f"- shape: {shape.shape_summary}\n"
        f"- x2_profile: {shape.x2_module_ref}\n"
        f"- template_ssot: {shape.template_ref}\n"
        f"- jd_alignment fields (when object present): {jd_fields}\n"
        f"{_format_gate_group('Bounds gates', shape.bounds_gate_ids)}"
        f"{_format_gate_group('Proof gates', shape.proof_gate_ids)}"
        f"{_format_gate_group('Style gates', shape.style_gate_ids)}"
        f"{hints}\n"
        f"{forbidden}"
    )


def shape_to_dict(shape: SectionProductShape) -> dict[str, Any]:
    return {
        "section_id": shape.section_id,
        "template_ref": shape.template_ref,
        "x2_module_ref": shape.x2_module_ref,
        "display_field": shape.display_field,
        "shape_summary": shape.shape_summary,
        "bounds_gate_ids": list(shape.bounds_gate_ids),
        "proof_gate_ids": list(shape.proof_gate_ids),
        "style_gate_ids": list(shape.style_gate_ids),
        "required_gate_ids": list(shape.required_gate_ids),
        "required_any_text_patterns": list(shape.required_any_text_patterns),
        "required_all_text_patterns": list(shape.required_all_text_patterns),
        "forbidden_text_patterns": list(shape.forbidden_text_patterns),
        "jd_alignment_proof_fields": list(shape.jd_alignment_proof_fields),
        "compile_hints": list(shape.compile_hints),
    }


__all__ = [
    "FORBIDDEN_LEGACY_COMPETENCIES",
    "FORBIDDEN_LEGACY_EXEC_SUMMARY",
    "FORBIDDEN_LEGACY_HEADLINE",
    "FORBIDDEN_LEGACY_NARRATIVE",
    "HEADLINE_MAX_CHARS",
    "HEADLINE_PIPE_SEPARATORS",
    "HEADLINE_SEGMENT_COUNT",
    "HEADLINE_SEGMENT_PREFIX",
    "HEADLINE_WORD_MAX",
    "HEADLINE_WORD_MIN",
    "RETIRED_UNIFY_BULLETS_X2_GATE_IDS",
    "JD_ALIGNMENT_PROOF_FIELDS",
    "NARRATIVE_MAX_CHARS",
    "NARRATIVE_MAX_WORDS",
    "NARRATIVE_PREFERRED_WORD_MAX",
    "NARRATIVE_PREFERRED_WORD_MIN",
    "RETIRED_EXEC_SUMMARY_X2_GATE_IDS",
    "SectionProductShape",
    "is_retired_exec_summary_x2_gate",
    "all_generated_lane_shapes",
    "format_product_shape_prompt_block",
    "product_shape_gate_ids_by_lane",
    "product_shape_gate_ids_for_lane",
    "section_product_shape",
    "shape_to_dict",
]
