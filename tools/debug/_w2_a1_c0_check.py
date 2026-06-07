"""Confirm A1 orphan ratchet flagged the 5 active C0 stages."""

import json
from pathlib import Path

LOG = Path("artifacts/cursor/wiring_gate_violations.jsonl")
lines = LOG.read_text(encoding="utf-8").strip().splitlines()
a1_runs = [json.loads(line) for line in lines if "A1_orphan" in line]
assert a1_runs, "no A1 runs logged"
last = a1_runs[-1]
subjects = {v["subject"] for v in last["violations"]}

c0_active_stages = [
    "agentic_core/knowledge/retrieval/retrieval_plan.py",
    "agentic_core/knowledge/gates/preretrieval_gate.py",
    "agentic_core/knowledge/retrieval/hybrid_recall_stage.py",
    "agentic_core/knowledge/retrieval/senior_librarian_reranker.py",
    "agentic_core/knowledge/retrieval/evidence_contract_builder.py",
]
for m in c0_active_stages:
    flag = "FOUND" if m in subjects else "MISS "
    print(f"  {flag} {m}")

found = sum(1 for m in c0_active_stages if m in subjects)
print(f"\nsummary: {found}/{len(c0_active_stages)} C0 active stages flagged by A1")
print(f"total A1 violations: {len(last['violations'])}")
