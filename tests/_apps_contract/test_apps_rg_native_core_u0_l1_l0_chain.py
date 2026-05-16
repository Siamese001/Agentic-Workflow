"""W2: U0/L1/L0 native contract-shaped carriers from binding YAML only."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.native_contract_chain import (
    NativeContractChainError,
    build_native_core_contract_chain_from_binding,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_native_chain_emits_validated_request_l1_route_contracts() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    proof = build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
    vr = proof.validated_request
    l1 = proof.l1_plan_contract
    rc = proof.route_contract
    assert vr.app_id == "apps_rg"
    assert l1.app_id == "apps_rg"
    assert rc.app_id == "apps_rg"
    assert rc.route_id
    assert rc.execution_form == "single_step"
    assert "CACHE" not in rc.route_id.upper() and "FINAL" not in rc.route_id.upper()


def test_route_contract_single_managed_profile_row() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    proof = build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
    assert proof.route_contract.route_id.count("_") >= 1


def test_missing_l1_section_fails_closed(tmp_path: Path) -> None:
    import shutil

    import yaml

    dst = tmp_path / "pkg"
    shutil.copytree(FIXTURE_PKG, dst)
    man = dst / "app_binding_sections.binding_v1.yaml"
    doc = yaml.safe_load(man.read_text(encoding="utf-8"))
    del doc["sections"]["l1_static_plan_profile"]
    man.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    pkg = load_app_binding_package(dst)
    with pytest.raises(NativeContractChainError):
        build_native_core_contract_chain_from_binding(pkg, repo_root=REPO_ROOT)
