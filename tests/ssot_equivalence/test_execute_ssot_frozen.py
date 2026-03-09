"""
SSOT entrypoint label contract.

History: both execute_ssot.py and execute_ssot_entrypoint.py were once labelled
'# FROZEN — superseded by l0_execute.py'.  l0_execute.py was never built.
These files ARE the active entrypoints.  The tests below enforce the corrected
state and document the architectural debt explicitly.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_HEADER = "# NOTE: l0_execute.py was planned but never implemented. This file is ACTIVE."

STALE_FROZEN_HEADER = "# FROZEN — superseded by l0_execute.py"

ACTIVE_FILES = [
    REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py",
    REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot_entrypoint.py",
]

L0_EXECUTE_PATH = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "l0_execute.py"


def test_active_header_present():
    """Both entrypoint files must carry the corrected ACTIVE label."""
    for fpath in ACTIVE_FILES:
        assert fpath.exists(), f"Entrypoint file not found: {fpath}"
        content = fpath.read_text(encoding="utf-8")
        assert ACTIVE_HEADER in content, f"ACTIVE header missing in {fpath.name}. Expected: {ACTIVE_HEADER!r}"


def test_active_header_is_early():
    """ACTIVE label must appear within the first 5 non-empty lines."""
    for fpath in ACTIVE_FILES:
        lines = fpath.read_text(encoding="utf-8").splitlines()
        non_empty = [ln for ln in lines[:10] if ln.strip()]
        found = any(ACTIVE_HEADER in ln for ln in non_empty[:5])
        assert found, f"ACTIVE header not in first 5 non-empty lines of {fpath.name}"


def test_stale_frozen_label_absent():
    """The false FROZEN label must not appear in either entrypoint file."""
    for fpath in ACTIVE_FILES:
        content = fpath.read_text(encoding="utf-8")
        assert STALE_FROZEN_HEADER not in content, (
            f"Stale FROZEN label still present in {fpath.name}. Remove it."
        )


def test_l0_execute_does_not_exist():
    """l0_execute.py was planned but never implemented — assert non-existence.

    If this test starts failing, l0_execute.py was finally built.  At that
    point: remove this test, migrate callers, and retire execute_ssot_entrypoint.py.
    """
    assert not L0_EXECUTE_PATH.exists(), (
        f"l0_execute.py now exists at {L0_EXECUTE_PATH}. "
        "Update the entrypoint architecture and retire execute_ssot_entrypoint.py."
    )


def test_v15_bootstrap_wired_in_legacy_main():
    """AST-verify that _legacy_main in execute_ssot.py calls _v15_build_ssot_manifest.

    §8.1e requires the V15 manifest bootstrap to run at SSOT entry.  Both
    entrypoints reach §8.1e via _legacy_main, so we assert on _legacy_main's
    AST body rather than the entrypoint wrappers.
    """
    fpath = REPO_ROOT / "agentic_core" / "L0_routing" / "scripts" / "execute_ssot.py"
    source = fpath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(fpath))

    legacy_main_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_legacy_main":
            legacy_main_node = node
            break

    assert legacy_main_node is not None, "_legacy_main not found in execute_ssot.py"

    call_names: set[str] = set()
    for node in ast.walk(legacy_main_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                call_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                call_names.add(node.func.attr)

    assert "_v15_build_ssot_manifest" in call_names, (
        "§8.1e: _v15_build_ssot_manifest() not called inside _legacy_main. "
        "V15 audit bootstrap is missing from the SSOT entrypoint."
    )
    assert "_v15_ssot_gateway_audit" in call_names, (
        "§8.1e: _v15_ssot_gateway_audit() not called inside _legacy_main. "
        "V15 gateway audit is missing from the SSOT entrypoint."
    )
