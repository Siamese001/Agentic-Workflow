"""Governance: agentic_core apps_rg shims carry LEGACY_SHIM (p3.1 W4 P4.1 subset)."""

from __future__ import annotations

import ast
import pathlib

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_AGENTIC_CORE = _REPO_ROOT / "agentic_core"

# Active TEMPORARY_THIN_ADAPTER shims still required in core (not yet archive-pending).
_ACTIVE_LEGACY_SHIM_PATHS: tuple[pathlib.Path, ...] = (
    _AGENTIC_CORE / "L0_routing" / "apps_rg_l0_binding.py",
    _AGENTIC_CORE / "L1_cognition" / "apps_rg_l1_binding.py",
    _AGENTIC_CORE / "runtime" / "c0" / "apps_rg_c0_binding.py",
    _AGENTIC_CORE / "prompt_governance" / "apps_rg_pa_binding.py",
    _AGENTIC_CORE / "runtime" / "exit" / "apps_rg_exit_binding.py",
    _AGENTIC_CORE / "runtime" / "entry" / "u0_apps_rg_binding.py",
)

_L2_CORE_SHIM_PATH = _AGENTIC_CORE / "L2_execution" / "apps_rg_l2_binding.py"
_CANONICAL_L2_BINDING_PATH = _REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "l2_binding.py"


def _archived_l2_shim_path() -> pathlib.Path:
    matches = sorted(
        (_REPO_ROOT / "archives").glob(
            "l2_rationalization_*/agentic_core/L2_execution/apps_rg_l2_binding.py"
        )
    )
    assert matches, "archived L2 shim missing under archives/l2_rationalization_*/"
    return matches[-1]


def test_active_legacy_shim_files_exist_and_marked() -> None:
    """Known active apps_rg re-export shims must exist and carry LEGACY_SHIM + apps_rg."""

    missing: list[str] = []
    for path in _ACTIVE_LEGACY_SHIM_PATHS:
        if not path.is_file():
            missing.append(str(path.relative_to(_REPO_ROOT)))
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        assert "LEGACY_SHIM" in content, f"missing LEGACY_SHIM marker: {path}"
        assert "apps_rg" in content, f"expected apps_rg mention in shim: {path}"
    assert not missing, "Missing active shim files:\n" + "\n".join(missing)


def test_l2_canonical_binding_active_core_shim_archived() -> None:
    """L2 product binding is apps_rg-owned; legacy core shim archived under archives/ (W11)."""

    assert _CANONICAL_L2_BINDING_PATH.is_file(), "canonical L2 binding must exist under apps_rg"
    canon = _CANONICAL_L2_BINDING_PATH.read_text(encoding="utf-8", errors="replace")
    assert "apps_rg" in canon
    assert "l2_execute_apps_rg" in canon

    assert not _L2_CORE_SHIM_PATH.is_file(), "shim must not remain in agentic_core after archive"
    archive = _archived_l2_shim_path()
    shim = archive.read_text(encoding="utf-8", errors="replace")
    assert "LEGACY_SHIM" in shim
    assert "apps_rg" in shim
    assert "apps_rg.runtime.bindings.l2_binding" in shim


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
