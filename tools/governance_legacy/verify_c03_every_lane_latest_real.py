#!/usr/bin/env python3
"""Verify C0.3 spine + skills authority on latest REAL run per GENERATED_LANE."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES  # noqa: E402

PROOFS_ROOT = REPO / "artifacts" / "apps_rg" / "runtime_proofs"


def _latest_real_run(lane: str) -> Path | None:
    lane_dir = PROOFS_ROOT / lane / "real"
    if not lane_dir.is_dir():
        return None
    runs = [p for p in lane_dir.iterdir() if p.is_dir()]
    if not runs:
        return None
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0]


def _check_run(lane: str, run_dir: Path) -> dict:
    spine_path = run_dir / "section_spine_c0_retrieve_receipt.json"
    ledger_path = run_dir / "section_input_usage_ledger.json"
    out: dict = {
        "lane": lane,
        "run_dir": str(run_dir.relative_to(REPO)).replace("\\", "/"),
        "spine_receipt_present": spine_path.is_file(),
        "ledger_present": ledger_path.is_file(),
        "canonical_c0_3_graph_claimed": False,
        "graph_lane_deferred": True,
        "graph_traverse_ref": "",
        "augmented_skills_graph_authority": False,
        "pass": False,
    }
    if spine_path.is_file():
        spine = json.loads(spine_path.read_text(encoding="utf-8"))
        out["canonical_c0_3_graph_claimed"] = spine.get("canonical_c0_3_graph_claimed") is True
        out["graph_lane_deferred"] = spine.get("graph_lane_deferred") is True
        refs = spine.get("graph_expansion_refs") or []
        for ref in refs:
            if "ref:graph:traverse:" in str(ref):
                out["graph_traverse_ref"] = str(ref)
                break
    if ledger_path.is_file():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ia = ledger.get("input_authority") or {}
        out["augmented_skills_graph_authority"] = (
            ia.get("augmented_skills_graph") == "SKILLS_COMPETENCY_AUTHORITY"
        )
    out["pass"] = (
        out["spine_receipt_present"]
        and out["ledger_present"]
        and out["canonical_c0_3_graph_claimed"]
        and not out["graph_lane_deferred"]
        and out["augmented_skills_graph_authority"]
    )
    return out


def main() -> int:
    rows = []
    for lane in GENERATED_LANES:
        run = _latest_real_run(lane)
        if run is None:
            rows.append({"lane": lane, "run_dir": "", "pass": False, "error": "no_real_run"})
            continue
        rows.append(_check_run(lane, run))
    all_pass = all(r.get("pass") for r in rows)
    report = {"status": "PASS" if all_pass else "FAIL", "lanes": rows}
    out_path = REPO / "docs" / "reports" / "apps_rg" / "c03_every_lane_latest_real_verify.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
