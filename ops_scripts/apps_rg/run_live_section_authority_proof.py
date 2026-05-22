#!/usr/bin/env python3
"""Run canonical section lanes and verify product_evidence_authority_receipt on disk."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SECTIONS = ("headline", "executive_summary", "unify_bullets", "unify_narrative")
REPO = Path(__file__).resolve().parents[2]
JD = REPO / "apps_rg/config/targeting/neo4j_vp_product_management_agentic_ai_jd.txt"
BRIEF = REPO / "tests/_fixtures/ci-probe-briefing.txt"


def _latest_ledger(lane: str) -> Path | None:
    root = REPO / "artifacts/apps_rg/runtime_proofs" / lane / "real"
    if not root.is_dir():
        return None
    candidates = list(root.glob("*/section_input_usage_ledger.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _verify_ledger(path: Path) -> dict[str, object]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    receipt = doc.get("product_evidence_authority_receipt") or {}
    ea = receipt.get("evidence_authority") or doc.get("evidence_authority") or {}
    if isinstance(doc.get("proof_pool_metadata"), dict):
        ea_meta = doc["proof_pool_metadata"].get("evidence_authority") or {}
        if not ea:
            ea = ea_meta
    ok = (
        str(ea.get("type") or (ea.get("authority") if isinstance(ea, dict) else "")) == "augmented_skills_graph"
        or receipt.get("evidence_authority", {}).get("type") == "augmented_skills_graph"
    )
    graph_present = receipt.get("evidence_authority", {}).get("graph_ref") == "present" or bool(
        str((ea if isinstance(ea, dict) else {}).get("graph_ref") or "").strip()
    )
    ledger_present = receipt.get("evidence_authority", {}).get("ledger_ref") == "present" or bool(
        str((ea if isinstance(ea, dict) else {}).get("ledger_ref") or "").strip()
    )
    return {
        "ledger_path": str(path.relative_to(REPO)).replace("\\", "/"),
        "exit_ok": ok and graph_present and ledger_present,
        "receipt": receipt,
        "ea_type": receipt.get("evidence_authority", {}).get("type"),
        "graph_ref": receipt.get("evidence_authority", {}).get("graph_ref"),
        "ledger_ref": receipt.get("evidence_authority", {}).get("ledger_ref"),
    }


def main() -> int:
    results: list[dict[str, object]] = []
    for lane in SECTIONS:
        cmd = [
            sys.executable,
            "-m",
            "apps_rg",
            "--section",
            lane,
            "--target-company",
            "Neo4j",
            "--target-role",
            "VP Product Management Agentic AI",
            "--jd",
            str(JD),
            "--manual-brief",
            str(BRIEF),
        ]
        proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
        ledger = _latest_ledger(lane)
        row: dict[str, object] = {
            "section": lane,
            "cli_exit_code": proc.returncode,
            "ledger_found": ledger is not None,
        }
        if ledger:
            row.update(_verify_ledger(ledger))
        else:
            row["exit_ok"] = False
            row["stderr_tail"] = (proc.stderr or proc.stdout or "")[-800:]
        results.append(row)
        print(json.dumps(row, indent=2))

    out = REPO / "artifacts/apps_rg/live_section_authority_proof_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"sections": results}, indent=2) + "\n", encoding="utf-8")
    all_ok = all(r.get("exit_ok") for r in results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
