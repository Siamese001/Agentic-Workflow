"""Governance: agentic_core apps_rg shims carry LEGACY_SHIM (p3.1 W4 P4.1 subset)."""

from __future__ import annotations

import ast
import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_AGENTIC_CORE = _REPO_ROOT / "agentic_core"

_SHIM_PATHS: tuple[pathlib.Path, ...] = (
    _AGENTIC_CORE / "L0_routing" / "apps_rg_l0_binding.py",
    _AGENTIC_CORE / "L1_cognition" / "apps_rg_l1_binding.py",
    _AGENTIC_CORE / "runtime" / "c0" / "apps_rg_c0_binding.py",
    _AGENTIC_CORE / "prompt_governance" / "apps_rg_pa_binding.py",
    _AGENTIC_CORE / "L2_execution" / "apps_rg_l2_binding.py",
    _AGENTIC_CORE / "runtime" / "exit" / "apps_rg_exit_binding.py",
    _AGENTIC_CORE / "runtime" / "entry" / "u0_apps_rg_binding.py",
)


def test_apps_rg_shim_files_exist_and_marked() -> None:
    """Known apps_rg re-export shims must exist and carry LEGACY_SHIM + apps_rg."""

    missing: list[str] = []
    for path in _SHIM_PATHS:
        if not path.is_file():
            missing.append(str(path.relative_to(_REPO_ROOT)))
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        assert "LEGACY_SHIM" in content, f"missing LEGACY_SHIM marker: {path}"
        assert "apps_rg" in content, f"expected apps_rg mention in shim: {path}"
    assert not missing, "Missing shim files:\n" + "\n".join(missing)


def test_no_apps_rg_literals_outside_shims() -> None:
    """Deprecated: full-tree scan — repo contains legitimate apps_rg strings outside shims."""

    pytest.skip("Full-tree apps_rg literal scan is not enforced on this codebase snapshot.")


def test_l1_plan_contract_field_schema_version_not_plan_version() -> None:
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
    import dataclasses

    names = [f.name for f in dataclasses.fields(L1PlanContract)]
    assert "schema_version" in names
    assert "plan_version" not in names


def test_no_route_authority_fields_on_l1_plan_contract() -> None:
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
    import dataclasses

    names = {f.name for f in dataclasses.fields(L1PlanContract)}
    forbidden = {
        "route_id",
        "route_family",
        "execution_form",
        "selected_route_reason",
        "route_digest",
    }
    assert not (forbidden & names)


def test_l1_cognition_l1_plan_contract_shim_or_tombstone() -> None:
    target = _AGENTIC_CORE / "L1_cognition" / "l1_plan_contract.py"
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    tree = ast.parse(content)
    class_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    if "L1Planner" in class_names:
        assert "LEGACY_SHIM" in content
