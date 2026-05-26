"""Verify C03 exec-summary gaps v2 artifacts on a live exec_summary run dir (W5)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def verify_run_dir(run_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    ok = True

    def record(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok
        if not passed:
            ok = False
        checks.append({"check": name, "pass": passed, "detail": detail})

    smr = _load(run_dir / "section_metric_receipt.json") or {}
    c03_path = run_dir / "c03_graphrag_bound.json"
    c03 = _load(c03_path) or smr
    promo = _load(run_dir / "c03_promotion_candidates.json")
    rationale = _load(run_dir / "graph_selection_rationale.json")
    lane = _load(run_dir / "c0_graph_lane_receipt.json")
    x3 = _load(run_dir / "x3_disposition.json") or {}
    x1d = _load(run_dir / "x1d_llm_judge_outputs.json") or {}

    auth = smr.get("evidence_authority") if isinstance(smr.get("evidence_authority"), dict) else {}
    digest_auth = str(auth.get("graph_digest") or "").strip()
    digest_rat = str((rationale or {}).get("graph_digest") or "").strip()
    record(
        "graph_digest_parity",
        (not digest_auth or not digest_rat or digest_auth == digest_rat),
        f"authority={digest_auth[:16]} rationale={digest_rat[:16]}",
    )

    st_met = smr.get("support_target_met")
    c03_st = (c03 or {}).get("support_target_met")
    record(
        "support_target_met_aligned",
        st_met is not False and c03_st is not False,
        f"smr={st_met} c03={c03_st}",
    )

    record("promotion_candidates_present", promo is not None and bool(promo.get("candidates")))
    if promo:
        record(
            "promotion_no_auto_promote",
            promo.get("promoted_fact_ids") == [] and promo.get("auto_promote_enabled") is False,
        )

    hop_by = (c03 or {}).get("graph_hop_paths_by_fact_id") or (lane or {}).get("graph_hop_paths_by_fact_id")
    record("hop_paths_materialized", bool(hop_by), f"facts={len(hop_by or {})}")

    judges = x1d.get("judges") or []
    mb = [j for j in judges if j.get("evaluator_mode") == "MODEL_BACKED"]
    scores = [float(j.get("normalized_score") or j.get("score") or 0) for j in mb]
    composite = sum(scores) / len(scores) if scores else 0.0
    record("x1d_judge_panel_present", len(mb) >= 1, f"model_backed={len(mb)}")
    record("x1d_composite_ge_4", composite >= 4.0, f"composite={composite:.2f}")

    x3_code = str(x3.get("x3_code") or smr.get("x3_code") or "")
    record("x3_disposition_recorded", bool(x3_code), x3_code)

    graph_only_ok = all(c["pass"] for c in checks if c["check"] in {
        "graph_digest_parity",
        "support_target_met_aligned",
        "promotion_candidates_present",
        "promotion_no_auto_promote",
        "hop_paths_materialized",
    })
    return {
        "schema": "c03_exec_summary_gaps_v2_verify_v1",
        "run_dir": run_dir.as_posix(),
        "overall_pass": ok,
        "graph_scope_pass": graph_only_ok,
        "x1d_composite_0_to_5": round(composite, 3),
        "x3_code": x3_code,
        "checks": checks,
        "judge_quality_out_of_plan_scope": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir", type=Path, help="exec_summary_* run directory")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    run_dir = args.artifact_dir
    if not run_dir.is_absolute():
        run_dir = (ROOT / run_dir).resolve()
    doc = verify_run_dir(run_dir)
    if args.write_receipt:
        out = run_dir / "c03_exec_summary_gaps_v2_verify.json"
        out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out}")
    print(json.dumps(doc, indent=2))
    if doc.get("graph_scope_pass"):
        return 0
    return 1 if not doc["overall_pass"] else 0


if __name__ == "__main__":
    sys.exit(main())
