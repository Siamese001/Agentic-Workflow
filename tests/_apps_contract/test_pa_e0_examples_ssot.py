"""PA E0 SSOT: compiled prompts must hydrate examples from apps_rg/prompt_assembly/examples/*.yaml."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.prompt_assembly.e0_examples import (
    build_executive_summary_e0,
    example_after_text,
    load_examples_by_id,
    resolve_e0_for_section,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_pa import load_executive_summary_template_slots
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

REPO = Path(__file__).resolve().parents[2]


def _minimal_exec_payload(*, run_id: str = "e0_ssot_run") -> dict:
    return {
        "product_visible": False,
        "run_id": run_id,
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI platform leadership",
        "briefing": "regulated enterprise environment",
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "es_e0_fact_001",
                    "claim_text": "Delivered governed agentic AI platforms at scale.",
                },
            ],
            "required_fact_ids": ["es_e0_fact_001"],
        },
    }


def test_gold_yaml_has_at_least_four_sentences():
    gold = example_after_text("executive_summary", "exec_summary_gold_base_resume_001")
    assert len(split_sentences(gold)) >= 4


def test_compiled_e0_includes_yaml_gold_not_template_stub():
    gold = example_after_text("executive_summary", "exec_summary_gold_base_resume_001")
    assert "productized AI revenue" in gold
    e0 = build_executive_summary_e0()
    assert "productized AI revenue" in e0
    assert "runtime architecture spanning orchestration, retrieval, policy enforcement" not in e0


def test_resolve_e0_ignores_template_inline_positive_stubs():
    template_e0 = load_executive_summary_template_slots().get("E0", "")
    assert "runtime architecture spanning orchestration" in template_e0 or "hydrated at compile" in template_e0
    resolved = resolve_e0_for_section("executive_summary", template_e0)
    assert "productized AI revenue" in resolved
    if "runtime architecture spanning orchestration" in template_e0:
        assert "runtime architecture spanning orchestration, retrieval, policy enforcement" not in resolved


def test_compile_executive_summary_prompt_contains_hydrated_gold():
    payload = _minimal_exec_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "E0 hydrated at compile" in content or "productized AI revenue" in content
    assert "<!-- SLOT: E0 -->" in content
    e0_start = content.index("<!-- SLOT: E0 -->")
    e0_end = content.index("<!-- SLOT:", e0_start + 10)
    e0_seg = content[e0_start:e0_end]
    assert "exec_summary_gold_base_resume_001" in e0_seg
    assert len(split_sentences(example_after_text("executive_summary", "exec_summary_gold_base_resume_001"))) >= 4
    gold_in_prompt = e0_seg
    assert "productized AI revenue" in gold_in_prompt


def test_competencies_e0_includes_examples_catalog():
    e0 = resolve_e0_for_section("competencies", "# stub")
    assert "competencies_pos_001" in e0
    assert "competencies_neg_001" in e0


def test_unify_lanes_share_unify_examples():
    bullets = resolve_e0_for_section("unify_bullets", "")
    narrative = resolve_e0_for_section("unify_narrative", "")
    assert "unify_pos_001" in bullets and "unify_pos_001" in narrative
    assert "unify_neg_001" in bullets


def test_shared_ids_use_yaml_body_for_gold():
    by_id = load_examples_by_id("executive_summary")
    row = by_id["exec_summary_gold_base_resume_001"]
    after = str(row.get("after") or "").strip()
    e0 = build_executive_summary_e0()
    assert after[:80] in e0.replace("\n", " ").replace("  ", " ")


@pytest.mark.parametrize(
    "section,example_id,min_sentences",
    [
        ("executive_summary", "exec_summary_gold_base_resume_001", 4),
        ("executive_summary", "exec_summary_pos_credibility_implied_001", 4),
        ("executive_summary", "exec_summary_pos_outcomes_led_001", 4),
    ],
)
def test_positive_compile_ids_meet_sentence_band(section: str, example_id: str, min_sentences: int):
    text = example_after_text(section, example_id)
    assert len(split_sentences(text)) >= min_sentences
