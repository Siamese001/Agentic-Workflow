"""Anti-cheat tests — fabrication detection on apps_e2e bundles.

These tests construct mutated copies of real bundles and assert the
shared verifier rejects them. The point: a hand-edited or maliciously
fabricated bundle MUST NOT pass.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools.certification.apps_e2e.app_specs import find_spec
from tools.certification.apps_e2e.paths import AppCertPaths
from tools.certification.apps_e2e.shared_verifier import (
    Violation, format_violation, verify_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def rg_bundle() -> dict:
    paths = AppCertPaths("apps_rg")
    if not paths.proof_bundle.exists():
        pytest.skip("apps_rg bundle not emitted; cannot run anti-cheat checks")
    return json.loads(paths.proof_bundle.read_text(encoding="utf-8"))


def _has_rule(violations: list[Violation], rule_id: str) -> bool:
    return any(v.rule_id == rule_id for v in violations)


def test_real_apps_rg_bundle_passes(rg_bundle: dict) -> None:
    """Sanity: the real bundle has no internal-consistency violations."""
    spec = find_spec("apps_rg")
    violations = verify_bundle(rg_bundle, spec)
    assert violations == [], [format_violation(v) for v in violations]


def test_mutated_app_name_is_caught(rg_bundle: dict) -> None:
    """An attacker who copies apps_rg's bundle and renames it as apps_qna
    must be caught by the spec-vs-bundle app_name check.
    """
    spec = find_spec("apps_qna")  # mismatched spec
    violations = verify_bundle(rg_bundle, spec)
    assert _has_rule(violations, "app_name_mismatch")


def test_fake_success_with_runtime_refs_nulled(rg_bundle: dict) -> None:
    """If success=true but every runtime_*_ref is None, fail closed."""
    spec = find_spec("apps_rg")
    mutated = copy.deepcopy(rg_bundle)
    for k in (
        "runtime_route_contract_ref", "runtime_l1_plan_ref",
        "runtime_l3_receipt_ref", "runtime_l3_bypass_ref",
        "runtime_exit_disposition_ref", "runtime_exhaust_ref",
        "otel_or_runtime_trace_ref",
    ):
        mutated[k] = None
    mutated["blocking_gaps"] = []
    mutated["success"] = True
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "success_true_missing_runtime_ref")


def test_synthetic_trace_with_success_true_is_caught(rg_bundle: dict) -> None:
    spec = find_spec("apps_rg")
    mutated = copy.deepcopy(rg_bundle)
    mutated["synthetic_trace_detected"] = True
    mutated["success"] = True  # already true; just being explicit
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "synthetic_trace_with_success_true")


def test_run_id_mismatch_is_caught(rg_bundle: dict, tmp_path: Path) -> None:
    """Mutate the bundle's run_id but leave the route_contract on disk
    pointing at the original. Verifier must catch the threading break.
    """
    spec = find_spec("apps_rg")
    if not rg_bundle.get("success"):
        pytest.skip("apps_rg success=false; threading check inactive")
    mutated = copy.deepcopy(rg_bundle)
    mutated["run_id"] = "FORGED_RUN_ID_xxxxxxxxx"
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "run_id_threading_violation")


def test_overlay_violated_with_success_true_is_caught(rg_bundle: dict) -> None:
    spec = find_spec("apps_rg")
    if not rg_bundle.get("success"):
        pytest.skip("apps_rg success=false; overlay check inactive when not success")
    mutated = copy.deepcopy(rg_bundle)
    mutated["app_overlay_authority_status"] = "overlay_violated"
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "overlay_violated_with_success")


def test_invalid_exit_disposition_is_caught(rg_bundle: dict, tmp_path: Path) -> None:
    """If runtime_exit_disposition_ref points at a file with x3_disposition
    not in the allowed set, the verifier must flag it.
    """
    spec = find_spec("apps_rg")
    exit_ref = rg_bundle.get("runtime_exit_disposition_ref")
    if not exit_ref:
        pytest.skip("no exit ref; check inactive")

    # Write a fake exit disposition into tmp and point a copied bundle at it.
    fake_exit = tmp_path / "fake_exit.json"
    fake_exit.write_text(json.dumps({"x3_disposition": "EXIT_BANANA", "sealed": True}), encoding="utf-8")
    fake_rel = fake_exit.relative_to(REPO_ROOT) if fake_exit.is_relative_to(REPO_ROOT) else None
    if fake_rel is None:
        # tmp_path is outside repo → can't easily forge; skip this scenario
        pytest.skip("tmp_path outside REPO_ROOT — cannot forge ref path")
    mutated = copy.deepcopy(rg_bundle)
    mutated["runtime_exit_disposition_ref"] = str(fake_rel).replace("\\", "/")
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "exit_disposition_invalid")


def test_harness_pass_false_is_caught(rg_bundle: dict) -> None:
    spec = find_spec("apps_rg")
    mutated = copy.deepcopy(rg_bundle)
    mutated["harness_pass"] = False
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "harness_pass_false")


def test_dropped_required_field_is_caught(rg_bundle: dict) -> None:
    spec = find_spec("apps_rg")
    mutated = copy.deepcopy(rg_bundle)
    del mutated["proof_schema_version"]
    violations = verify_bundle(mutated, spec)
    assert _has_rule(violations, "bundle_missing_required_field")
