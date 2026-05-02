"""Stage-by-stage collectors for spine receipts.

Reads every artifact written by a real `python -m <app>` run and maps
each to one of the canonical stages: U0, L1, L0, L3 (run|bypass), C0, PA,
L2, Exit, L6, OTEL. No execution; pure read.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.certification.apps_e2e.hash_utils import (
    REPO_ROOT, relative_to_repo, sha256_file, utc_now_iso,
)


def latest_run_dir(runs_root: Path) -> Path | None:
    """Return the most recent date-prefixed run dir under <app>/runs/.

    Convention: dirs are named YYYYMMDD_HHMMSS or similar; first 8 chars
    must be digits.
    """
    if not runs_root.exists():
        return None
    runs = sorted(
        (p for p in runs_root.iterdir() if p.is_dir() and p.name[:8].isdigit()),
        key=lambda p: p.name,
        reverse=True,
    )
    return runs[0] if runs else None


def latest_adg_snapshot() -> Path | None:
    adg_dir = REPO_ROOT / "artifacts" / "adg"
    if not adg_dir.exists():
        return None
    snaps = sorted(
        adg_dir.glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return snaps[0] if snaps else None


def collect_run_artifacts(
    run_dir: Path | None, run_floor_epoch: float,
) -> dict[str, Any]:
    """Enumerate real artifacts in run_dir AND verify freshness.

    Stale = mtime predates run_floor_epoch by more than 5s.
    """
    if not run_dir or not run_dir.exists():
        return {"run_dir": None, "artifacts": [], "stale": [], "dir_mtime_epoch": None}
    items: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    import time
    for p in sorted(run_dir.rglob("*")):
        if not p.is_file():
            continue
        mt = p.stat().st_mtime
        rec = {
            "path": relative_to_repo(p),
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
            "mtime_epoch": mt,
            "mtime_utc": utc_now_iso() if mt == 0 else time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(mt)
            ),
        }
        if mt + 5 < run_floor_epoch:
            stale.append(rec)
        else:
            items.append(rec)
    return {
        "run_dir": relative_to_repo(run_dir),
        "dir_mtime_epoch": run_dir.stat().st_mtime,
        "artifacts": items,
        "stale": stale,
    }


# Keyword → stage map. Order within each tuple is fallback priority.
_STAGE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "intake": ("u0_intake_envelope", "validated_request", "u0_intake"),
    "l1": ("l1_plan_contract", "l1_plan"),
    "route": ("route_contract", "l0_route_contract"),
    "l3_receipt": ("l3_orchestration_receipt", "l3_receipt", "l3_workflow_contract"),
    "l3_bypass": ("l3_bypass_receipt", "l3_bypass"),
    "c0": ("final_evidence_contract", "c0_final_evidence", "c0_retrieval"),
    "prompt": ("prompt_assembly_manifest", "compiled_prompt", "prompt_envelope"),
    "l2": ("l2_execution_receipt", "l2_sealed_artifact", "sealed_artifact"),
    "exit": ("exit_review_packet", "exit_disposition", "x3_disposition"),
    "exhaust": ("runtime_exhaust_bundle", "runtime_exhaust", "l6_exhaust"),
    "otel": ("otel_runtime_trace", "otel_export", "runtime_trace"),
    "uwg": ("uwg_commit_receipt", "uwg_commit_request"),
}


def find_stage_artifact(
    artifacts: list[dict[str, Any]], stage: str,
) -> dict[str, Any] | None:
    """Return first artifact whose basename matches a keyword for `stage`.

    Excludes paths under narrative/candidates/ where similarly-named files
    can occur (apps_rg precedent).
    """
    needles = _STAGE_KEYWORDS.get(stage, ())
    for needle in needles:
        for rec in artifacts:
            path = (rec.get("path") or "").lower()
            if "/narrative/" in path or "\\narrative\\" in path:
                continue
            stem = path.rsplit("/", 1)[-1]
            if needle in stem:
                return rec
    return None


def read_spine_ids(route_artifact: dict[str, Any] | None) -> tuple[str | None, str | None, str | None]:
    """Read run_id, request_id, trace_root from a RouteContract JSON file."""
    if not route_artifact:
        return (None, None, None)
    p = REPO_ROOT / route_artifact["path"]
    if not p.exists():
        return (None, None, None)
    import json
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (None, None, None)
    return (data.get("run_id"), data.get("request_id"), data.get("trace_root"))


def detect_synthetic_trace(otel_artifact: dict[str, Any] | None) -> bool:
    """True if the OTEL/runtime trace has a `contains_synthetic_spans` flag
    or any span with `is_synthetic=true`. Conservative: returns False if
    the file cannot be read.
    """
    if not otel_artifact:
        return False
    p = REPO_ROOT / otel_artifact["path"]
    if not p.exists():
        return False
    import json
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if data.get("contains_synthetic_spans"):
        return True
    for s in data.get("spans") or []:
        if s.get("is_synthetic"):
            return True
    return False


__all__ = [
    "latest_run_dir",
    "latest_adg_snapshot",
    "collect_run_artifacts",
    "find_stage_artifact",
    "read_spine_ids",
    "detect_synthetic_trace",
]
