"""Unit tests for adg_enforcement_report aggregator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.adg_enforcement_report import (  # noqa: E402
    build_enforcement_report,
    compute_certified_rollup,
)


def test_compute_certified_clean() -> None:
    assert compute_certified_rollup(p0_failed=[], runtime_proof_status="attested", require_runtime_proof=False) == "CERTIFIED"


def test_compute_certified_p0_fail() -> None:
    assert (
        compute_certified_rollup(
            p0_failed=["manifest:static.no_null_triplet:x"],
            runtime_proof_status="attested",
            require_runtime_proof=False,
        )
        == "NOT_CERTIFIED"
    )


def test_build_report_merges_planes(tmp_path: Path) -> None:
    gate_manifest = tmp_path / "gate.json"
    gate_manifest.write_text(
        json.dumps(
            {
                "certification_status": "clean",
                "gates": [{"name": "wiring", "status": "pass"}],
            }
        ),
        encoding="utf-8",
    )
    rollup = tmp_path / "rollup.json"
    rollup.write_text(
        json.dumps({"suite": "quick", "overall_status": "PASS", "gates": []}),
        encoding="utf-8",
    )
    disp = tmp_path / "disp.json"
    disp.write_text(
        json.dumps({"overall_exit_code": 0, "gates": [], "total_gates": 0}),
        encoding="utf-8",
    )
    report = build_enforcement_report(
        snapshot_path=None,
        gate_manifest_path=gate_manifest,
        three_graph_rollup_path=rollup,
        dispatcher_results_path=disp,
    )
    assert report["planes"]["generator"]["failed"] == []
    assert report["planes"]["dispatcher"]["block_fail"] == 0
