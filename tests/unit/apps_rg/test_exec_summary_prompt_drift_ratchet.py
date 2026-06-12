"""Drift ratchet: executive_summary template must not restate X2 gate catalogs in I0/R0."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_pa import load_executive_summary_template_slots

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = (
    REPO / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
)

_X2_GATE_ID = re.compile(r"\bx2_[a-z0-9_]+\b")


def _slot_body(raw: str, slot: str) -> str:
    marker = f"  {slot}: |"
    start = raw.index(marker)
    rest = raw[start + len(marker) :]
    end = rest.find("\n  ") if "\n  " in rest else len(rest)
    return rest[:end].strip()


def test_template_i0_and_r0_contain_no_x2_gate_id_literals():
    raw = TEMPLATE.read_text(encoding="utf-8")
    for slot in ("I0", "R0"):
        body = _slot_body(raw, slot)
        hits = _X2_GATE_ID.findall(body)
        assert not hits, f"{slot} must not list X2 gate IDs (use PRODUCT_SHAPE): {hits}"


def test_compiled_prompt_lists_x2_gates_only_under_product_shape():
    payload = {
        "product_visible": False,
        "run_id": "drift_ratchet_run",
        "target_title": "SVP",
        "target_company": "Co",
        "jd_text": "jd",
        "briefing": "brief",
        "allowed_fact_ids": ["f1"],
        "selected_fact_plan": {"facts": [{"fact_id": "f1", "claim_text": "Built platforms."}]},
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "PRODUCT_SHAPE" in content
    ps_idx = content.index("PRODUCT_SHAPE")
    i0_idx = content.find("<!-- SLOT: I0 -->")
    i0_end = content.find("<!-- SLOT: C0 -->", i0_idx)
    i0_seg = content[i0_idx:i0_end] if i0_idx >= 0 and i0_end > i0_idx else ""
    assert not _X2_GATE_ID.search(i0_seg), "I0 compiled segment must not enumerate x2_ gates"
    after_ps = content[ps_idx:]
    assert "x2_exec_summary_sentence_count_6" in after_ps


def test_graph_evidence_style_block_compact_skips_gate_catalog_and_full_exemplars():
    from apps_rg.runtime.sections.executive_summary_pa import format_graph_evidence_style_quality_block

    block = format_graph_evidence_style_quality_block()
    assert "srfs_product_shape" not in block
    assert "<srfs_style_only_oneshot" not in block
    assert "<exemplar_platform_led>" not in block
    assert "PRODUCT_SHAPE" in block
    assert len(block) < 3500


def test_static_slots_under_core_law_budget():
    slots = load_executive_summary_template_slots()
    from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate

    static_est = sum(estimate_tokens_approximate(slots[k]) for k in ("S0", "D0", "I0", "E0", "Y0", "R0"))
    assert static_est < 7500, f"static slots exceed core-law budget: {static_est}"
