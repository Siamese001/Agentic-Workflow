"""Unit tests for shared_verifier.

Builds synthetic proof bundles and asserts violations are computed
correctly. No app execution; pure logic.
"""
from __future__ import annotations

from tools.certification.apps_e2e.app_specs import find_spec
from tools.certification.apps_e2e.shared_verifier import (
    REQUIRED_TOP_FIELDS, verify_bundle, format_violation,
)


def _minimal_passing_bundle(app_name: str = "apps_rg") -> dict:
    """A bundle with all top-level fields, success=False, no runtime evidence.

    Verifier should treat this as: all schema fields present, success=False
    (so no anti-cheat checks fire), no violations.
    """
    base: dict = {k: None for k in REQUIRED_TOP_FIELDS}
    base.update({
        "proof_schema_version": "apps_e2e_proof/2026-05-01/v1",
        "harness_schema_version": "apps_e2e_harness/2026-05-01/v1",
        "app_name": app_name,
        "app_package": app_name,
        "entrypoint_command": f"python -m {app_name}",
        "run_id": "test-run-12345678",
        "request_id": "test-run-12345678",
        "trace_root": "test-run-12345678",
        "started_at_utc": "2026-05-01T00:00:00Z",
        "finished_at_utc": "2026-05-01T00:01:00Z",
        "exit_code": 0,
        "git_commit": "abc1234",
        "git_dirty": False,
        "runtime_mode": "standalone_orchestrator_pre_spine",
        "mock_mode_detected": False,
        "fixture_mode_detected": False,
        "synthetic_trace_detected": False,
        "success": False,
        "blocking_gaps": ["no_runtime_route_contract_emitted"],
        "harness_pass": True,
        "honest_fail_closed": True,
        "harness_run_id": "harness-test-1",
        "app_overlay_authority_status": "overlay_unknown",
        "agentic_core_spine_status": "spine_bypassed",
        "stage_matrix": [],
    })
    return base


def test_minimal_failing_bundle_is_internally_consistent() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    violations = verify_bundle(bundle, spec)
    # success=false with honest blocking gap is NOT a verifier failure
    assert violations == [], [format_violation(v) for v in violations]


def test_missing_top_field_violates() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    del bundle["run_id"]
    violations = verify_bundle(bundle, spec)
    assert any(v.rule_id == "bundle_missing_required_field" for v in violations)


def test_app_name_mismatch_violates() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle(app_name="apps_qna")
    violations = verify_bundle(bundle, spec)
    assert any(v.rule_id == "app_name_mismatch" for v in violations)


def test_harness_pass_false_violates() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    bundle["harness_pass"] = False
    violations = verify_bundle(bundle, spec)
    assert any(v.rule_id == "harness_pass_false" for v in violations)


def test_synthetic_trace_with_success_violates() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    bundle["success"] = True
    bundle["synthetic_trace_detected"] = True
    bundle["blocking_gaps"] = []
    violations = verify_bundle(bundle, spec)
    rules = [v.rule_id for v in violations]
    assert "synthetic_trace_with_success_true" in rules


def test_success_without_runtime_refs_violates() -> None:
    """success=true with all runtime refs null must produce violations."""
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    bundle["success"] = True
    bundle["blocking_gaps"] = []
    violations = verify_bundle(bundle, spec)
    rules = {v.rule_id for v in violations}
    assert "success_true_missing_runtime_ref" in rules


def test_timestamp_must_be_iso_utc() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    bundle["started_at_utc"] = "2026-05-01 00:00:00"  # missing Z
    violations = verify_bundle(bundle, spec)
    assert any(v.rule_id == "timestamp_not_iso_utc" for v in violations)


def test_entrypoint_command_must_match_package() -> None:
    spec = find_spec("apps_rg")
    bundle = _minimal_passing_bundle()
    bundle["entrypoint_command"] = "bash run_apps.sh"
    violations = verify_bundle(bundle, spec)
    assert any(v.rule_id == "entrypoint_command_invalid" for v in violations)
