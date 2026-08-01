"""Stable section-quality benchmark constants."""

from __future__ import annotations

INPUT_SCHEMA_VERSION = "apps_rg.section_quality_input.v1"
REVIEW_SCHEMA_VERSION = "apps_rg.section_quality_review.v1"
REPORT_SCHEMA_VERSION = "apps_rg.section_quality_report.v1"

SECTION_IDS = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "ibm_bullets",
)

DIMENSIONS = (
    "target_job_relevance",
    "evidence_fidelity",
    "achievement_prioritization",
    "naturalness",
    "professional_voice",
    "concision",
    "specificity",
    "non_contrivance",
    "ats_compatibility",
    "keyword_use",
    "jd_parroting_avoidance",
    "unsupported_language_avoidance",
    "repetition_avoidance",
    "internal_coherence",
)

RUBRIC_FILES = {
    "headline": "headline.v1.yaml",
    "executive_summary": "executive_summary.v1.yaml",
    "competencies": "competencies.v1.yaml",
    "unify_bullets": "experience_bullets.v1.yaml",
    "ibm_bullets": "experience_bullets.v1.yaml",
}

RESULT_STATES = frozenset({"PASS", "FAIL", "UNKNOWN", "NOT_MEASURED"})
REVIEWER_CLASSES = frozenset({"HUMAN", "MODEL_JUDGE"})
PREFERENCES = frozenset({"VARIANT_A", "VARIANT_B", "TIE", "UNKNOWN"})

__all__ = [
    "DIMENSIONS",
    "INPUT_SCHEMA_VERSION",
    "PREFERENCES",
    "REPORT_SCHEMA_VERSION",
    "RESULT_STATES",
    "REVIEWER_CLASSES",
    "REVIEW_SCHEMA_VERSION",
    "RUBRIC_FILES",
    "SECTION_IDS",
]
