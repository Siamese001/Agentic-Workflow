"""W9 section_prompt_contracts exist for all modular lanes (W5 plan closure)."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
CONTRACTS = REPO / "apps_rg" / "prompt_assembly" / "section_prompt_contracts"

W9_LANES = (
    "executive_summary",
    "headline",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)


def test_w9_section_prompt_contracts_exist_for_all_modular_lanes():
    for section in W9_LANES:
        path = CONTRACTS / f"{section}.contract.yaml"
        assert path.is_file(), f"missing W9 contract: {path}"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        assert data.get("section_id") == section
        assert data.get("apps_rg_prompt_template_ref")


def test_audit_json_reports_zero_p0_and_no_dual_authority_on_examples_lanes():
    audit_path = REPO / "artifacts" / "apps_rg" / "plans" / "prompt_assembly_ssot_gap_audit.json"
    assert audit_path.is_file(), "run: python ops_scripts/apps_rg/prompt_assembly_ssot_gap_audit.py"
    import json

    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert data.get("p0_count") == 0
    for lane in data.get("w9_lanes") or []:
        if lane.get("examples_file"):
            assert lane.get("examples_wired_at_compile") is True
            assert lane.get("dual_authority_risk") is False
