"""Tests for apps_* repair profile contracts.

Plan: apps-core-contract-rectification-a8f3c2 Phase 1.5
Verifies: schema compliance, all 8 apps covered, field presence, refs format.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

ALL_APPS = [
    "apps_qna",
    "apps_rg",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_exec",
    "apps_eval",
    "apps_underwriting_ai",
]

EXPECTED_TASK_CLASS = {
    "apps_qna": "qna_pack_build",
    "apps_rg": "resume_generation",
    "apps_lic": "outreach_message",
    "apps_research": "company_brief",
    "apps_rfp": "rfp_response",
    "apps_exec": "brief_assembly",
    "apps_eval": "eval_self",
    "apps_underwriting_ai": "underwriting_decision",
}


def _load_repair_profile(app_id: str) -> dict[str, Any]:
    path = REPO_ROOT / app_id / "config" / "domain_contract" / "repair_profiles.yaml"
    assert path.is_file(), f"repair_profiles.yaml missing for {app_id}: {path}"
    with path.open() as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict), f"{app_id}: repair_profiles.yaml must be a YAML dict"
    return data


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_file_exists(app_id: str) -> None:
    path = REPO_ROOT / app_id / "config" / "domain_contract" / "repair_profiles.yaml"
    assert path.is_file(), f"repair_profiles.yaml missing for {app_id}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_required_fields(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    for field in ("repair_profile_id", "app_id", "version", "status", "repair_scenarios"):
        assert field in data, f"{app_id}: missing required field {field!r}"


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_id_format(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    profile_id = data["repair_profile_id"]
    pattern = re.compile(r"^rp::.+::.+::v\d+$")
    assert pattern.match(profile_id), (
        f"{app_id}: repair_profile_id {profile_id!r} does not match rp::<app>::<task>::vN format"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_app_id_matches(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    assert data["app_id"] == app_id, (
        f"repair_profile app_id {data['app_id']!r} does not match expected {app_id!r}"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_status_valid(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    assert data["status"] in {"draft", "active", "deprecated"}, (
        f"{app_id}: invalid status {data['status']!r}"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_has_min_scenarios(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    scenarios = data.get("repair_scenarios", [])
    assert isinstance(scenarios, list), f"{app_id}: repair_scenarios must be a list"
    assert len(scenarios) >= 3, (
        f"{app_id}: must have ≥3 repair scenarios, got {len(scenarios)}"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_scenario_required_fields(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    required = {"scenario_id", "stage_id", "trigger_condition", "recovery_action", "rollback_target"}
    for i, scenario in enumerate(data.get("repair_scenarios", [])):
        missing = required - set(scenario.keys())
        assert not missing, (
            f"{app_id} scenario[{i}]: missing required fields {missing}"
        )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_scenario_ids_unique(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    ids = [s["scenario_id"] for s in data.get("repair_scenarios", []) if "scenario_id" in s]
    assert len(ids) == len(set(ids)), (
        f"{app_id}: duplicate scenario_ids found: {ids}"
    )


@pytest.mark.parametrize("app_id", ALL_APPS)
def test_repair_profile_ref_embedded_in_id(app_id: str) -> None:
    data = _load_repair_profile(app_id)
    profile_id: str = data["repair_profile_id"]
    task_class = EXPECTED_TASK_CLASS[app_id]
    assert task_class in profile_id, (
        f"{app_id}: repair_profile_id {profile_id!r} should contain task_class {task_class!r}"
    )


def test_l4_record_has_repair_profile_refs_field() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(AppDomainContractRecord)}
    assert "repair_profile_refs" in field_names, (
        "AppDomainContractRecord is missing repair_profile_refs field (Phase 1.4)"
    )


def test_l4_record_repair_profile_refs_defaults_empty() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord

    rec = AppDomainContractRecord(
        app_domain_contract_id="adc::apps_qna::test",
        app_id="apps_qna",
        app_version="1.0.0",
        domain="test_domain",
        owner_surface="apps_qna",
        status="draft",
    )
    assert rec.repair_profile_refs == (), (
        "repair_profile_refs should default to empty tuple"
    )


def test_l4_record_accepts_repair_profile_refs() -> None:
    from agentic_core.L4_state.contracts.app_domain import AppDomainContractRecord

    rec = AppDomainContractRecord(
        app_domain_contract_id="adc::apps_qna::test",
        app_id="apps_qna",
        app_version="1.0.0",
        domain="test_domain",
        owner_surface="apps_qna",
        status="draft",
        repair_profile_refs=("rp::apps_qna::qna_pack_build::v1",),
    )
    assert rec.repair_profile_refs == ("rp::apps_qna::qna_pack_build::v1",)
