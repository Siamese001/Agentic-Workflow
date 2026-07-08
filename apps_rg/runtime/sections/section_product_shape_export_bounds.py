"""RG export bounds derived from section_product_shape_ssot (no duplicate magic numbers)."""

from __future__ import annotations

from apps_rg.runtime.sections.competencies_rigor import MAX_CATEGORY_COUNT, MIN_CATEGORY_COUNT
from apps_rg.runtime.sections.section_product_shape_ssot import (
    EXEC_SUMMARY_MAX_SENTENCES,
    EXEC_SUMMARY_MAX_WORDS,
    EXEC_SUMMARY_MIN_SENTENCES,
    HEADLINE_MAX_CHARS,
    NARRATIVE_MAX_CHARS,
    NARRATIVE_MAX_WORDS,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE,
)

# Executive summary — lane X2 caps are the export authority.
EXEC_SUMMARY_EXPORT_MIN_WORDS = 10
EXEC_SUMMARY_EXPORT_MAX_WORDS = EXEC_SUMMARY_MAX_WORDS
EXEC_SUMMARY_EXPORT_MAX_SENTENCES = EXEC_SUMMARY_MAX_SENTENCES
EXEC_SUMMARY_EXPORT_MIN_SENTENCES = EXEC_SUMMARY_MIN_SENTENCES
# Char ceiling DERIVED from the word authority (9 chars/word incl. whitespace —
# observed executive prose runs ~7.7). The previous literal 900 contradicted the
# lane word cap it claims to mirror: a lane-accepted, dual-judge-passed
# summary near the cap is ~1075 chars, so product export could never succeed (first
# export attempt, patch_run_19, 2026-06-11). rg_output_schema.json
# sections.summary.text.maxLength moves in lockstep — enforced by
# tests/_apps_contract/test_schema_export_bounds_match_ssot.py. The word cap
# remains the binding editorial constraint; chars backstop degenerate tokens.
EXEC_SUMMARY_EXPORT_MAX_CHARS = EXEC_SUMMARY_MAX_WORDS * 9

COMPETENCIES_EXPORT_MAX_CATEGORIES = MAX_CATEGORY_COUNT
COMPETENCIES_EXPORT_MIN_CATEGORIES = MIN_CATEGORY_COUNT

# Schema / export alignment (mirror narrative + headline X2).
RG_HEADLINE_MAX_CHARS = HEADLINE_MAX_CHARS
RG_ROLE_NARRATIVE_MAX_CHARS = NARRATIVE_MAX_CHARS
# Longest locked-copy early-career SSOT bullet is ~390 chars; the export schema
# must not silently mutate locked sections that final assembly preserves verbatim.
RG_BULLET_MAX_CHARS = 420

__all__ = [
    "COMPETENCIES_EXPORT_MAX_CATEGORIES",
    "COMPETENCIES_EXPORT_MIN_CATEGORIES",
    "EXEC_SUMMARY_EXPORT_MAX_CHARS",
    "EXEC_SUMMARY_EXPORT_MAX_SENTENCES",
    "EXEC_SUMMARY_EXPORT_MAX_WORDS",
    "EXEC_SUMMARY_EXPORT_MIN_SENTENCES",
    "EXEC_SUMMARY_EXPORT_MIN_WORDS",
    "RG_BULLET_MAX_CHARS",
    "RG_HEADLINE_MAX_CHARS",
    "RG_ROLE_NARRATIVE_MAX_CHARS",
    "NARRATIVE_MAX_WORDS",
]
