"""Verifier for the agentic_core spine harness.

Boundary invariant test: this file MUST NOT import from
`tools.certification.apps_e2e` and the apps_e2e tests MUST NOT import
from `tools.certification.agentic_core_e2e`. Constitutional plan §14.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.certification.agentic_core_e2e import CORE_PROOF_SCHEMA_VERSION
from tools.certification.agentic_core_e2e.run_core_proof import (
    CORE_PROOF_PATH, CORE_ROUTE_MATRIX_PATH, build_core_proof,
)
from tools.certification.agentic_core_e2e.scenarios import CORE_SCENARIOS

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def core_proof() -> dict:
    if not CORE_PROOF_PATH.exists():
        # Build on-demand for first-run convenience
        proof = build_core_proof()
        CORE_PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
        CORE_PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    return json.loads(CORE_PROOF_PATH.read_text(encoding="utf-8"))


def test_core_proof_schema_version(core_proof: dict) -> None:
    assert core_proof["proof_schema_version"] == CORE_PROOF_SCHEMA_VERSION


def test_core_proof_contains_every_scenario(core_proof: dict) -> None:
    expected = {s.scenario_id for s in CORE_SCENARIOS}
    actual = {r["scenario_id"] for r in core_proof["scenarios"]}
    assert expected == actual


def test_core_proof_blocking_gaps_match_failing_scenarios(core_proof: dict) -> None:
    failing = {r["scenario_id"] for r in core_proof["scenarios"] if not r["pass"]}
    expected_gaps = {f"core_scenario_{s}_not_executable" for s in failing}
    assert set(core_proof["blocking_gaps"]) == expected_gaps


def test_core_proof_harness_pass_is_true(core_proof: dict) -> None:
    """The HARNESS ran (even if every scenario is not_implemented).
    success vs harness_pass distinction matches apps_e2e's pattern.
    """
    assert core_proof["harness_pass"] is True


def test_route_matrix_mirrors_proof() -> None:
    if not CORE_ROUTE_MATRIX_PATH.exists():
        pytest.skip("route matrix not emitted")
    matrix = json.loads(CORE_ROUTE_MATRIX_PATH.read_text(encoding="utf-8"))
    proof = json.loads(CORE_PROOF_PATH.read_text(encoding="utf-8"))
    assert matrix["scenario_count"] == len(proof["scenarios"])


def _scan_for_imports(pkg_dir: Path, forbidden_module: str) -> list[str]:
    """AST-based scan for actual import statements (not docstring mentions)."""
    import ast
    offenders: list[str] = []
    for p in pkg_dir.rglob("*.py"):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(forbidden_module):
                    offenders.append(f"{p.relative_to(REPO_ROOT)}: from {node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(forbidden_module):
                        offenders.append(f"{p.relative_to(REPO_ROOT)}: import {alias.name}")
    return offenders


def test_boundary_invariant_no_apps_e2e_imports() -> None:
    """agentic_core_e2e package MUST NOT import from apps_e2e (AST-checked)."""
    pkg_dir = REPO_ROOT / "tools" / "certification" / "agentic_core_e2e"
    offenders = _scan_for_imports(pkg_dir, "tools.certification.apps_e2e")
    assert not offenders, f"agentic_core_e2e imports forbidden apps_e2e: {offenders}"


def test_boundary_invariant_no_apps_e2e_back_imports() -> None:
    """apps_e2e package MUST NOT import from agentic_core_e2e (AST-checked)."""
    pkg_dir = REPO_ROOT / "tools" / "certification" / "apps_e2e"
    offenders = _scan_for_imports(pkg_dir, "tools.certification.agentic_core_e2e")
    assert not offenders, f"apps_e2e imports forbidden agentic_core_e2e: {offenders}"
