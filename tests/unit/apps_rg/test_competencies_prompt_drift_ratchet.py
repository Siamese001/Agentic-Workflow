"""Drift ratchet: competencies PA slots must not restate X2 gate catalogs in static slots."""

from __future__ import annotations

import os
import re
from pathlib import Path

from apps_rg.runtime.sections.competencies_pa import compile_competencies_prompt, load_competencies_template_slots
from apps_rg.runtime.sections.competency_capability_evidence import (
    attach_competency_bundles_to_proof_pool_metadata,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)
from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / "apps_rg" / "prompt_assembly" / "templates" / "competency_selector_v2.pa_slots.yaml"

_X2_GATE_ID = re.compile(r"\bx2_competencies_[a-z0-9_]+\b")
_X2_COMPANION_GATE = re.compile(r"\bx2_competency_[a-z0-9_]+\b")


def _slot_body(raw: str, slot: str) -> str:
    marker = f"  {slot}: |"
    start = raw.index(marker)
    rest = raw[start + len(marker) :]
    end = rest.find("\n  ") if "\n  " in rest else len(rest)
    return rest[:end].strip()


def _competencies_proof_meta() -> dict:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO,
        section_id="competencies",
        target_role="SVP Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
        briefing_text="regulated enterprise",
    )
    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
        "selected_graph_evidence_plan": plan,
    }
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=str(meta["graph_ref"]),
        ledger_ref="apps_rg/fact_inventory/candidate_fact_ledger.json",
        skills_authority_status="PASS",
    )
    return attach_competency_bundles_to_proof_pool_metadata(meta, section_id="competencies")


def test_template_markers_and_pa_core_law_ref():
    raw = TEMPLATE.read_text(encoding="utf-8")
    assert "COMPETENCIES_PROMPT_CORE_LAW_V3" in raw
    assert "pa_core_law_v1.yaml" in raw
    assert raw.count("<proof_law_v1>") == 1
    assert "COMPETENCY SELECTOR — SOVEREIGN CONSTRAINTS" not in raw


def test_template_static_slots_contain_no_x2_competencies_gate_literals():
    raw = TEMPLATE.read_text(encoding="utf-8")
    for slot in ("I0", "S0", "D0", "E0", "Y0"):
        body = _slot_body(raw, slot)
        hits = _X2_GATE_ID.findall(body) + _X2_COMPANION_GATE.findall(body)
        assert not hits, f"{slot} must not list competencies X2 gate IDs: {hits}"


def test_static_competencies_slots_under_core_law_budget():
    slots = load_competencies_template_slots()
    static_est = sum(
        estimate_tokens_approximate(slots[k]) for k in ("S0", "D0", "I0", "E0", "Y0") if k in slots
    )
    assert static_est < 2500, f"competencies static slots exceed core-law budget: {static_est}"


def test_compiled_prompt_lists_x2_competencies_gates_only_under_product_shape():
    from apps_rg.runtime.spine.front_contracts import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    os.environ.setdefault("PYTEST_CURRENT_TEST", "test_competencies_prompt_drift_ratchet")
    activate_fixture_dev_bypass(non_product_certified=True)
    payload = {
        "product_visible": False,
        "run_id": "competencies_drift_ratchet",
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI platform",
        "briefing": "regulated enterprise",
        "selected_fact_plan": {
            "section_id": "competencies",
            "selection_method": "test",
            "required_fact_ids": ["bul_unify_001"],
            "facts": [],
        },
        "proof_pool_metadata": _competencies_proof_meta(),
        "allowed_fact_ids": ["bul_unify_001"],
    }
    out = compile_competencies_prompt(
        payload,
        companion_context="",
        fact_lines="- bul_unify_001: Example bullet with agentic platform delivery",
        run_id="competencies_drift_ratchet",
    )
    content = out.artifact.messages[0]["content"]
    assert "PRODUCT_SHAPE" in content
    ps_idx = content.index("PRODUCT_SHAPE")
    i0_idx = content.find("<!-- SLOT: I0 -->")
    i0_end = content.find("<!-- SLOT: C0 -->", i0_idx)
    i0_seg = content[i0_idx:i0_end] if i0_idx >= 0 and i0_end > i0_idx else ""
    assert not _X2_GATE_ID.search(i0_seg)
    assert not _X2_COMPANION_GATE.search(i0_seg)
    assert "x2_competencies_min_category_count" in content[ps_idx:]
    deactivate_fixture_dev_bypass()
