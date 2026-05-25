"""Negative-control tests for plane-2 manifest gates (ADR-081 W3.3)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RUNNER_PATH = REPO_ROOT / "ops_scripts" / "ci" / "run_adg_three_graph_tests.py"
spec = importlib.util.spec_from_file_location("_adg_runner_neg", RUNNER_PATH)
assert spec is not None and spec.loader is not None
_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_runner)

from tests.adg.fixtures.negative.fixture_builder import (  # noqa: E402
    build_forged_trace_id,
    build_missing_mv_views,
    build_null_triplet_edges,
)


def test_null_triplet_fixture_fails_view_rule_gate() -> None:
    fix = build_null_triplet_edges()
    snap = REPO_ROOT / "tests" / "adg" / "fixtures" / "negative" / fix.slug / "snapshot.sqlite"
    manifest = _runner.load_manifest()
    gate = next(g for g in manifest["gates"] if g["gate_id"] == "static.no_null_triplet")
    result = _runner.execute_gate(gate, snapshot=snap, strict=True)
    assert result.status == "FAIL", result.actual_fail_reason


@pytest.mark.parametrize(
    "builder,script_rel,extra_argv",
    [
        (build_missing_mv_views, "ops_scripts/ci/check_snapshot_has_mvs.py", []),
        (
            build_forged_trace_id,
            "ops_scripts/ci/check_runtime_proof_view_well_formed.py",
            ["--strict"],
        ),
    ],
)
def test_legacy_script_fixture_exits_nonzero(builder, script_rel, extra_argv) -> None:
    fix = builder()
    snap = REPO_ROOT / "tests" / "adg" / "fixtures" / "negative" / fix.slug / "snapshot.sqlite"
    script = REPO_ROOT / script_rel
    cmd = [sys.executable, str(script), str(snap), *extra_argv]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)  # noqa: S603
    assert proc.returncode != 0, proc.stdout[-300:]


def test_changed_suite_resolves_gate_ids() -> None:
    ids = _runner._resolve_changed_gate_ids()
    assert "preflight.snapshot_present" in ids
    assert "cross_bucket.impossible_states" in ids
