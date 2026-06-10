"""Summarize an apps_rg E2E run into a truthful lane-status matrix.

Differentiates the three real lane states that ``integrated_lane_evidence_status.json``
currently conflates (apps_rg AIG E2E remediation, Wave 0 / E2E-05):

  * ``EXECUTED_<x3>``        — the lane ran and produced an X3 disposition
                              (e.g. ``EXECUTED_X3_BLOCK``, ``EXECUTED_X3_ALLOW``).
  * ``PRE_RUN_BLOCKED``     — the lane was dispatched but raised its own exception
                              (or was blocked) before producing an X3 verdict.
  * ``MISSING_NOT_ATTEMPTED`` — the lane was never attempted because a prior lane's
                              exception aborted the wave (``prior_abort``).

The classification is re-derived from each lane's ``dispatch_result`` rather than the
roll-up ``reason`` field, which buckets executed-but-blocked lanes identically to
never-attempted ones.

Two directory shapes are accepted:

  * **FULL run dir**    — contains ``integrated_lane_evidence_status.json`` and
                          ``modular_r4/sections/<lane>/``.
  * **SECTION run dir** — a single-lane dir containing
                          ``cli_section_execution_report.json`` /
                          ``exit_disposition_receipt.json``.

Usage:
    python tools/apps_rg/summarize_e2e_run.py <artifact-dir>

If ``<artifact-dir>`` is omitted, the most recently modified directory under
``artifacts/apps_rg/`` is selected.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
E2E_ROOT = REPO_ROOT / "artifacts" / "apps_rg"

# Canonical lane order (display); any extra lane dirs found are appended.
CANONICAL_LANES: List[str] = [
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
]

_DASH = "—"


# ----------------------------------------------------------------- read helpers


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ----------------------------------------------------------------- classification


def classify_lane_state(
    dispatch_result: Optional[Dict[str, Any]],
    *,
    pre_run_status: Optional[str] = None,
) -> str:
    """Re-derive the true lane state from a lane ``dispatch_result``.

    Precedence (most-specific first):
      1. ``x3_disposition`` present  -> ``EXECUTED_<x3>`` (the lane ran to a verdict).
      2. ``prior_abort`` present     -> ``MISSING_NOT_ATTEMPTED`` (a sibling aborted the wave).
      3. own ``fault==exception`` / ``error`` -> ``PRE_RUN_BLOCKED`` (attempted, threw).
      4. ``status==PRE_RUN_BLOCKED`` -> ``PRE_RUN_BLOCKED`` (best effort).
      5. otherwise                   -> ``MISSING_NOT_ATTEMPTED``.
    """
    dr = dispatch_result or {}
    x3 = dr.get("x3_disposition")
    if x3:
        return f"EXECUTED_{x3}"
    if dr.get("prior_abort"):
        return "MISSING_NOT_ATTEMPTED"
    if dr.get("fault") == "exception" or dr.get("error"):
        return "PRE_RUN_BLOCKED"
    if pre_run_status == "PRE_RUN_BLOCKED":
        return "PRE_RUN_BLOCKED"
    return "MISSING_NOT_ATTEMPTED"


# ----------------------------------------------------------------- metric extraction


def _latest_real_run(lane_dir: Path) -> Optional[Path]:
    real = lane_dir / "real"
    if not real.is_dir():
        return None
    runs = [p for p in real.iterdir() if p.is_dir()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime)


def lane_metrics_from_run_dir(run_dir: Path) -> Dict[str, Any]:
    """Extract provider/model/X1D/X2/X3/authorized from one lane's run dir.

    Works for both a standalone section dir and a full-run lane ``real/<run_id>/`` dir.
    Every field is best-effort; missing inputs yield ``"—"``.
    """
    out: Dict[str, Any] = {
        "provider": _DASH,
        "model": _DASH,
        "runtime_generation_status": _DASH,
        "x1d": _DASH,
        "x2_failed": _DASH,
        "x3": _DASH,
        "authorized": _DASH,
    }
    pr = _load_json(run_dir / "provider_response.json")
    if pr:
        out["provider"] = pr.get("provider_requested") or _DASH
        out["model"] = pr.get("model") or _DASH
        out["runtime_generation_status"] = pr.get("runtime_generation_status") or _DASH
    edr = _load_json(run_dir / "exit_disposition_receipt.json")
    if edr:
        x3d = edr.get("x3_disposition") or {}
        out["x3"] = edr.get("x3_code") or x3d.get("x3_code") or out["x3"]
        gates = x3d.get("x2_failed_gates")
        if isinstance(gates, list):
            out["x2_failed"] = len(gates)
        mode = x3d.get("x1d_evaluator_mode")
        decisive = x3d.get("decisive_judge_failures") or []
        if mode:
            out["x1d"] = f"{mode} fail:{','.join(decisive)}" if decisive else f"{mode} pass"
        if x3d.get("pass") is not None:
            out["authorized"] = bool(x3d.get("pass"))
    cli = _load_json(run_dir / "cli_section_execution_report.json")
    if cli:
        out["x3"] = cli.get("x3_code") or cli.get("product_status") or out["x3"]
        if cli.get("product_authorized") is not None:
            out["authorized"] = bool(cli.get("product_authorized"))
        if out["x2_failed"] == _DASH and cli.get("x2_product_quality_status"):
            out["x2_failed"] = cli.get("x2_product_quality_status")
    return out


# ----------------------------------------------------------------- run summarizers


def is_full_run(run_dir: Path) -> bool:
    return (run_dir / "integrated_lane_evidence_status.json").is_file() or (
        run_dir / "modular_r4" / "sections"
    ).is_dir()


def _lane_record_full(sections_root: Path, lane: str) -> Dict[str, Any]:
    lane_dir = sections_root / lane
    pre = _load_json(lane_dir / "integrated_lane_pre_run_failure.json") or {}
    dispatch_result = pre.get("dispatch_result") or {}
    state = classify_lane_state(dispatch_result, pre_run_status=pre.get("status"))
    blocker = pre.get("blocker") or dispatch_result.get("error") or dispatch_result.get("prior_abort") or _DASH
    rec: Dict[str, Any] = {"lane": lane, "state": state, "blocker": blocker}
    # Pull metrics from the executed run dir when the lane actually ran.
    run_dir = _latest_real_run(lane_dir)
    if run_dir is None and dispatch_result.get("artifact_dir"):
        cand = Path(dispatch_result["artifact_dir"])
        run_dir = cand if cand.is_dir() else None
    rec.update(lane_metrics_from_run_dir(run_dir) if run_dir else lane_metrics_from_run_dir(lane_dir))
    # W3 (plan apps-rg-aig-remaining-lanes-closeout-d4e1f7): a lane that SUCCEEDED writes no
    # integrated_lane_pre_run_failure.json, so dispatch_result is empty and classify_lane_state
    # fell through to MISSING_NOT_ATTEMPTED — mislabeling X3_ALLOW/authorized lanes. When no
    # pre-run failure exists, derive the state from the executed run dir's actual X3 evidence.
    if not pre and rec.get("x3") not in (None, "", _DASH):
        rec["state"] = f"EXECUTED_{rec['x3']}"
        rec["blocker"] = _DASH
    return rec


def summarize_full_run(run_dir: Path) -> Dict[str, Any]:
    sections_root = run_dir / "modular_r4" / "sections"
    found = (
        sorted(p.name for p in sections_root.iterdir() if p.is_dir())
        if sections_root.is_dir()
        else []
    )
    lanes = [l for l in CANONICAL_LANES if l in found] + [l for l in found if l not in CANONICAL_LANES]
    records = [_lane_record_full(sections_root, lane) for lane in lanes]
    return {"mode": "full", "run_dir": str(run_dir), "lanes": records, "counts": _count_states(records)}


def summarize_section_run(run_dir: Path) -> Dict[str, Any]:
    lane = run_dir.name
    edr = _load_json(run_dir / "exit_disposition_receipt.json") or {}
    lane = edr.get("section_id") or lane
    metrics = lane_metrics_from_run_dir(run_dir)
    x3 = metrics.get("x3") or _DASH
    state = f"EXECUTED_{x3}" if x3 not in (_DASH, None) else "PRE_RUN_BLOCKED"
    record = {"lane": lane, "state": state, "blocker": _DASH, **metrics}
    return {"mode": "section", "run_dir": str(run_dir), "lanes": [record], "counts": _count_states([record])}


def _count_states(records: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in records:
        bucket = r["state"] if r["state"].startswith("EXECUTED_") else r["state"]
        counts[bucket] = counts.get(bucket, 0) + 1
    return counts


def summarize(run_dir: Path) -> Dict[str, Any]:
    return summarize_full_run(run_dir) if is_full_run(run_dir) else summarize_section_run(run_dir)


# ----------------------------------------------------------------- render


def _cell(v: Any) -> str:
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v)


def render(summary: Dict[str, Any]) -> str:
    name = Path(summary["run_dir"]).name
    lines: List[str] = [f"# apps_rg E2E Run Summary — `{name}`", ""]
    counts = summary.get("counts", {})
    count_str = " | ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "no lanes"
    lines.append(f"mode: **{summary['mode']}** · lanes: {len(summary['lanes'])} · {count_str}")
    lines.append("")
    lines.append("| Lane | State | Provider | Model | Gen | X1D | X2 fail | X3 | Authorized | Blocker |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in summary["lanes"]:
        lines.append(
            "| `{lane}` | {state} | {provider} | {model} | {gen} | {x1d} | {x2} | {x3} | {auth} | {blk} |".format(
                lane=r.get("lane", _DASH),
                state=r.get("state", _DASH),
                provider=_cell(r.get("provider", _DASH)),
                model=_cell(r.get("model", _DASH)),
                gen=_cell(r.get("runtime_generation_status", _DASH)),
                x1d=_cell(r.get("x1d", _DASH)),
                x2=_cell(r.get("x2_failed", _DASH)),
                x3=_cell(r.get("x3", _DASH)),
                auth=_cell(r.get("authorized", _DASH)),
                blk=str(r.get("blocker", _DASH))[:80],
            )
        )
    lines.append("")
    return "\n".join(lines)


def _latest_e2e_dir() -> Optional[Path]:
    if not E2E_ROOT.is_dir():
        return None
    candidates = [p for p in E2E_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def main(argv: List[str]) -> int:
    if len(argv) > 1 and argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0
    if len(argv) > 1:
        run_dir = Path(argv[1]).resolve()
    else:
        latest = _latest_e2e_dir()
        if latest is None:
            print(f"No E2E dirs found under {E2E_ROOT}.", file=sys.stderr)
            return 2
        run_dir = latest
    if not run_dir.is_dir():
        print(f"Run dir not found: {run_dir}", file=sys.stderr)
        return 2
    sys.stdout.write(render(summarize(run_dir)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
