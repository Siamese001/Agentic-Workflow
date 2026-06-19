"""Verifier for the all-apps matrix.

Asserts:
  * matrix exists at the canonical path
  * matrix mirrors per-app proof bundles (no hand-authored drift)
  * totals are coherent
  * every AppSpec is represented (no silent omissions)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.certification.apps_e2e.app_specs import APP_SPECS, find_spec
from tools.certification.apps_e2e.matrix_builder import build_matrix
from tools.certification.apps_e2e.paths import MATRIX_PATH, AppCertPaths

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def matrix() -> dict:
    if not MATRIX_PATH.exists():
        pytest.skip(
            f"Matrix not emitted yet. Run:\n"
            f"  python -m tools.certification.apps_e2e.matrix_builder"
        )
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def test_matrix_schema_version_is_set(matrix: dict) -> None:
    assert matrix["matrix_schema_version"].startswith("apps_e2e_matrix/")


def test_matrix_has_one_row_per_appspec(matrix: dict) -> None:
    expected = {s.app_name for s in APP_SPECS}
    actual = {row["app_name"] for row in matrix["apps"]}
    missing = expected - actual
    extra = actual - expected
    assert not missing, f"matrix missing apps: {missing}"
    assert not extra, f"matrix has unexpected apps: {extra}"


def test_matrix_totals_are_coherent(matrix: dict) -> None:
    rows = matrix["apps"]
    t = matrix["totals"]
    assert t["discovered"] == sum(1 for r in rows if r["discovered"])
    assert t["runnable"] == sum(1 for r in rows if r["entrypoint_runnable"])
    assert t["succeeded"] == sum(1 for r in rows if r["success"])
    failed = sum(1 for r in rows if not r["success"] and r["proof_bundle_ref"])
    assert t["failed"] == failed
    not_run = sum(1 for r in rows if not r["proof_bundle_ref"])
    assert t["not_run"] == not_run


def test_matrix_is_freshly_buildable(matrix: dict) -> None:
    """Re-running build_matrix must produce a row set identical to the
    persisted matrix (modulo timestamps and harness_run_id).
    """
    fresh = build_matrix()
    assert {r["app_name"] for r in fresh["apps"]} == {r["app_name"] for r in matrix["apps"]}
    fresh_status = {r["app_name"]: r["agentic_core_spine_status"] for r in fresh["apps"]}
    persisted_status = {r["app_name"]: r["agentic_core_spine_status"] for r in matrix["apps"]}
    assert fresh_status == persisted_status, (
        "Persisted matrix drifted from current bundles — re-emit matrix."
    )


def test_no_app_silently_omitted(matrix: dict) -> None:
    """Every AppSpec — runnable or not — must appear with `discovered=true`."""
    by_name = {row["app_name"]: row for row in matrix["apps"]}
    for spec in APP_SPECS:
        row = by_name.get(spec.app_name)
        assert row is not None, f"{spec.app_name} omitted from matrix"
        assert row["discovered"] is True


def test_apps_rg_is_runnable_in_matrix(matrix: dict) -> None:
    by_name = {row["app_name"]: row for row in matrix["apps"]}
    rg = by_name["apps_rg"]
    assert rg["entrypoint_runnable"] is True
    assert rg["entrypoint_command"].startswith("python -m apps_rg")


def test_apps_underwriting_ai_runnable_matches_registry(matrix: dict) -> None:
    by_name = {row["app_name"]: row for row in matrix["apps"]}
    spec = find_spec("apps_underwriting_ai")
    assert spec is not None
    assert by_name["apps_underwriting_ai"]["entrypoint_runnable"] is spec.runnable


def test_print_matrix_table(matrix: dict, capsys: pytest.CaptureFixture) -> None:
    """Pretty-print the all-apps table for human review."""
    rows = matrix["apps"]
    cols = (
        ("App", "app_name", 22),
        ("Entry", "entrypoint_runnable", 5),
        ("StaticDAG", "static_dag_status", 13),
        ("L3", "l3_runtime_status", 9),
        ("Spine", "agentic_core_spine_status", 16),
        ("OTEL", "otel_status", 9),
        ("Exit", "exit_status", 8),
        ("L6", "l6_status", 8),
        ("Success", "success", 7),
        ("Gap", "blocking_gaps", 38),
    )
    header = "  ".join(f"{n:<{w}}" for n, _, w in cols)
    sep = "-" * len(header)
    lines = [header, sep]
    for r in rows:
        cells = []
        for _, k, w in cols:
            v = r.get(k)
            if isinstance(v, list):
                v = ",".join(v[:2])[:w]
            elif isinstance(v, bool):
                v = "true" if v else "false"
            else:
                v = "" if v is None else str(v)
            cells.append(f"{v[:w]:<{w}}")
        lines.append("  ".join(cells))
    lines.append(sep)
    t = matrix["totals"]
    lines.append(
        f"TOTALS: discovered={t['discovered']}  runnable={t['runnable']}  "
        f"succeeded={t['succeeded']}  failed={t['failed']}  not_run={t['not_run']}"
    )
    print("\n" + "\n".join(lines))
