"""W4 — executable manifest coverage + regen cycles observability."""

from __future__ import annotations

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.executive_summary_regen_observability import (
    audit_judge_feedback_pack,
    finalize_judge_regen_cycles_receipt,
    normalize_cycle_record_observability,
    pack_judge_feedback_with_stats,
)
from apps_rg.runtime.sections.section_prompt_authority_ssot import (
    EXECUTABLE_PROMPT_SOURCES,
    assert_all_generated_lanes_executable_corpus_non_empty,
    collect_executable_prompt_corpus,
)


def test_executable_prompt_sources_cover_all_generated_lanes() -> None:
    assert set(EXECUTABLE_PROMPT_SOURCES) == set(GENERATED_LANES)
    for lane in GENERATED_LANES:
        sources = EXECUTABLE_PROMPT_SOURCES[lane]
        assert sources, f"{lane}: missing sources"
        kinds = {s["kind"] for s in sources}
        assert "yaml_template" in kinds


def test_headline_executable_corpus_includes_u0_snippet() -> None:
    corpus = collect_executable_prompt_corpus("headline")
    assert "SVP Engineering" in corpus
    assert "headline_line" in corpus
    assert len(corpus.strip()) >= 200


def test_assert_all_generated_lanes_executable_corpus_non_empty() -> None:
    assert_all_generated_lanes_executable_corpus_non_empty()


def test_pack_judge_feedback_with_stats_includes_all_lines() -> None:
    sections = {
        "judge_feedback": [f"line-{i}" for i in range(40)],
        "dimension": [],
        "floors": [],
        "guards": [],
    }
    packed, stats = pack_judge_feedback_with_stats(sections)
    assert stats["judge_feedback_lines_total"] == 40
    assert stats["judge_feedback_lines_included"] == 40
    assert stats["judge_feedback_lines_dropped"] == 0
    assert len(packed) == 40


def test_finalize_judge_regen_cycles_receipt_rollups() -> None:
    receipt = finalize_judge_regen_cycles_receipt(
        {
            "cycles": [
                {
                    "cycle": 1,
                    "draft_parse_ok": True,
                    "accepted": True,
                    "publish_eligible": True,
                    "candidate_digest": "abc123",
                },
            ],
            "regen_outcome": "improved",
            "final_publish_baseline": "regen_cycle_1",
        },
        scratch_candidate_digest="scratch-digest",
        published_candidate_digest="pub-digest",
    )
    assert receipt["judge_regen_cycles"]
    assert receipt["publishable_baseline_hash"]
    assert receipt["rewrite_from"] == "abc123"
    assert "use_rejected_as_negative_example" in receipt


def test_normalize_cycle_record_post_gate_accepted_semantics() -> None:
    row = normalize_cycle_record_observability(
        {"draft_parse_ok": True, "publish_eligible": True, "g3_passed": True},
    )
    assert row["accepted"] is True
    row2 = normalize_cycle_record_observability(
        {"draft_parse_ok": True, "accepted": True, "publish_eligible": False},
    )
    assert row2["accepted"] is False


def test_audit_judge_feedback_pack_shape() -> None:
    judges = [
        {
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "evaluator_mode": "MODEL_BACKED",
            "findings": ["S6 thin."],
            "remediation_suggestions": ["Strengthen S6."],
        },
    ]
    stats = audit_judge_feedback_pack(judges)
    assert stats["judge_feedback_lines_total"] >= 1
