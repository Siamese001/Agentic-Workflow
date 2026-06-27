"""Materialize augmented skills graph to SQLite + validate + emit closeout receipt."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    materialize_augmented_skills_graph_sqlite,
    validate_materialized_sqlite,
)
from apps_rg.runtime.c03_graph_sqlite_context import (
    PROOF_CLASSIFICATION,
    assemble_c03_graph_sqlite_context,
    write_c03_graph_sqlite_context_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "docs/reports/apps_rg"
PLAN_ID = "graph-skills-sqlite-c03-w1"


def _receipt_paths() -> tuple[Path, Path]:
    out_dir_raw = os.environ.get("APPS_RG_AUGMENTED_SKILLS_GRAPH_SQLITE_RECEIPT_DIR")
    out_dir = Path(out_dir_raw) if out_dir_raw else DEFAULT_OUT_DIR
    return (
        out_dir / "augmented_skills_graph_sqlite_closeout_receipt.json",
        out_dir / "augmented_skills_graph_sqlite_closeout_receipt.md",
    )


def _run_cmd(argv: list[str]) -> dict[str, Any]:
    proc = subprocess.run(  # guardian: allow-chokepoint-bypass -- offline materialization receipt runs bounded repo scripts only
        argv, cwd=str(ROOT), capture_output=True, text=True, timeout=180
    )
    return {
        "command": " ".join(argv),
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-800:],
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def _section_projection_parity() -> dict[str, Any]:
    """Offline parity: W4/W14 projection runner still PASS after sqlite materialization."""
    cmd = [sys.executable, "apps_rg/fact_inventory/run_w4_w14_multilane_section_projection.py"]
    run = _run_cmd(cmd)
    status = "PASS" if run["exit_code"] == 0 else "FAIL"
    return {"status": status, "command_run": run}


def _w14b_traversal_parity() -> dict[str, Any]:
    cmd = [sys.executable, "apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py"]
    run = _run_cmd(cmd)
    status = "PASS" if run["exit_code"] == 0 else "FAIL"
    return {"status": status, "command_run": run}


def run_closeout(*, skip_parity: bool = False) -> dict[str, Any]:
    mat = materialize_augmented_skills_graph_sqlite(repo_root=ROOT)
    val = validate_materialized_sqlite(repo_root=ROOT)
    c03_bundle = assemble_c03_graph_sqlite_context(
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        section_id="executive_summary",
        selected_fact_ids=["fact_engineering_platform_001"],
        repo_root=ROOT,
    )
    c03_receipt_path = write_c03_graph_sqlite_context_receipt(c03_bundle, repo_root=ROOT)

    parity = {"section_projection": {"status": "SKIPPED"}, "w14b_traversal": {"status": "SKIPPED"}}
    if not skip_parity:
        parity["section_projection"] = _section_projection_parity()
        parity["w14b_traversal"] = _w14b_traversal_parity()

    overall = "PASS"
    if val.get("status") != "PASS":
        overall = "FAIL"
    if c03_bundle["receipt"].get("c03_integration_status") != "SQLITE_CONTEXT_AVAILABLE":
        overall = "FAIL"
    if not skip_parity:
        if parity["section_projection"].get("status") != "PASS":
            overall = "FAIL"
        if parity["w14b_traversal"].get("status") != "PASS":
            overall = "FAIL"

    receipt: dict[str, Any] = {
        "STATUS": overall,
        "PLAN_ID": PLAN_ID,
        "WAVE": "graph-sqlite-c03-w1",
        "SCOPE_MATCH": True,
        "FILES_CHANGED": [
            "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py",
            "apps_rg/runtime/c03_graph_sqlite_context.py",
            "apps_rg/runtime/c03_graphrag_bound.py",
            "apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py",
        ],
        "COMMANDS_RUN": [],
        "SQLITE_DB_PATH": mat["sqlite_db_path"],
        "TABLES_CREATED": mat["tables_created"],
        "GRAPH_VERSION": mat["graph_version"],
        "GRAPH_HASH": mat["graph_hash"],
        "C03_SQLITE_MATERIALIZER_CODE_VERSION": mat.get(
            "c03_sqlite_materializer_code_version"
        ),
        "NODE_COUNT": val.get("node_count"),
        "EDGE_COUNT": val.get("edge_count"),
        "SKILL_FACT_LINK_COUNT": val.get("skill_fact_link_count"),
        "SECTION_ELIGIBILITY_COUNT": val.get("section_eligibility_count"),
        "ROLE_FAMILY_PROJECTION_COUNT": val.get("role_family_projection_count"),
        "C0_3_INTEGRATION_STATUS": c03_bundle["receipt"]["c03_integration_status"],
        "C0_3_RECEIPT_PATH": str(
            c03_receipt_path.relative_to(ROOT)
            if c03_receipt_path.is_relative_to(ROOT)
            else c03_receipt_path
        ),
        "VALIDATION_RESULTS": val,
        "SECTION_PROJECTION_PARITY_STATUS": parity["section_projection"].get("status"),
        "W14B_TRAVERSAL_PARITY_STATUS": parity["w14b_traversal"].get("status"),
        "BROAD_SKILLS_LEDGER_STATUS": "non_authority",
        "PROOF_CLASSIFICATION": PROOF_CLASSIFICATION,
        "EXPLICIT_NON_CLAIMS": c03_bundle["receipt"]["explicit_non_claims"],
        "NEXT_RECOMMENDED_WAVE": "wire_c03_sqlite_context_into_section_prompt_assembly_read_only",
        "materialization_summary": mat,
        "c03_context_sample": {
            "pillar_count": len(c03_bundle["context"]["pillars"]),
            "skill_count": len(c03_bundle["context"]["skills"]),
            "bridge_edge_count": len(c03_bundle["context"]["bridge_edges"]),
        },
    }
    if not skip_parity:
        receipt["COMMANDS_RUN"].append(parity["section_projection"].get("command_run"))
        receipt["COMMANDS_RUN"].append(parity["w14b_traversal"].get("command_run"))

    out_json, out_md = _receipt_paths()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_md.write_text(_render_md(receipt), encoding="utf-8")
    return receipt


def _render_md(receipt: dict[str, Any]) -> str:
    lines = [
        "# Augmented skills graph SQLite closeout",
        "",
        f"- **STATUS**: {receipt.get('STATUS')}",
        f"- **PLAN_ID**: {receipt.get('PLAN_ID')}",
        f"- **SQLITE_DB_PATH**: [{Path(str(receipt.get('SQLITE_DB_PATH'))).name}]({str(receipt.get('SQLITE_DB_PATH')).replace(chr(92), '/')})",
        f"- **GRAPH_VERSION**: {receipt.get('GRAPH_VERSION')}",
        f"- **MATERIALIZER_CODE_VERSION**: `{receipt.get('C03_SQLITE_MATERIALIZER_CODE_VERSION')}`",
        f"- **GRAPH_HASH**: `{str(receipt.get('GRAPH_HASH', ''))[:16]}…`",
        f"- **NODE_COUNT**: {receipt.get('NODE_COUNT')} | **EDGE_COUNT**: {receipt.get('EDGE_COUNT')}",
        f"- **C0.3 integration**: {receipt.get('C0_3_INTEGRATION_STATUS')}",
        f"- **C0.3 receipt**: [{Path(str(receipt.get('C0_3_RECEIPT_PATH'))).name}]({str(receipt.get('C0_3_RECEIPT_PATH')).replace(chr(92), '/')})",
        f"- **Section projection parity**: {receipt.get('SECTION_PROJECTION_PARITY_STATUS')}",
        f"- **W14b traversal parity**: {receipt.get('W14B_TRAVERSAL_PARITY_STATUS')}",
        f"- **broad_skills_ledger**: {receipt.get('BROAD_SKILLS_LEDGER_STATUS')}",
        "",
        "## Proof classification",
        "",
        f"{receipt.get('PROOF_CLASSIFICATION')} — graph SQLite is routing/context only.",
        "",
        "Machine-readable: [augmented_skills_graph_sqlite_closeout_receipt.json](docs/reports/apps_rg/augmented_skills_graph_sqlite_closeout_receipt.json).",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    skip = "--skip-parity" in sys.argv
    receipt = run_closeout(skip_parity=skip)
    print(json.dumps({"STATUS": receipt["STATUS"], "SQLITE_DB_PATH": receipt["SQLITE_DB_PATH"]}, indent=2))
    return 0 if receipt["STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
