"""Aggregate ADG enforcement planes into one triage artifact (tools-layer SSOT).

Plan: ``adg-ci-unified-migration-a7f3b2`` (W2.3). ``ops_scripts/ci/adg_enforcement_report.py``
re-exports this module so CI scripts keep a stable import path without tools → ops_scripts edges.
"""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _plane1_failed(gate_manifest: dict[str, Any]) -> list[str]:
    failed: list[str] = []
    for g in gate_manifest.get("gates", []):
        if g.get("status") in ("fail", "timed_out", "missing_script"):
            failed.append(f"{g.get('name')}:{g.get('status')}")
    return failed


def _plane2_failed(rollup: dict[str, Any]) -> list[str]:
    failed: list[str] = []
    for g in rollup.get("gates", []):
        if isinstance(g, dict) and g.get("status") == "FAIL":
            failed.append(f"{g.get('gate_id')}:{g.get('actual_fail_reason', '')}")
    return failed


def _plane3_summary(dispatcher: dict[str, Any]) -> dict[str, Any]:
    rows = dispatcher.get("gates", [])
    summary = dispatcher.get("summary") if isinstance(dispatcher.get("summary"), dict) else {}
    block_fail = summary.get("block_fail")
    if block_fail is None:
        block_fail = sum(
            1
            for r in rows
            if r.get("enforcement") == "block"
            and (r.get("status") == "fail" or int(r.get("exit_code") or 0) != 0)
        )
    ratchet_regressed = summary.get("ratchet_regressed")
    if ratchet_regressed is None:
        ratchet_regressed = sum(1 for r in rows if r.get("classification") == "regressed")
    return {
        "overall_exit_code": dispatcher.get("overall_exit_code"),
        "block_fail": int(block_fail or 0),
        "ratchet_regressed": int(ratchet_regressed or 0),
        "total_gates": dispatcher.get("total_gates", len(rows)),
        "results_path": None,
    }


def _p0_failed(*, plane1: list[str], plane2: list[str], plane3_block: int) -> list[str]:
    out: list[str] = []
    out.extend(f"generator:{x}" for x in plane1)
    out.extend(f"manifest:{x}" for x in plane2)
    if plane3_block:
        out.append(f"dispatcher:block_fail={plane3_block}")
    return out


def compute_certified_rollup(
    *,
    p0_failed: list[str],
    runtime_proof_status: str,
    require_runtime_proof: bool,
) -> str:
    if p0_failed:
        return "NOT_CERTIFIED"
    if require_runtime_proof and runtime_proof_status != "attested":
        return "NOT_CERTIFIED"
    return "CERTIFIED"


def build_enforcement_report(
    *,
    snapshot_path: Path | None,
    gate_manifest_path: Path | None,
    three_graph_rollup_path: Path | None,
    dispatcher_results_path: Path | None,
    runtime_proof_status: str = "view_absent",
    require_runtime_proof: bool = False,
    ts: str | None = None,
) -> dict[str, Any]:
    """Pure builder for tests and wrapper."""
    gate_manifest: dict[str, Any] = {}
    rollup: dict[str, Any] = {}
    dispatcher: dict[str, Any] = {}

    if gate_manifest_path and gate_manifest_path.is_file():
        gate_manifest = _load_json(gate_manifest_path)
    if three_graph_rollup_path and three_graph_rollup_path.is_file():
        rollup = _load_json(three_graph_rollup_path)
    if dispatcher_results_path and dispatcher_results_path.is_file():
        dispatcher = _load_json(dispatcher_results_path)

    plane1_failed = _plane1_failed(gate_manifest)
    plane2_failed = _plane2_failed(rollup)
    plane3 = _plane3_summary(dispatcher)
    if dispatcher_results_path:
        plane3["results_path"] = str(dispatcher_results_path)

    p0 = _p0_failed(
        plane1=plane1_failed,
        plane2=plane2_failed,
        plane3_block=int(plane3.get("block_fail") or 0),
    )
    certified = compute_certified_rollup(
        p0_failed=p0,
        runtime_proof_status=runtime_proof_status,
        require_runtime_proof=require_runtime_proof,
    )

    stamp = ts or datetime.now(timezone.utc).strftime("%m%d%Y_%H%M")
    return {
        "schema_version": 1,
        "timestamp": _utcnow_iso(),
        "report_id": f"adg_enforcement_report_{stamp}",
        "snapshot_path": str(snapshot_path) if snapshot_path else None,
        "planes": {
            "generator": {
                "manifest_path": str(gate_manifest_path) if gate_manifest_path else None,
                "certification_status": gate_manifest.get("certification_status"),
                "failed": plane1_failed,
            },
            "snapshot_manifest": {
                "suite": rollup.get("suite"),
                "overall_status": rollup.get("overall_status"),
                "rollup_path": str(three_graph_rollup_path) if three_graph_rollup_path else None,
                "failed": plane2_failed,
            },
            "dispatcher": plane3,
            "satellite": {"skipped": ["graph_layer_evidence", "M10", "M11", "M12", "AUDIT_5"]},
        },
        "certified_rollup": certified,
        "p0_bug_gates_failed": p0,
        "runtime_proof_status": runtime_proof_status,
    }


def write_enforcement_report(report: dict[str, Any], *, ts: str | None = None) -> Path:
    ARTIFACTS_ADG.mkdir(parents=True, exist_ok=True)
    stamp = ts or datetime.now(timezone.utc).strftime("%m%d%Y_%H%M")
    path = ARTIFACTS_ADG / f"adg_enforcement_report_{stamp}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    latest = ARTIFACTS_ADG / "adg_enforcement_report_latest.json"
    latest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def latest_enforcement_report() -> Path | None:
    latest = ARTIFACTS_ADG / "adg_enforcement_report_latest.json"
    if latest.is_file():
        return latest
    candidates = sorted(
        ARTIFACTS_ADG.glob("adg_enforcement_report_*.json"),
        key=lambda p: p.stat().st_mtime,
    )
    return candidates[-1] if candidates else None
