"""Pick per-lane runs with full aggregation proof artifacts and rewrite generated_lane_rollup.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apps_rg.runtime.aggregation.preflight import REQUIRED_PROOF_FILES
from apps_rg.runtime.internal.generated_lane_rollup import (
    GENERATED_LANES,
    collect_lane_from_run_dir,
    render_markdown,
)
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root

REPO = find_repo_root()
RUNTIME_PROOFS = REPO / "artifacts" / "apps_rg" / "runtime_proofs"
ROLLUP_PATH = RUNTIME_PROOFS / "generated_lane_rollup" / "generated_lane_rollup.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_has_required(run_dir: Path) -> bool:
    for name in REQUIRED_PROOF_FILES:
        if not (run_dir / name).is_file():
            return False
    pool = _load_json(run_dir / "x2_source_fact_pool_receipt.json")
    if str(pool.get("x2_source_fact_pool_status") or "") != "PASS":
        return False
    x2 = _load_json(run_dir / "x2_gate_outputs.json")
    if int(x2.get("x2_failed") or 0) > 0:
        return False
    l2 = _load_json(run_dir / "l2_output.json")
    if str(l2.get("product_quality_status") or "") == "FAIL":
        return False
    return True


def _run_product_proof_score(run_dir: Path) -> int:
    """Higher = better for product-proof rollup pin (W8-W10)."""
    if not _run_has_required(run_dir):
        return -1000
    x3 = _load_json(run_dir / "x3_disposition.json")
    code = str(x3.get("x3_code") or "")
    rgs = str(x3.get("runtime_generation_status") or "")
    auth = str(x3.get("authorization_scope") or "")
    if rgs == "OFFLINE_CONTRACT_STUB":
        return -500
    if "MOCK" in code.upper() or auth == "PLUMBING_ONLY":
        return -400
    if code == "X3_ALLOW" and rgs == "REAL_LLM" and auth == "PRODUCT_QUALITY":
        return 300
    if code == "X3_ALLOW" and rgs == "REAL_LLM":
        return 250
    if "REVIEW" in code.upper() and rgs == "REAL_LLM":
        return 100
    if rgs == "REAL_LLM":
        return 50
    return 0


def _candidate_run_dirs(lane: str) -> list[Path]:
    lane_root = RUNTIME_PROOFS / lane
    out: list[Path] = []
    for bucket in ("real", "mock"):
        base = lane_root / bucket
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if child.is_dir():
                out.append(child)
    return out


def _pick_lane_run(lane: str, prefer_date: str | None, *, product_proof: bool = False) -> Path | None:
    candidates = [d for d in _candidate_run_dirs(lane) if _run_has_required(d)]
    if not candidates:
        return None
    if prefer_date:
        dated = [d for d in candidates if prefer_date in d.name]
        if dated:
            candidates = dated
    if product_proof:
        return max(candidates, key=_run_product_proof_score)
    return candidates[0]


def build_coherent_rollup(*, prefer_date: str | None = None, product_proof: bool = False) -> dict:
    lane_rows: dict[str, dict] = {}
    chosen_date: str | None = prefer_date
    for lane in GENERATED_LANES:
        run_dir = _pick_lane_run(lane, chosen_date, product_proof=product_proof)
        if run_dir is None:
            raise SystemExit(f"No aggregation-ready run for lane {lane}")
        if chosen_date is None:
            chosen_date = run_dir.name.split("_")[0] if "_" in run_dir.name else None
        row = collect_lane_from_run_dir(lane, run_dir, repo=REPO)
        row["rollup_source_run_dir"] = run_dir.relative_to(REPO).as_posix()
        row["latest_successful_real_artifact_path"] = row["rollup_source_run_dir"]
        row["latest_successful_real_run_id"] = run_dir.name
        row["accepted_real_evidence_resolution"] = "coherent_aggregation_pin"
        lane_rows[lane] = row

    from datetime import datetime, timezone

    blob = {
        "rollup_id": f"generated_lane_rollup_coherent_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "coherent_aggregation_pin": True,
        "coherent_run_date_prefix": chosen_date,
        "product_proof_pin": product_proof,
        "lanes": lane_rows,
    }
    return blob


def main() -> int:
    parser = argparse.ArgumentParser(description="Build coherent aggregation rollup")
    parser.add_argument("--prefer-date", default="20260518", help="Prefer run_id date prefix YYYYMMDD")
    parser.add_argument("--write", action="store_true", help="Write generated_lane_rollup.json")
    parser.add_argument(
        "--product-proof",
        action="store_true",
        help="Prefer REAL_LLM + X3_ALLOW runs (reject stub/mock/plumbing)",
    )
    args = parser.parse_args()
    blob = build_coherent_rollup(
        prefer_date=args.prefer_date or None,
        product_proof=bool(args.product_proof),
    )
    if args.write:
        ROLLUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        ROLLUP_PATH.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_path = ROLLUP_PATH.with_suffix(".md")
        md_path.write_text(render_markdown(blob) + "\n", encoding="utf-8")
        print(f"Wrote {ROLLUP_PATH.relative_to(REPO)}")
    else:
        print(json.dumps({"rollup_id": blob["rollup_id"], "lanes": list(blob["lanes"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
