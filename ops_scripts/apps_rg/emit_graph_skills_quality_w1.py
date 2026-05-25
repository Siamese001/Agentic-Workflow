#!/usr/bin/env python3
"""W1: JD subgraph rationale fixtures + receipt for graph-skills-quality-enhancement."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.graph_selection_rationale import write_graph_selection_rationale

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RATIONALE_DIR = REPORTS / "graph_skills_quality_w1_rationale"
W1_JSON = REPORTS / "graph_skills_quality_w1_jd_subgraph.json"
RECEIPT_JSON = REPORTS / "graph_skills_quality_w1_receipt.json"

TARGET_COMPANY = "Brown & Brown"
TARGET_ROLE = "SVP IT Strategy & Innovation"
JD_PATH = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF_DEFAULT = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
BRIEF_EXEC = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md"

LANES = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def _briefing_for(lane: str) -> str:
    path = BRIEF_EXEC if lane == "executive_summary" else BRIEF_DEFAULT
    return path.read_text(encoding="utf-8")


def main() -> int:
    jd_text = JD_PATH.read_text(encoding="utf-8")
    sections: dict[str, Any] = {}
    monotonic_failures: list[str] = []

    for lane in LANES:
        briefing = _briefing_for(lane)
        out_path = RATIONALE_DIR / f"{lane}.json"
        payload = write_graph_selection_rationale(
            out_path,
            section_id=lane,
            target_company=TARGET_COMPANY,
            target_role=TARGET_ROLE,
            jd_text=jd_text,
            briefing_text=briefing,
            repo_root=REPO,
        )
        audit = payload.get("track_weight_audit") or {}
        if not audit.get("jd_boost_monotonic"):
            monotonic_failures.append(lane)
        if not payload.get("neg1_all_selected_skills_have_fact_links"):
            monotonic_failures.append(f"{lane}:neg1")
        sections[lane] = {
            "rationale_path": out_path.relative_to(REPO).as_posix(),
            "role_family_key": payload.get("role_family_key"),
            "jd_boost_monotonic": audit.get("jd_boost_monotonic"),
            "jd_keyword_hit_count": len(payload.get("jd_keyword_hits") or []),
            "selected_skill_count": payload.get("selected_skill_count"),
            "selection_method": payload.get("selection_method"),
        }

    w1_status = "PASS" if not monotonic_failures else "FAIL"
    aggregate = {
        "schema": "graph_skills_quality_w1_jd_subgraph_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W1",
        "status": w1_status,
        "brown_jd_path": JD_PATH.relative_to(REPO).as_posix(),
        "sections": sections,
        "phase_gate_g_w1": {
            "gate": "G-W1",
            "status": "PASS" if w1_status == "PASS" else "FAIL",
            "graph_selection_rationale_per_lane": True,
            "jd_boost_monotonic_all_lanes": not monotonic_failures,
            "failures": monotonic_failures,
        },
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    W1_JSON.write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")

    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w1.py"]
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W1",
        "proof_class": "CONTRACT_TEST_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {},
        "exit_code": 0 if w1_status == "PASS" else 1,
        "artifact_paths": [
            W1_JSON.relative_to(REPO).as_posix(),
            RECEIPT_JSON.relative_to(REPO).as_posix(),
            *[v["rationale_path"] for v in sections.values()],
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W1", "status": "PASS" if w1_status == "PASS" else "FAIL"},
        "notes": "Fixture rationale only; REAL_LLM graph_selection_rationale.json is W10.",
    }
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": w1_status == "PASS", "status": w1_status, "w1": str(W1_JSON)}))
    return 0 if w1_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
