"""W12 regenerated lane matrix for W11-W13 closeout."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

REPO = find_repo_root()
RUNS = (
    ("headline", "headline_20260518_233957"),
    ("headline", "headline_20260518_233603"),
    ("ibm_bullets", "ibm_bullets_20260518_233826"),
    ("ibm_bullets", "ibm_bullets_20260518_224815"),
)


def main() -> int:
    rows = []
    for lane, run_id in RUNS:
        rd = REPO / "artifacts/apps_rg/runtime_proofs" / lane / "real" / run_id
        x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
        x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
        rows.append(
            {
                "lane": lane,
                "run_id": run_id,
                "artifact_dir": rd.relative_to(REPO).as_posix(),
                "x3_code": x3.get("x3_code"),
                "runtime_generation_status": x3.get("runtime_generation_status"),
                "x2_failed": int(x2.get("x2_failed") or 0),
                "soft_failed_judges": x3.get("soft_failed_judges") or [],
                "mocked_judges": x3.get("mocked_judges") or [],
                "rollup_selected": run_id in ("headline_20260518_233603", "ibm_bullets_20260518_224815"),
            },
        )
    blob = {
        "schema": "apps_rg.regenerated_lane_matrix_w11_w13.v1",
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "regenerations": rows,
    }
    out = REPO / "artifacts/apps_rg/runtime_proofs/final_resume_assembly/regenerated_lane_matrix_w11_w13.json"
    out.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
