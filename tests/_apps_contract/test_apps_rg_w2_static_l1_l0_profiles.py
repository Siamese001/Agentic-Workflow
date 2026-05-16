"""Static L1/L0 profile rows referenced by the native-core binding fixture."""

from __future__ import annotations

from pathlib import Path

import yaml

from agentic_core.runtime.bindings.native_contract_chain import NATIVE_PROOF_ROUTE_PROFILE_ID

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_fixture_route_profile_contains_native_proof_id() -> None:
    rp = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package/fixture_route_profiles.yaml"
    data = yaml.safe_load(rp.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    ids = [row.get("route_profile_id") for row in data if isinstance(row, dict)]
    assert NATIVE_PROOF_ROUTE_PROFILE_ID in ids


def test_fixture_l1_has_schema_and_hops() -> None:
    l1 = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package/l1_static_plan_profile.yaml"
    doc = yaml.safe_load(l1.read_text(encoding="utf-8"))
    assert doc.get("schema_version")
    assert doc.get("planning_posture", {}).get("mode")
    assert doc.get("plan_hops")
