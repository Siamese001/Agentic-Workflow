"""SSOT: employment bullet judge dimensions (Unify / IBM) — not executive-summary rubrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Executive-summary judge dimensions that must never appear on bullet lanes.
FORBIDDEN_EXEC_SUMMARY_DIMENSION_IDS: Final[frozenset[str]] = frozenset(
    {
        "executive_signal",
        "synthesis_quality",
        "resume_voice",
        "evidence_utilization",
        "deterministic_alignment",
        "executive_strategy_thesis",
        "executive_summary_quality",
        "executive_presence",
        "executive_brevity",
        "north_star_alignment",
        "complementarity_vs_bullets",
        "why_role_mattered",
    }
)

EMPLOYMENT_BULLET_RUBRIC_VERSION: Final[str] = "employment_bullet_judge_v1"


@dataclass(frozen=True, slots=True)
class BulletJudgeDimension:
    dimension_id: str
    criterion: str


def _numbered_block(dimensions: tuple[BulletJudgeDimension, ...]) -> str:
    lines = ["Rubric dimensions (employment bullets — not executive summary):"]
    for idx, dim in enumerate(dimensions, start=1):
        lines.append(f"{idx}. {dim.dimension_id}: {dim.criterion}")
    return "\n".join(lines)


# Shared across Unify and IBM bullet lanes.
SHARED_EMPLOYMENT_BULLET_DIMENSIONS: Final[tuple[BulletJudgeDimension, ...]] = (
    BulletJudgeDimension(
        "claim_ledger_grounding",
        "each bullet maps to bul_* source_fact_ids in the claim ledger; metrics match allowed facts verbatim.",
    ),
    BulletJudgeDimension(
        "bullet_line_discipline",
        "one high-impact resume bullet per slot — concise line, no narrative paragraph or multi-sentence block.",
    ),
    BulletJudgeDimension(
        "jd_briefing_targeting_discipline",
        "JD and briefing shape emphasis only — never JD-as-proof, briefing-as-proof, or target company as experience.",
    ),
    BulletJudgeDimension(
        "keyword_discipline_without_stuffing",
        "role-relevant phrasing without ATS keyword bags or copied JD phrases as proof.",
    ),
    BulletJudgeDimension(
        "cross_bullet_outcome_diversity",
        "each bullet answers a distinct outcome spine — not six restatements of the same mechanism stack.",
    ),
    BulletJudgeDimension(
        "employer_scope_purity",
        "no cross-employer fact leakage, wrong-company names, or facts from other employment slices.",
    ),
)

UNIFY_BULLET_ONLY_DIMENSIONS: Final[tuple[BulletJudgeDimension, ...]] = (
    BulletJudgeDimension(
        "current_role_unify_platform_signal",
        "Unify reads as the candidate's current-role platform proof (governance, commercialization, scale) where evidenced.",
    ),
    BulletJudgeDimension(
        "protected_metric_anchor",
        "bul_unify_006 preserves locked commercial metrics ($22M / margin / team scale) and approved metric_outcome_id anchors without splitting or diluting.",
    ),
    BulletJudgeDimension(
        "mechanism_inventory_cap",
        "at most one mechanism-dense bullet; others stay outcome-led, not comma-stacked architecture inventories.",
    ),
)

IBM_BULLET_ONLY_DIMENSIONS: Final[tuple[BulletJudgeDimension, ...]] = (
    BulletJudgeDimension(
        "foundation_enterprise_credibility",
        "IBM bullets prove enterprise/platform foundation — not ownership of current agentic runtime product lines.",
    ),
    BulletJudgeDimension(
        "ibm_fact_scope_only",
        "bul_ibm_* facts only — no Unify, InsurTech, EY, education, or early-career contamination.",
    ),
    BulletJudgeDimension(
        "no_unify_runtime_vocabulary",
        "no Unify-era agentic runtime vocabulary (agentic AI, GraphRAG, multi-agent orchestration, etc.).",
    ),
    BulletJudgeDimension(
        "narrative_slot_reservation",
        "bullets deliver KPI lines; they do not preempt the IBM one-sentence narrative capstone.",
    ),
)


def employment_bullet_dimensions(section_id: str) -> tuple[BulletJudgeDimension, ...]:
    lane = str(section_id or "").strip().lower()
    if lane == "unify_bullets":
        return SHARED_EMPLOYMENT_BULLET_DIMENSIONS + UNIFY_BULLET_ONLY_DIMENSIONS
    if lane == "ibm_bullets":
        return SHARED_EMPLOYMENT_BULLET_DIMENSIONS + IBM_BULLET_ONLY_DIMENSIONS
    return SHARED_EMPLOYMENT_BULLET_DIMENSIONS


def pool_selector_dimension_ids(section_id: str) -> tuple[str, ...]:
    """Subset scored per candidate variant in the Claude pool selector."""
    lane = str(section_id or "").strip().lower()
    if lane == "unify_bullets":
        return (
            "claim_ledger_grounding",
            "bullet_line_discipline",
            "jd_briefing_targeting_discipline",
            "keyword_discipline_without_stuffing",
            "cross_bullet_outcome_diversity",
            "current_role_unify_platform_signal",
            "protected_metric_anchor",
        )
    if lane == "ibm_bullets":
        return (
            "claim_ledger_grounding",
            "bullet_line_discipline",
            "jd_briefing_targeting_discipline",
            "keyword_discipline_without_stuffing",
            "cross_bullet_outcome_diversity",
            "foundation_enterprise_credibility",
            "no_unify_runtime_vocabulary",
        )
    return tuple(d.dimension_id for d in SHARED_EMPLOYMENT_BULLET_DIMENSIONS)


def pool_selector_scoring_instruction(section_id: str) -> str:
    dims = pool_selector_dimension_ids(section_id)
    numbered = "\n".join(f"  - {d}" for d in dims)
    return (
        "Score each candidate variant 0.0–1.0 on these employment-bullet dimensions only "
        "(do not use executive-summary dimensions such as synthesis_quality, resume_voice, "
        "evidence_utilization, or sentence-count criteria):\n"
        f"{numbered}\n"
        "- Composite score = minimum across dimensions (weakest dimension governs).\n"
        "- Apply min_selection_score as the pass floor for pool selection (score below floor => passes=false)."
    )


def grade_only_rubric_text(section_id: str, *, bullet_count: int, bullet_id_range: str) -> str:
    dims = employment_bullet_dimensions(section_id)
    block = _numbered_block(dims)
    lane = str(section_id or "").strip().lower()
    extra = ""
    if lane == "unify_bullets":
        extra = (
            "\n\nDecisive failure triggers:\n"
            "- unsupported metric or cross-employer fact leakage (IBM/InsurTech/EY)\n"
            "- first-person language\n"
            f"- wrong bullet count (expected {bullet_count})\n"
            "- protected bul_unify_006 metrics missing or split incorrectly\n"
            "- JD phrase copied as proof (>4 consecutive words)\n"
            "- generic filler that loses Unify-specific mechanisms or protected metrics"
        )
    elif lane == "ibm_bullets":
        extra = (
            "\n\nDecisive failure triggers:\n"
            "- unsupported metric or cross-employer fact leakage (bul_unify_*, InsurTech, EY, etc.)\n"
            "- first-person language\n"
            f"- wrong bullet count (expected {bullet_count})\n"
            "- JD phrase copied as proof (>4 consecutive words)\n"
            "- Unify runtime vocabulary in bullet text"
        )
    return (
        f"You are evaluating exactly {bullet_count} employment bullets ({bullet_id_range}).\n"
        "This is a BULLET-LINE lane — not an executive summary paragraph.\n"
        "Return JSON only with: score_scale, score, threshold, pass, decisive_failure, findings, "
        "cited_sentence_indexes, remediation_suggestions.\n\n"
        "Score contract:\n"
        '- score_scale must be "0_to_1" or "0_to_5" only.\n'
        "- Keep score and threshold within the declared scale.\n"
        "- Employment pool lanes: min_selection_score is the pass floor for Claude pool selection.\n\n"
        f"{block}"
        f"{extra}"
    ).strip()


def assert_no_exec_summary_dimensions(section_id: str) -> None:
    """Raise if bullet rubric accidentally reuses executive-summary dimension ids."""
    ids = {d.dimension_id for d in employment_bullet_dimensions(section_id)}
    overlap = ids & FORBIDDEN_EXEC_SUMMARY_DIMENSION_IDS
    if overlap:
        raise ValueError(f"{section_id}: bullet rubric must not reuse exec-summary dimensions: {sorted(overlap)}")


__all__ = [
    "EMPLOYMENT_BULLET_RUBRIC_VERSION",
    "FORBIDDEN_EXEC_SUMMARY_DIMENSION_IDS",
    "BulletJudgeDimension",
    "SHARED_EMPLOYMENT_BULLET_DIMENSIONS",
    "UNIFY_BULLET_ONLY_DIMENSIONS",
    "IBM_BULLET_ONLY_DIMENSIONS",
    "assert_no_exec_summary_dimensions",
    "employment_bullet_dimensions",
    "grade_only_rubric_text",
    "pool_selector_dimension_ids",
    "pool_selector_scoring_instruction",
]
