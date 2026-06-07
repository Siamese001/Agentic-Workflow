"""Unit tests for apps_rg.runtime.sections.selected_role_fact_set (W1 SRFS helpers)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from apps_rg.runtime.sections import selected_role_fact_set as srfs
def _required_top(
    selected_facts_by_section: dict,
    *,
    selection_id: str = "sel-unit-test",
) -> dict:
    return {
        "selection_id": selection_id,
        "selected_facts_by_section": selected_facts_by_section,
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
    }


def _high_row(
    *,
    cid: str = "bul_unify_001",
    claim: str = "Owned platform delivery.",
    metric_values: list | None = None,
) -> dict:
    return {
        "candidate_fact_id": cid,
        "claim_text": claim,
        "confidence": "HIGH",
        "metric_values": metric_values or [],
        "verification_status": "eligible_high_qualitative",
        "company_lane": "unify",
        "role_families_supported": ["ENGINEERING_PLATFORM"],
    }


def test_section_keys_match_fact_inventory() -> None:
    assert tuple(srfs.SECTION_KEYS) == SECTION_KEYS
    assert len(SECTION_KEYS) == 11


@pytest.mark.parametrize("section_id", SECTION_KEYS)
def test_validate_and_plan_each_section_key(section_id: str, tmp_path: Path) -> None:
    doc = _required_top({section_id: [_high_row(cid=f"bul_unit_{section_id[:3]}")]})
    p = tmp_path / "srfs.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    srfs.validate_section_slice_required(loaded, section_id)
    plan = srfs.build_section_fact_plan(loaded, section_id)
    assert plan["section_id"] == section_id
    assert plan["facts"]
    assert plan["required_fact_ids"]


def test_loader_legacy_list_shape(tmp_path: Path) -> None:
    doc = _required_top({"headline": [_high_row(cid="bul_headline_001")]})
    p = tmp_path / "a.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    rows = srfs.get_section_fact_slice(loaded, "headline")
    assert len(rows) == 1
    assert rows[0]["candidate_fact_id"] == "bul_headline_001"


def test_loader_nested_facts_shape(tmp_path: Path) -> None:
    doc = _required_top({"headline": {"facts": [_high_row(cid="bul_nested_001")]}})
    p = tmp_path / "b.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    rows = srfs.get_section_fact_slice(loaded, "headline")
    assert len(rows) == 1
    assert rows[0]["candidate_fact_id"] == "bul_nested_001"


def test_missing_section_key_fails_validate(tmp_path: Path) -> None:
    doc = _required_top({"headline": [_high_row()]})
    p = tmp_path / "c.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="missing required section slice"):
        srfs.validate_section_slice_required(loaded, "executive_summary")


def test_empty_section_slice_fails_validate(tmp_path: Path) -> None:
    doc = _required_top({"headline": []})
    p = tmp_path / "d.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="empty"):
        srfs.validate_section_slice_required(loaded, "headline")


def test_unknown_section_id_get_slice() -> None:
    doc = _required_top({"headline": [_high_row()]})
    with pytest.raises(ValueError, match="unknown section_id"):
        srfs.get_section_fact_slice(doc, "not_a_section")


def test_row_missing_candidate_fact_id_fails_validate(tmp_path: Path) -> None:
    bad = {**_high_row(), "candidate_fact_id": ""}
    doc = _required_top({"headline": [bad]})
    p = tmp_path / "e.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="missing candidate_fact_id"):
        srfs.validate_section_slice_required(loaded, "headline")


def test_allowed_fact_ids_namespace_and_metric_derivative(tmp_path: Path) -> None:
    doc = _required_top(
        {"executive_summary": [_high_row(cid="bul_m_001", metric_values=["15% rev"])]}
    )
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    ordered, allowed = srfs.build_allowed_fact_ids_for_section(loaded, "executive_summary")
    assert "bul_m_001" in allowed
    assert len(ordered) >= 2
    deriv = [x for x in ordered if "_metric_" in x]
    assert len(deriv) == 1
    assert deriv[0].startswith("bul_m_001_metric_")


def test_build_exec_summary_plan_from_in_memory_doc() -> None:
    doc = _required_top(
        {
            "executive_summary": [
                _high_row(cid="bul_exec_a"),
                _high_row(cid="bul_exec_b", claim="second"),
            ]
        }
    )
    plan = srfs.build_section_fact_plan(doc, "executive_summary")
    ordered, allowed = srfs.build_allowed_fact_ids_for_plan_facts(list(plan["facts"]))
    assert len(ordered) >= 2
    assert allowed


def test_load_selected_role_fact_set_raises(tmp_path: Path) -> None:
    p = tmp_path / "gone.json"
    p.write_text("{}")
    with pytest.raises(ValueError, match="SelectedRoleFactSet JSON missing keys"):
        srfs.load_selected_role_fact_set(p)


def test_non_high_row_fails_plan(tmp_path: Path) -> None:
    row = _high_row()
    row["confidence"] = "MEDIUM"
    doc = _required_top({"headline": [row]})
    p = tmp_path / "low.json"
    p.write_text(json.dumps(doc))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="only HIGH"):
        srfs.build_section_fact_plan(loaded, "headline")
