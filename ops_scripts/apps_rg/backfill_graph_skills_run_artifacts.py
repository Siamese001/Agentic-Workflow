#!/usr/bin/env python3
"""Backfill graph_selection_rationale.json (+ native_c03) into latest real run dirs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import LANES
from apps_rg.runtime.graph_skills_run_artifacts import (
    RATIONALE_FILENAME,
    persist_graph_skills_lane_artifacts,
)

PROOFS = REPO / "artifacts" / "apps_rg" / "runtime_proofs"


def _latest_real(lane: str) -> Path | None:
    real = PROOFS / lane / "real"
    if not real.is_dir():
        return None
    runs = [p for p in real.iterdir() if p.is_dir()]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def main() -> int:
    updated = 0
    for lane in LANES:
        run_dir = _latest_real(lane)
        if run_dir is None:
            print(f"{lane}: no real run")
            continue
        payload_path = run_dir / "runtime_payload.json"
        if not payload_path.is_file():
            print(f"{lane}: missing runtime_payload.json")
            continue
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        paths = persist_graph_skills_lane_artifacts(
            run_dir,
            section_id=lane,
            runtime_payload=payload,
            repo_root=REPO,
        )
        if paths.get(RATIONALE_FILENAME):
            updated += 1
            print(f"{lane}: wrote {RATIONALE_FILENAME} -> {run_dir.name}")
        else:
            print(f"{lane}: skipped (insufficient targeting)")
    print(f"updated_lanes={updated}/{len(LANES)}")
    return 0 if updated else 1


if __name__ == "__main__":
    raise SystemExit(main())
