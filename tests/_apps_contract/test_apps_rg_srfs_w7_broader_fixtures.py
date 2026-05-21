"""W7: broader SRFS fixtures and edge-case coverage for W1–W6 behavior.

Pytest-only structural / offline-stub proof. No runtime certification; no full-resume R4 wiring.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from tests._apps_contract.contract_harness_paths import harness_run

from apps_rg.runtime.sections.selected_role_fact_set import (
    get_section_fact_slice,
    load_selected_role_fact_set,
    metric_derivative_fact_id,
    resolve_srfs_section_proof_bundle,
    validate_section_slice_required,
)
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates
from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

from tests._apps_contract.test_apps_rg_srfs_w6_reporting import W6_FIELDS

REPO = Path(__file__).resolve().parents[2]

# Written under repo artifacts for discoverability (same pattern as W3/W4/W6).
W7_FIXTURE_SUBDIR = REPO / "artifacts" / "apps_rg" / "test_fixtures" / "srfs_w7"


def _srfs_shell(selection_id: str) -> dict:
    return {
        "selection_id": selection_id,
        "selected_facts_by_section": {},
        "blocked_facts": [{"fact": {"candidate_fact_id": "blocked_w7_001", "confidence": "LOW"}}],
        "facts_requiring_human_confirmation": [
            {"fact": {"candidate_fact_id": "medium_w7_001", "confidence": "MEDIUM"}},
        ],
        "unsupported_jd_needs": [],
        "confidence_policy": "W7 fixture — HIGH proof rows per section; nested + bare-list shapes tested.",
        "candidate_not_canonical_assertion": True,
        "no_jd_fact_minting_assertion": True,
        "role_family_priorities": [{"role_family": "ENGINEERING_PLATFORM", "score": 9, "evidence_terms": [], "source_channels": []}],
        "competencies_capability_tags_ordered": ["kubernetes", "platform_governance"],
    }


def _high_row(
    candidate_fact_id: str,
    *,
    claim_text: str,
    metric_values: list[str] | None = None,
) -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": claim_text,
        "metric_values": list(metric_values or []),
    }


def realistic_seven_section_rows_bare() -> dict[str, list[dict]]:
    """Representative IDs and copy; one metric-backed row for derivative coverage."""
    return {
        "headline": [
            _high_row("bul_w7_head_001", claim_text="Led global platform modernization at scale."),
        ],
        "executive_summary": [
            _high_row(
                "bul_w7_exec_001",
                claim_text="Grew ARR 22% YoY while cutting infra cost.",
                metric_values=["22% YoY ARR growth", "$4.2M cost takeout"],
            ),
            _high_row("bul_w7_exec_002", claim_text="Board-ready transparency on delivery and risk."),
        ],
        "unify_bullets": [
            _high_row(f"bul_w7_unify_{i:03d}", claim_text=f"Unify chapter achievement {i}.") for i in range(1, 7)
        ],
        "unify_narrative": [
            _high_row("bul_w7_unify_001", claim_text="Primary unify narrative anchor shares bullet pool id."),
            _high_row("unify_narrative_base_w7", claim_text="Synthetic base narrative token allowed in this slice."),
        ],
        "ibm_bullets": [
            _high_row(f"bul_w7_ibm_{i:03d}", claim_text=f"IBM chapter achievement {i}.") for i in range(1, 6)
        ],
        "ibm_narrative": [
            _high_row("bul_w7_ibm_001", claim_text="IBM narrative anchor aligned to first IBM bullet."),
        ],
        "competencies": [
            _high_row("bul_w7_comp_001", claim_text="Core competency proof row for structured output."),
            _high_row("bul_w7_comp_002", claim_text="Secondary proof row for term diversity."),
        ],
    }


def doc_bare_list(selection_id: str = "w7_bare_realistic_v1") -> dict:
    d = _srfs_shell(selection_id)
    rows = realistic_seven_section_rows_bare()
    d["selected_facts_by_section"] = {k: list(rows.get(k) or []) for k in SECTION_KEYS}
    return d


def doc_nested_facts(selection_id: str = "w7_nested_realistic_v1") -> dict:
    """Same logical rows as bare list, nested ``{"facts": [...]}`` per section."""
    d = _srfs_shell(selection_id)
    bare = realistic_seven_section_rows_bare()
    d["selected_facts_by_section"] = {sec: {"facts": list(bare[sec])} for sec in SECTION_KEYS}
    return d


def write_fixture_json(name: str, doc: dict) -> Path:
    W7_FIXTURE_SUBDIR.mkdir(parents=True, exist_ok=True)
    p = W7_FIXTURE_SUBDIR / name
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


@pytest.fixture(scope="module")
def w7_realistic_bare_path() -> Path:
    return write_fixture_json("w7_realistic_bare_list.json", doc_bare_list())


@pytest.fixture(scope="module")
def w7_realistic_nested_path() -> Path:
    return write_fixture_json("w7_realistic_nested_facts.json", doc_nested_facts())


def test_w7_fixture_files_on_disk(w7_realistic_bare_path: Path, w7_realistic_nested_path: Path) -> None:
    assert w7_realistic_bare_path.is_file()
    assert w7_realistic_nested_path.is_file()


def test_w7_bare_vs_nested_resolve_equivalent_allowed_sets(
    w7_realistic_bare_path: Path,
    w7_realistic_nested_path: Path,
) -> None:
    for section in SECTION_KEYS:
        _, o_bare, s_bare, _ = resolve_srfs_section_proof_bundle(w7_realistic_bare_path, section)
        _, o_nested, s_nested, meta_nested = resolve_srfs_section_proof_bundle(w7_realistic_nested_path, section)
        assert s_bare == s_nested, section
        assert o_bare == o_nested, section
        assert meta_nested.get("proof_pool_type") == "selected_role_fact_set"


def test_w7_metric_derivative_ids_in_executive_allowed_set(w7_realistic_bare_path: Path) -> None:
    _plan, ordered, allowed, _ = resolve_srfs_section_proof_bundle(w7_realistic_bare_path, "executive_summary")
    assert "bul_w7_exec_001" in allowed
    mr = "|".join(["22% YoY ARR growth", "$4.2M cost takeout"])
    expected_mid = metric_derivative_fact_id("bul_w7_exec_001", mr)
    assert expected_mid in allowed
    assert expected_mid in ordered


def test_w7_nested_invalid_facts_type_raises(tmp_path: Path) -> None:
    d = doc_bare_list("w7_bad_nested")
    d["selected_facts_by_section"]["headline"] = {"facts": "not_a_list"}  # type: ignore[assignment]
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    doc = load_selected_role_fact_set(p)
    with pytest.raises(ValueError, match="facts must be a list"):
        get_section_fact_slice(doc, "headline")


def test_w7_missing_section_slice_validate_raises(tmp_path: Path) -> None:
    d = doc_bare_list("w7_missing_headline")
    del d["selected_facts_by_section"]["headline"]
    p = tmp_path / "no_headline.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    doc = load_selected_role_fact_set(p)
    with pytest.raises(ValueError, match="missing required section slice"):
        validate_section_slice_required(doc, "headline")


def test_w7_empty_section_slice_validate_raises(tmp_path: Path) -> None:
    d = doc_bare_list("w7_empty_headline")
    d["selected_facts_by_section"]["headline"] = []
    p = tmp_path / "empty_headline.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    doc = load_selected_role_fact_set(p)
    with pytest.raises(ValueError, match="empty"):
        validate_section_slice_required(doc, "headline")


def test_w7_headline_cross_slice_exec_id_fails_gate(tmp_path: Path) -> None:
    d = doc_bare_list("w7_cross_head")
    d["selected_facts_by_section"]["headline"] = [_high_row("bul_w7_head_only", claim_text="Head only.")]
    d["selected_facts_by_section"]["executive_summary"] = [_high_row("bul_w7_exec_isolated", claim_text="Exec.")]
    p = tmp_path / "cross.json"
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    _, _, allowed, _ = resolve_srfs_section_proof_bundle(p, "headline")
    gates = run_headline_x2_gates(
        headline_line="SVP Engineering | A B | C D | E F",
        parsed_output={
            "headline_line": "x",
            "selected_fact_plan": {"facts": [], "required_fact_ids": ["bul_w7_exec_isolated"]},
            "claim_ledger": [{"claim_text": "x", "source_fact_ids": ["bul_w7_exec_isolated"]}],
            "jd_alignment": {"jd_used_as_proof": False, "briefing_used_as_proof": False},
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["bul_w7_exec_isolated"]}],
        jd_text="",
        target_company="",
        target_title="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=allowed,
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    g = by_id["x2_headline_source_fact_ids_within_srfs_slice"]
    assert g.pass_ is False
    assert "bul_w7_exec_isolated" in (g.observed_value.get("out_of_slice_fact_ids") or [])


def test_w7_unify_narrative_synthetic_id_not_in_slice_fails(tmp_path: Path) -> None:
    """``unify_narrative_base_*`` style token must be in the section allowlist when SRFS is active."""
    d = doc_bare_list("w7_narr_syn")
    d["selected_facts_by_section"]["unify_narrative"] = [_high_row("bul_w7_unify_001", claim_text="Only unify bullet id.")]
    p = tmp_path / "narr.json"
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    _, _, allowed, _ = resolve_srfs_section_proof_bundle(p, "unify_narrative")
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="Single sentence about Unify Consulting platforms for enterprise.",
        parsed_output={
            "narrative_sentence": "x",
            "claim_ledger": [],
            "jd_alignment": {
                "selected_jd_themes": ["t"],
                "targeting_rationale": "r",
                "jd_used_as_proof": False,
                "briefing_used_as_proof": False,
                "selected_briefing_themes": [],
            },
            "gap_notes": [],
            "change_log": [],
            "self_check": {},
        },
        claim_ledger=[{"claim_text": "Led platform work.", "source_fact_ids": ["unify_narrative_base_001"]}],
        jd_text="enterprise",
        briefing_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts=None,
        x1d_judges=[],
        allowed_fact_ids=allowed,
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    g = by_id["x2_unify_narrative_source_fact_ids_within_srfs_slice"]
    assert g.pass_ is False
    assert "unify_narrative_base_001" in (g.observed_value.get("out_of_slice_fact_ids") or [])


def test_w7_competencies_term_source_fact_id_and_ids_collected(tmp_path: Path) -> None:
    p = tmp_path / "srfs_co_w7.json"
    p.write_text(
        json.dumps(
            doc_bare_list("w7_co"),
        ),
        encoding="utf-8",
    )
    _, _, allowed, _ = resolve_srfs_section_proof_bundle(p, "competencies")
    competencies = []
    bad_id = "bul_w7_term_bad_src"
    for i in range(8):
        competencies.append(
            {
                "category_label": f"Category {i}",
                "terms": [
                    {
                        "text": f"skill {i}a",
                        "source_fact_id": "bul_w7_comp_001",
                        "source_fact_ids": ["bul_w7_comp_001"],
                    },
                    {
                        "text": f"skill {i}b",
                        "source_fact_id": "bul_w7_comp_001",
                        "source_fact_ids": ["bul_w7_comp_001"],
                    },
                ],
                "source_fact_ids": ["bul_w7_comp_001"],
            }
        )
    competencies[0]["terms"][1]["source_fact_id"] = bad_id
    competencies[0]["terms"][1]["source_fact_ids"] = [bad_id, "bul_w7_comp_001"]
    po = {
        "competencies": competencies,
        "claim_ledger": [{"claim_text": "c", "source_fact_ids": ["bul_w7_comp_001"]} for _ in range(3)],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    cl = [{"claim_text": "c", "source_fact_ids": ["bul_w7_comp_001"]} for _ in range(3)]
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=po,
        claim_ledger=cl,
        jd_text="",
        briefing_text="",
        bullet_texts_lower=[],
        resume_support_blob="bul_w7_comp_001 skill",
        allowed_fact_ids=allowed,
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )
    by_id = {g.gate_id: g for g in gates}
    g = by_id["x2_competencies_source_fact_ids_within_srfs_slice"]
    assert g.pass_ is False
    oos = g.observed_value.get("out_of_slice_fact_ids") or []
    assert bad_id in oos


