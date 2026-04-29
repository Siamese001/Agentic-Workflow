"""Negative-control tests for the ADG three-graph harness.

Each fixture in tests/adg/fixtures/negative/<slug>/ deliberately violates
one specific invariant. The corresponding gate MUST detect the violation
(exit non-zero or surface the expected_fail_reason in its GateResult).

Together these tests prove every gate CAN detect a real violation — not
just that they pass on the live snapshot by coincidence.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = REPO_ROOT / "tests" / "adg" / "fixtures" / "negative"
GATE_PATHS = {
    "static.edge_authority_well_formed": REPO_ROOT / "ops_scripts" / "ci" / "check_edge_authority_well_formed.py",
    "runtime.proof_view_well_formed": REPO_ROOT / "ops_scripts" / "ci" / "check_runtime_proof_view_well_formed.py",
    "runtime.trace_topology": REPO_ROOT / "ops_scripts" / "ci" / "check_runtime_trace_topology.py",
    "registry.graph_integrity": REPO_ROOT / "ops_scripts" / "ci" / "check_registry_graph_integrity.py",
    "cross_bucket.impossible_states": REPO_ROOT / "ops_scripts" / "ci" / "check_three_bucket_impossible_states.py",
}


def _ensure_fixtures_built() -> None:
    if not FIXTURE_ROOT.exists() or not any(FIXTURE_ROOT.iterdir()):
        builder = FIXTURE_ROOT / "fixture_builder.py"
        subprocess.run(
            [sys.executable, str(builder)],
            cwd=str(REPO_ROOT), check=True, timeout=60,
        )


@pytest.fixture(scope="module", autouse=True)
def fixtures_ready():
    _ensure_fixtures_built()


def _load_fixture_manifest(slug: str) -> dict:
    return json.loads((FIXTURE_ROOT / slug / "manifest.json").read_text())


def _run_gate(slug: str, *, fixture_manifest: dict, json_out: Path) -> subprocess.CompletedProcess:
    snapshot = FIXTURE_ROOT / slug / "snapshot.sqlite"
    gate = fixture_manifest["target_gate"]
    script = GATE_PATHS[gate]
    cmd = [
        sys.executable, str(script),
        "--snapshot", str(snapshot),
        "--json-out", str(json_out),
        *fixture_manifest.get("extra_args", []),
    ]
    env = os.environ.copy()
    # Override ADG_SNAPSHOT in case the gate falls back to "latest".
    env["ADG_SNAPSHOT"] = str(snapshot)
    return subprocess.run(
        cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True,
        timeout=60, check=False,
    )


# ---------------------------------------------------------------------------
# Per-fixture parametrized assertions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "slug",
    [
        "duplicate_active_target",
        "registry_only_prod_route",
        "triplet_missing_bucket_ref",
        "stale_snapshot_vs_gap_report",
        "synthetic_mislabeled_prod",
        "missing_parent_span_chain",
    ],
)
def test_negative_control_emits_expected_fail_reason(slug, tmp_path):
    """Each fixture's gate must surface the documented expected_fail_reason."""
    fix_manifest = _load_fixture_manifest(slug)
    expected = fix_manifest["expected_fail_reason"]
    if not expected:
        pytest.skip(f"{slug} is advisory-only (no expected_fail_reason)")

    out = tmp_path / f"{slug}.json"

    # For impossible-states fixtures, point the gate's gap-report path
    # to the fixture-local file via env var.
    env_extra = {}
    if slug == "stale_snapshot_vs_gap_report":
        # The impossible_states gate reads the standard gap-report path.
        # For this fixture, copy the fixture's gap report into place.
        gap_src = FIXTURE_ROOT / slug / "gap_report.json"
        gap_dst = REPO_ROOT / "docs" / "reports" / "adg" / "THREE_BUCKET_GAP_REPORT.json"
        backup = gap_dst.read_bytes() if gap_dst.exists() else None
        gap_dst.write_bytes(gap_src.read_bytes())
        try:
            proc = _run_gate(slug, fixture_manifest=fix_manifest, json_out=out)
        finally:
            if backup is not None:
                gap_dst.write_bytes(backup)
    else:
        proc = _run_gate(slug, fixture_manifest=fix_manifest, json_out=out)

    assert out.exists(), (
        f"{slug}: gate did not write JSON output. "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    )
    payload = json.loads(out.read_text())
    actual = payload.get("actual_fail_reason", "")
    assert actual == expected, (
        f"{slug}: expected '{expected}' got '{actual}'. "
        f"sample_failures={payload.get('sample_failures')}"
    )
    assert payload["status"] in ("FAIL", "WARN"), payload


def test_null_edge_authority_legacy_exit_code(tmp_path):
    """The legacy edge_authority gate doesn't write GateResult JSON; the
    fixture's expected_fail_reason is its non-zero exit code."""
    slug = "null_edge_authority"
    fix_manifest = _load_fixture_manifest(slug)
    snapshot = FIXTURE_ROOT / slug / "snapshot.sqlite"

    script = GATE_PATHS["static.edge_authority_well_formed"]
    env = os.environ.copy()
    env["ADG_SNAPSHOT"] = str(snapshot)
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT), env=env,
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert proc.returncode == 1, (
        f"expected exit 1 from edge_authority on null-authority fixture, "
        f"got {proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
    )


def test_forged_trace_id_legacy_proof_view(tmp_path):
    slug = "forged_trace_id"
    snapshot = FIXTURE_ROOT / slug / "snapshot.sqlite"
    script = GATE_PATHS["runtime.proof_view_well_formed"]
    proc = subprocess.run(
        [sys.executable, str(script), "--snapshot", str(snapshot), "--strict"],
        cwd=str(REPO_ROOT),
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert proc.returncode == 1, (
        f"proof_view gate did not flag forged trace_id; exit={proc.returncode}\n"
        f"stdout={proc.stdout}"
    )


def test_agent_without_execution_profile_strict(tmp_path):
    """In --strict mode, registry.graph_integrity flips C_WARN to FAIL."""
    slug = "agent_without_execution_profile"
    fix_manifest = _load_fixture_manifest(slug)
    out = tmp_path / "out.json"
    proc = _run_gate(slug, fixture_manifest=fix_manifest, json_out=out)
    assert out.exists()
    payload = json.loads(out.read_text())
    assert payload["status"] == "FAIL", payload
    assert payload["actual_fail_reason"] == "C_WARN_RELATION_FIELDS_ASPIRATIONAL"


def test_model_outside_gateway_advisory(tmp_path):
    """Wildcard scope is currently advisory; we assert the SAMPLE is
    surfaced even though the gate doesn't FAIL on it yet."""
    slug = "model_outside_gateway"
    fix_manifest = _load_fixture_manifest(slug)
    out = tmp_path / "out.json"
    proc = _run_gate(slug, fixture_manifest=fix_manifest, json_out=out)
    assert out.exists()
    payload = json.loads(out.read_text())
    sample_codes = {s.get("code") for s in payload["sample_failures"]}
    assert "D4_INFO_WILDCARD_SCOPE" in sample_codes, (
        f"D4_INFO_WILDCARD_SCOPE missing from samples: {sample_codes}"
    )
