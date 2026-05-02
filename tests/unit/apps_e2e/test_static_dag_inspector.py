"""Unit tests for static_dag_inspector — fail-closed shape + scan logic."""
from __future__ import annotations

from tools.certification.apps_e2e.static_dag_inspector import build_static_dag_proof


def test_build_static_dag_proof_for_unknown_app_is_fail_closed() -> None:
    proof = build_static_dag_proof(
        app_name="apps_does_not_exist_xyz",
        app_package="apps_does_not_exist_xyz",
    )
    assert proof["proof_kind"] == "static_l3_dag_proof"
    assert proof["app_name"] == "apps_does_not_exist_xyz"
    assert proof["present"] is False
    assert proof["fail_closed"] is True
    assert "static_dag_missing_entirely" in proof["fail_reasons"]
    assert proof["dag_id"] is None
    assert proof["dag_sha256"] is None
    # Scan results always populated
    assert "registries" in proof["scan_results"]
    assert "dag_directories" in proof["scan_results"]


def test_build_static_dag_proof_scans_canonical_paths() -> None:
    """For apps_rg the canonical scan paths must include route_registry.yaml."""
    proof = build_static_dag_proof(app_name="apps_rg", app_package="apps_rg")
    paths = [r["path"] for r in proof["scan_results"]["registries"]]
    assert "apps_rg/config/route_registry.yaml" in paths
    assert "apps_rg/config/l3_dag.yaml" in paths


def test_required_top_fields_present_even_when_fail_closed() -> None:
    proof = build_static_dag_proof(app_name="apps_qna", app_package="apps_qna")
    required = (
        "proof_schema_version", "proof_kind", "app_name", "generated_at_utc",
        "present", "fail_closed", "fail_reasons", "scan_results",
    )
    for k in required:
        assert k in proof, k
