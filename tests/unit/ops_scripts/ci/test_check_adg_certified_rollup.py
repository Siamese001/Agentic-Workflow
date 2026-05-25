"""ADR-081: check_adg_certified rollup mode does not subprocess sub-gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci import check_adg_certified as certified_mod  # noqa: E402
from ops_scripts.ci.adg_enforcement_report import write_enforcement_report, build_enforcement_report  # noqa: E402


def test_rollup_mode_skips_subprocess(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    report = build_enforcement_report(
        snapshot_path=None,
        gate_manifest_path=None,
        three_graph_rollup_path=None,
        dispatcher_results_path=None,
        runtime_proof_status="attested",
    )
    report["certified_rollup"] = "CERTIFIED"
    report["p0_bug_gates_failed"] = []
    path = write_enforcement_report(report, ts="test0000_0000")

    monkeypatch.setattr(
        "ops_scripts.ci.adg_enforcement_report.latest_enforcement_report",
        lambda: path,
    )

    with patch.object(certified_mod.subprocess, "run") as mock_run:
        rc = certified_mod.main(["--rollup", "--rollup-path", str(path)])
        mock_run.assert_not_called()

    assert rc == 0


def test_rollup_not_certified_strict_exits_nonzero(tmp_path: Path) -> None:
    report = build_enforcement_report(
        snapshot_path=None,
        gate_manifest_path=None,
        three_graph_rollup_path=None,
        dispatcher_results_path=None,
    )
    report["certified_rollup"] = "NOT_CERTIFIED"
    report["p0_bug_gates_failed"] = ["manifest:static.no_null_triplet:view_rule_fail"]
    path = write_enforcement_report(report, ts="test0001_0000")
    rc = certified_mod.main(["--rollup", "--rollup-path", str(path), "--strict"])
    assert rc == 1
