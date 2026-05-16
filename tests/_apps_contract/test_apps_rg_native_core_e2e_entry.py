"""W1: Opt-in native-core proof harness entry (generic binding consumer)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.app_binding_validation import (
    scan_generic_bindings_tree_for_apps_imports,
    validate_app_binding_package,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_proof_harness_loads_fixture_via_generic_loader() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    assert pkg.app_id == "apps_rg"
    vr = validate_app_binding_package(pkg)
    assert vr.status == "PASS"


def test_generic_bindings_tree_has_no_apps_imports() -> None:
    assert scan_generic_bindings_tree_for_apps_imports() == []


def test_python_m_apps_rg_help_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "apps_rg", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0


def test_default_product_entry_remains_resume_cli() -> None:
    main_py = REPO_ROOT / "apps_rg" / "__main__.py"
    text = main_py.read_text(encoding="utf-8")
    assert "resume generation CLI" in text
    assert "argparse" in text


@pytest.mark.parametrize(
    "fname",
    [
        "profile_validators.py",
        "ref_validators.py",
        "evidence_policy_validator.py",
        "native_contract_chain.py",
    ],
)
def test_generic_binding_modules_avoid_apps_rg_literals_where_required(fname: str) -> None:
    """Generic validators must not hard-code apps_rg lane vocabulary."""
    p = REPO_ROOT / "agentic_core" / "runtime" / "bindings" / fname
    body = p.read_text(encoding="utf-8")
    assert "executive_summary_dispatch" not in body
    assert "ibm_bullets_dispatch" not in body
