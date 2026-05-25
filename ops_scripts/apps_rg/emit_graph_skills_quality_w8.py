#!/usr/bin/env python3
"""W8: graph-skills utilization anti-gaming (D8) + CONTRACT receipt."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.graph_skills_utilization_scorer import (
    PLAN_ID,
    score_graph_skills_utilization,
)

REPORTS = REPO / "docs" / "reports" / "apps_rg"
UTILIZATION_JSON = REPORTS / "graph_skills_utilization_receipt.json"
RECEIPT_W8 = REPORTS / "graph_skills_quality_w8_receipt.json"
PYTEST_TARGET = "tests/unit/apps_rg/test_graph_skills_utilization_w8.py"


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def _run_pytest() -> tuple[bool, str]:
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", PYTEST_TARGET, "-q", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    tail = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, tail[-2000:]


def _contract_lane_fixtures() -> list[dict]:
    """Brown exec + competencies minimum (synthetic CONTRACT; not provider mock)."""
    exec_row = {
        "skill_id": "brown_exec_platform",
        "allowed_phrases": ["agentic ai platform"],
        "fact_id_links": ["fact_brown_exec_001"],
        "graph_hop_path": ["jd", "executive_summary", "brown_exec_platform"],
        "forbidden_phrases": ["unverified metric"],
    }
    comp_row = {
        "skill_id": "brown_comp_platform",
        "allowed_phrases": ["platform engineering"],
        "fact_id_links": ["fact_brown_comp_001"],
        "graph_hop_path": ["jd", "competencies", "brown_comp_platform"],
        "forbidden_phrases": [],
    }
    return [
        {
            "lane": "executive_summary",
            "skill_rows": [exec_row],
            "resume_display_text": (
                "Built an agentic-ai platform with governed runtime outcomes."
            ),
            "text_claim_coverage": {
                "sentences": [
                    {
                        "claim_text": "Built an agentic-ai platform with governed runtime outcomes.",
                        "cited_fact_ids": ["fact_brown_exec_001"],
                    }
                ]
            },
            "allowed_fact_ids": ["fact_brown_exec_001"],
        },
        {
            "lane": "competencies",
            "skill_rows": [comp_row],
            "resume_display_text": (
                "Led platform-engineering delivery with cited competency evidence."
            ),
            "text_claim_coverage": {
                "sentences": [
                    {
                        "claim_text": "Led platform-engineering delivery with cited competency evidence.",
                        "cited_fact_ids": ["fact_brown_comp_001"],
                    }
                ]
            },
            "allowed_fact_ids": ["fact_brown_comp_001"],
        },
    ]


def _probe_real_llm_dirs() -> list[str]:
    roots = [
        REPO / "artifacts" / "apps_rg" / "proof_pools",
        REPO / "artifacts" / "apps_rg" / "runs",
    ]
    hits: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("resume_display_text.txt"))[:3]:
            hits.append(str(path.relative_to(REPO)).replace("\\", "/"))
    return hits


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    pytest_ok, pytest_tail = _run_pytest()

    lane_receipts: list[dict] = []
    all_pass = True
    for fixture in _contract_lane_fixtures():
        receipt = score_graph_skills_utilization(
            section_id=str(fixture["lane"]),
            skill_rows=list(fixture["skill_rows"]),
            resume_display_text=str(fixture["resume_display_text"]),
            text_claim_coverage=dict(fixture["text_claim_coverage"]),
            allowed_fact_ids=list(fixture["allowed_fact_ids"]),
        )
        lane_receipts.append(receipt)
        if not receipt.get("pass"):
            all_pass = False

    real_llm_probe = _probe_real_llm_dirs()
    # Probe paths are hints only — W8 REAL_LLM requires live Brown exec+comp scoring.
    real_llm_executed = False

    utilization_doc = {
        "plan_id": PLAN_ID,
        "wave": "W8",
        "gate_id": "G-W8",
        "proof_class": "CONTRACT_TEST_PROOF",
        "real_llm_proof_class": "REAL_LLM_RUNTIME_PROOF",
        "real_llm_executed": real_llm_executed,
        "real_llm_probe_paths": real_llm_probe,
        "contract_test_pass": pytest_ok,
        "lanes": lane_receipts,
        "aggregate_pass": all_pass and pytest_ok,
        "utilization_score_mean": round(
            sum(float(r.get("utilization_score") or 0) for r in lane_receipts) / max(len(lane_receipts), 1),
            4,
        ),
        "git_commit": _git_commit(),
        "emitted_at": datetime.now(timezone.utc).isoformat(),
    }
    UTILIZATION_JSON.write_text(json.dumps(utilization_doc, indent=2) + "\n", encoding="utf-8")

    contract_ok = pytest_ok and all_pass
    if not contract_ok:
        status = "FAIL"
    elif real_llm_executed:
        status = "PASS"
    else:
        status = "PARTIAL"

    w8_receipt = {
        "plan_id": PLAN_ID,
        "wave": "W8",
        "status": status,
        "proof_classes": {
            "contract": "PASS" if contract_ok else "FAIL",
            "real_llm": "PASS" if real_llm_executed else "BLOCKED",
        },
        "artifacts": {
            "utilization_receipt": str(UTILIZATION_JSON.relative_to(REPO)).replace("\\", "/"),
        },
        "pytest_tail": pytest_tail,
        "git_commit": utilization_doc["git_commit"],
        "emitted_at": utilization_doc["emitted_at"],
    }
    RECEIPT_W8.write_text(json.dumps(w8_receipt, indent=2) + "\n", encoding="utf-8")

    print(f"STATUS: {status}")
    print(f"UTILIZATION: {UTILIZATION_JSON}")
    print(f"RECEIPT: {RECEIPT_W8}")
    return 0 if pytest_ok and all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
