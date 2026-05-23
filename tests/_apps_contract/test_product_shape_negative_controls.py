"""Negative controls — fail if retired shape language or export choke regressions return."""

from __future__ import annotations

import re
from pathlib import Path

from apps_rg.l2_recipe import modular_rg_output_builder as mob
from apps_rg.runtime.sections.section_product_shape_export_bounds import EXEC_SUMMARY_EXPORT_MAX_WORDS
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape
def test_live_judge_packet_has_no_four_sentence_valid() -> None:
    judge_path = (
        Path(__file__).resolve().parents[2]
        / "apps_rg"
        / "runtime"
        / "judges"
        / "executive_summary_judge_packet.py"
    )
    text = judge_path.read_text(encoding="utf-8")
    assert "4 sentences is valid" not in text.lower()


def test_modular_export_source_allows_ssot_word_band() -> None:
    text = Path(mob.__file__).read_text(encoding="utf-8")
    assert f"wc > {EXEC_SUMMARY_EXPORT_MAX_WORDS}" in text or "EXEC_SUMMARY_EXPORT_MAX_WORDS" in text
    assert "wc > 60" not in text


def test_unify_template_yaml_requires_heavy_equals_two() -> None:
    tpl = (
        Path(__file__).resolve().parents[2]
        / "apps_rg"
        / "prompt_assembly"
        / "templates"
        / "unify_bullet_tailor_v1.yaml"
    )
    body = tpl.read_text(encoding="utf-8")
    assert "HEAVY == 2" in body
    assert re.search(r"HEAVY\s*<=\s*3", body) is None


def test_ibm_shape_lists_word_budget() -> None:
    assert "x2_ibm_narrative_word_budget" in section_product_shape("ibm_narrative").bounds_gate_ids


def test_unify_bullets_x2_source_does_not_emit_max_heavy_three() -> None:
    src = Path(
        Path(__file__).resolve().parents[2]
        / "apps_rg"
        / "runtime"
        / "validators"
        / "unify_bullets_x2.py"
    ).read_text(encoding="utf-8")
    assert "x2_unify_max_heavy_3 retired" in src or "x2_unify_max_heavy_3" not in src.split("add(")


def test_prompt_registry_exec_summary_no_four_five_band() -> None:
    reg = (
        Path(__file__).resolve().parents[2]
        / "apps_rg"
        / "prompt_assembly"
        / "prompt_registry.yaml"
    )
    body = reg.read_text(encoding="utf-8")
    assert "4–5 dense" not in body
    assert "exactly six" in body.lower() or "six sentences" in body.lower()


def test_competencies_regen_no_all_eight_categories() -> None:
    src = (
        Path(__file__).resolve().parents[2]
        / "apps_rg"
        / "runtime"
        / "sections"
        / "competencies_lane_runtime.py"
    ).read_text(encoding="utf-8")
    assert "ALL eight categories" not in src
    assert "6–8" in src or "6-8" in src
