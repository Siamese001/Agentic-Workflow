"""Edge-case contract tests for SSOT product shape (export, X2, E0, graph-only, unify, IBM)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps_rg.l2_recipe import modular_rg_output_builder as mob
from apps_rg.l2_recipe.modular_rg_output_builder import _competencies_to_skills, _maybe_truncate_bullet_text
from apps_rg.prompt_assembly.e0_examples import (
    _EXEC_SUMMARY_POSITIVE_COMPILE_IDS,
    build_executive_summary_e0,
    example_after_text,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_export_bounds import (
    COMPETENCIES_EXPORT_MAX_CATEGORIES,
    EXEC_SUMMARY_EXPORT_MAX_WORDS,
    RG_BULLET_MAX_CHARS,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    EXEC_SUMMARY_MAX_WORDS,
    HEADLINE_MAX_CHARS,
    MAX_CATEGORY_COUNT,
    NARRATIVE_MAX_CHARS,
    NARRATIVE_MAX_WORDS,
    RETIRED_UNIFY_BULLETS_X2_GATE_IDS,
    section_product_shape,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EXEC_SUMMARY_MIN_SENTENCES,
    check_exec_summary_sentence_count_6,
    check_synthesis_quality,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences
from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates
from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates
from tests._apps_contract.product_shape_test_support import (
    build_export,
    fake_x1d_judges,
    gate_map,
    minimal_lane_bundle,
    minimal_unify_bullets_payload,
    six_sentence_exec_text,
)
from tests.unit.apps_rg.section_rigor.lane_registry import spec_for_lane

_REPO = Path(__file__).resolve().parents[2]


def test_export_bounds_module_matches_x2_ssot() -> None:
    assert EXEC_SUMMARY_EXPORT_MAX_WORDS == EXEC_SUMMARY_MAX_WORDS
    assert COMPETENCIES_EXPORT_MAX_CATEGORIES == MAX_CATEGORY_COUNT


def test_export_rejects_exec_summary_over_140_words(tmp_path: Path) -> None:
    lanes = minimal_lane_bundle()
    lanes["executive_summary"]["resume_display_text"] = six_sentence_exec_text(word_repeat=30)
    res = build_export(tmp_path, lanes, run_suffix="exec_over_words")
    assert res.ok is False
    assert res.failure_reason == "executive_summary_out_of_rg_bounds"
    assert res.merge_receipt.get("export_bounds", {}).get("max_words") == EXEC_SUMMARY_EXPORT_MAX_WORDS


def test_export_accepts_exec_summary_at_max_word_boundary(tmp_path: Path) -> None:
    lanes = minimal_lane_bundle()
    text = six_sentence_exec_text(word_repeat=3)
    wc = len(text.split())
    assert wc <= EXEC_SUMMARY_EXPORT_MAX_WORDS, f"fixture wc={wc} must be <= max for boundary test"
    lanes["executive_summary"]["resume_display_text"] = text
    res = build_export(tmp_path, lanes, run_suffix="exec_at_boundary")
    assert res.ok is True, res.failure_reason


def test_competencies_to_skills_preserves_eight_categories() -> None:
    competencies = [
        {
            "category_label": f"Category {i}",
            "terms": [{"text": f"Skill {i}a"}, {"text": f"Skill {i}b"}],
        }
        for i in range(8)
    ]
    out = _competencies_to_skills(competencies)
    assert out is not None
    assert len(out["categories"]) == 8


def test_competencies_to_skills_does_not_cap_at_six() -> None:
    competencies = [
        {"category_label": f"Category {i}", "terms": [{"text": "term"}]} for i in range(8)
    ]
    out = _competencies_to_skills(competencies)
    assert out is not None
    assert len(out["categories"]) == MAX_CATEGORY_COUNT
    assert len(out["categories"]) > 6


def test_bullet_truncate_records_export_shape_warning() -> None:
    warnings: list[str] = []
    long_text = "x" * (RG_BULLET_MAX_CHARS + 50)
    out = _maybe_truncate_bullet_text(long_text, warnings)
    assert len(out) == RG_BULLET_MAX_CHARS
    assert "bullet_text_truncated" in warnings


def test_unify_heavy_three_fails_rewrite_distribution_gate() -> None:
    bullets, ledger, parsed = minimal_unify_bullets_payload(heavy=3, moderate=2, light_protected=1)
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids={b["bullet_id"] for b in bullets},
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=fake_x1d_judges(),
    )
    by_id = gate_map(gates)
    assert by_id.get("x2_unify_rewrite_distribution_valid") is False


def test_unify_heavy_two_passes_rewrite_distribution_gate() -> None:
    bullets, ledger, parsed = minimal_unify_bullets_payload(heavy=2, moderate=3, light_protected=1)
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids={b["bullet_id"] for b in bullets},
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=fake_x1d_judges(),
    )
    by_id = gate_map(gates)
    assert by_id.get("x2_unify_rewrite_distribution_valid") is True


def test_unify_x2_does_not_emit_retired_max_heavy_three_gate() -> None:
    bullets, ledger, parsed = minimal_unify_bullets_payload(heavy=2, moderate=3, light_protected=1)
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids={b["bullet_id"] for b in bullets},
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=fake_x1d_judges(),
    )
    emitted = {g.gate_id for g in gates}
    assert not RETIRED_UNIFY_BULLETS_X2_GATE_IDS.intersection(emitted)


def test_ibm_narrative_word_budget_fails_over_360_chars() -> None:
    narrative = "At IBM, " + ("enterprise " * 80) + "."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative},
        raw_output="{}",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        runtime_generation_status="REAL_LLM",
    )
    assert gate_map(gates).get("x2_ibm_narrative_word_budget") is False


def test_ibm_narrative_exactly_one_sentence_fails_two_sentences() -> None:
    narrative = "At IBM, modernized analytics platforms. The team delivered strong uptime."
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[{"claim_text": narrative, "source_fact_ids": ["bul_ibm_001"]}],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative},
        raw_output="{}",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        runtime_generation_status="REAL_LLM",
    )
    by_id = gate_map(gates)
    assert by_id.get("x2_ibm_narrative_exactly_one_sentence") is False


def test_unify_narrative_word_budget_fails_over_58_words() -> None:
    words = " ".join(["delivery"] * 60)
    narrative = f"At Unify, {words}."
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        claim_ledger=[{"claim_text": narrative, "source_fact_ids": ["bul_unify_001"]}],
        companion_bullet_texts="",
        jd_text="Targeting only.",
        parsed_output={"narrative_sentence": narrative},
        raw_output="{}",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        runtime_generation_status="REAL_LLM",
    )
    assert gate_map(gates).get("x2_unify_narrative_word_budget") is False


def test_five_sentence_exec_summary_fails_x2_sentence_count() -> None:
    text = " ".join([f"Sentence {i} states platform delivery outcomes." for i in range(1, 6)])
    ok, reason = check_exec_summary_sentence_count_6(text)
    assert ok is False
    assert reason is not None
    assert "6" in reason


def test_synthesis_quality_under_six_sentences_reports_exactly_six() -> None:
    text = "One sentence only."
    ok, reason = check_synthesis_quality(text)
    assert ok is False
    assert reason is not None
    assert "exactly 6" in reason.lower()


def test_graph_only_source_never_caps_below_ssot_min_sentences() -> None:
    from apps_rg.runtime.sections import exec_summary_graph_only_quality as gq

    src = Path(gq.__file__).read_text(encoding="utf-8")
    assert "sentences[:5]" not in src
    assert "sentences[:6]" in src or "EXEC_SUMMARY_MAX_SENTENCES" in src
    assert "4–5" not in src and "4-5" not in src


@pytest.mark.parametrize("example_id", list(_EXEC_SUMMARY_POSITIVE_COMPILE_IDS))
def test_e0_positive_compile_examples_have_six_sentences(example_id: str) -> None:
    after = example_after_text("executive_summary", example_id)
    assert after
    count = len(split_sentences(after))
    assert count == EXEC_SUMMARY_MIN_SENTENCES, (
        f"{example_id} has {count} sentences; E0 must teach exactly {EXEC_SUMMARY_MIN_SENTENCES}"
    )


def test_build_executive_summary_e0_has_no_retired_four_five_band() -> None:
    body = build_executive_summary_e0()
    assert not re.search(r"4\s*[-–]\s*5\s+dense", body, re.IGNORECASE)
    assert "4 sentences is valid" not in body.lower()


def test_strategic_tailor_v2_marked_non_product_planning_only() -> None:
    path = _REPO / "apps_rg" / "prompt_assembly" / "templates" / "strategic_tailor_v2.yaml"
    head = path.read_text(encoding="utf-8")[:500]
    assert "NON_PRODUCT_PLANNING_ONLY" in head


def test_modular_resume_generation_marked_smoke_only() -> None:
    path = _REPO / "apps_rg" / "l2_recipe" / "modular_resume_generation.py"
    head = path.read_text(encoding="utf-8")[:400]
    assert "PHASE0_SMOKE_ONLY" in head


def test_ibm_template_asserts_exactly_one_sentence_period() -> None:
    path = _REPO / "apps_rg" / "prompt_assembly" / "templates" / "ibm_position_narrative_v1.yaml"
    body = path.read_text(encoding="utf-8")
    assert "count('.') == 1" in body
    assert re.search(r"count\('\.'\)\s*>=\s*1", body) is None


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_lane_registry_includes_all_ssot_bounds_gates(lane: str) -> None:
    shape = section_product_shape(lane)
    spec = spec_for_lane(lane)
    missing = [g for g in shape.bounds_gate_ids if g not in spec.critical_gates]
    assert not missing, f"{lane} missing bounds gates in registry: {missing}"


def test_headline_ssot_max_chars_matches_x2_threshold() -> None:
    assert HEADLINE_MAX_CHARS == 140


def test_narrative_ssot_bounds_match_ibm_and_unify_x2() -> None:
    assert NARRATIVE_MAX_WORDS == 58
    assert NARRATIVE_MAX_CHARS == 360


def test_export_builder_imports_ssot_bounds_symbols() -> None:
    src = Path(mob.__file__).read_text(encoding="utf-8")
    for sym in (
        "EXEC_SUMMARY_EXPORT_MAX_WORDS",
        "COMPETENCIES_EXPORT_MAX_CATEGORIES",
        "RG_BULLET_MAX_CHARS",
    ):
        assert sym in src
