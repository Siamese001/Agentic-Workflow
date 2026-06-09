"""W1 (plan prompt-gate-ssot-consolidation-e7c9a2): SECTION_CONSTRAINTS is the per-lane numeric SSOT.

These tests are the anti-drift guarantee: every value in ``SECTION_CONSTRAINTS`` MUST equal the
canonical owner constant it is sourced from, and the map MUST cover every generated lane. If a future
edit replaces a reference with a re-typed literal that later diverges from its owner, these tests fail.
"""

from __future__ import annotations

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    FINAL_BULLET_COUNT,
    SC_PATH_COUNT_BY_LANE,
)
from apps_rg.runtime.sections import section_product_shape_ssot as ssot
from apps_rg.runtime.sections.competencies_rigor import (
    CANDIDATE_CATEGORY_COUNT,
    MAX_CATEGORY_COUNT,
    MAX_ITEMS_PER_CATEGORY,
    MIN_CATEGORY_COUNT,
    MIN_ITEMS_PER_CATEGORY,
)
from apps_rg.runtime.validators.competencies_quality_x2 import GENERIC_CATEGORY_MIN_GRAPH_TERMS
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MAX_SENTENCES,
    EXEC_SUMMARY_MAX_WORDS,
    EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE,
    EXEC_SUMMARY_MIN_SENTENCES,
)

_BULLET_LANES = ("unify_bullets", "ibm_bullets", "insurtech_bullets", "ey_bullets")
_NARRATIVE_LANES = ("unify_narrative", "ibm_narrative", "insurtech_narrative", "ey_narrative")


def test_every_generated_lane_has_constraints() -> None:
    missing = [lane for lane in GENERATED_LANES if lane not in ssot.SECTION_CONSTRAINTS]
    assert not missing, f"GENERATED_LANES missing from SECTION_CONSTRAINTS: {missing}"


def test_exec_summary_values_track_owner_constants() -> None:
    c = ssot.SECTION_CONSTRAINTS["executive_summary"]
    assert c["min_sentences"] == EXEC_SUMMARY_MIN_SENTENCES
    assert c["max_sentences"] == EXEC_SUMMARY_MAX_SENTENCES
    assert c["max_words"] == EXEC_SUMMARY_MAX_WORDS
    assert c["max_words_per_sentence"] == EXEC_SUMMARY_MAX_WORDS_PER_SENTENCE
    # W0-C: one claim_ledger row per displayed sentence.
    assert c["claim_ledger_rows"] == EXEC_SUMMARY_MAX_SENTENCES


def test_headline_values_track_owner_constants() -> None:
    c = ssot.SECTION_CONSTRAINTS["headline"]
    assert c["word_min"] == ssot.HEADLINE_WORD_MIN
    assert c["word_max"] == ssot.HEADLINE_WORD_MAX
    assert c["max_chars"] == ssot.HEADLINE_MAX_CHARS
    assert c["segment_count"] == ssot.HEADLINE_SEGMENT_COUNT
    assert c["pipe_separators"] == ssot.HEADLINE_PIPE_SEPARATORS


def test_competencies_values_track_owner_constants() -> None:
    c = ssot.SECTION_CONSTRAINTS["competencies"]
    assert c["category_min"] == MIN_CATEGORY_COUNT
    assert c["category_max"] == MAX_CATEGORY_COUNT
    assert c["candidate_category_count"] == CANDIDATE_CATEGORY_COUNT
    assert c["items_min"] == MIN_ITEMS_PER_CATEGORY
    assert c["items_max"] == MAX_ITEMS_PER_CATEGORY
    assert c["generic_min_graph_terms"] == GENERIC_CATEGORY_MIN_GRAPH_TERMS
    # The 6->8 migration (W0-B) is complete: fixed band, not a range.
    assert c["category_min"] == c["category_max"] == 8


def test_bullet_lane_values_track_owner_constants() -> None:
    for lane in _BULLET_LANES:
        c = ssot.SECTION_CONSTRAINTS[lane]
        assert c["final_count"] == FINAL_BULLET_COUNT[lane], lane
        assert c["sc_pool_paths"] == SC_PATH_COUNT_BY_LANE[lane], lane
        # sourced, not the .get() default
        assert c["final_count"] > 0 and c["sc_pool_paths"] > 0, lane


def test_narrative_lane_values_track_owner_constants() -> None:
    for lane in _NARRATIVE_LANES:
        c = ssot.SECTION_CONSTRAINTS[lane]
        assert c["max_words"] == ssot.NARRATIVE_MAX_WORDS, lane
        assert c["max_chars"] == ssot.NARRATIVE_MAX_CHARS, lane
        assert c["preferred_word_min"] == ssot.NARRATIVE_PREFERRED_WORD_MIN, lane
        assert c["preferred_word_max"] == ssot.NARRATIVE_PREFERRED_WORD_MAX, lane


def test_accessor_returns_copy_and_empty_for_unknown() -> None:
    got = ssot.section_numeric_constraints("executive_summary")
    assert got == ssot.SECTION_CONSTRAINTS["executive_summary"]
    got["max_words"] = -1  # mutating the copy must not touch the SSOT
    assert ssot.SECTION_CONSTRAINTS["executive_summary"]["max_words"] == EXEC_SUMMARY_MAX_WORDS
    # locked-deterministic / unknown sections carry no numeric constraints
    assert ssot.section_numeric_constraints("education") == {}
    assert ssot.section_numeric_constraints("") == {}
