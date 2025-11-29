#!/usr/bin/env python3
"""
golden_trace_auditor.py
Executes golden flows and compares trace hash with golden_traces.json.

Covers:
- Golden trace schema presence
- Behavioral drift detection via hash mismatch
"""

import os
import sys
import json
import hashlib
import subprocess

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
GOLDEN_PATH = os.path.join(REPO_ROOT, "golden_traces.json")


def run_flow():
    """Run the golden flow via main.py --golden-flow and return parsed JSON trace."""
    proc = subprocess.run(
        [sys.executable, "main.py", "--golden-flow"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print("[GOLDEN] Golden flow execution failed")
        print(proc.stderr)
        sys.exit(2)

    try:
        return json.loads(proc.stdout)
    except Exception as e:
        print("[GOLDEN] Failed to parse golden trace JSON:", e)
        sys.exit(2)


def hash_trace(trace: dict) -> str:
    s = json.dumps(trace, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    if not os.path.exists(GOLDEN_PATH):
        print(f"[GOLDEN] Missing golden_traces.json at {GOLDEN_PATH}")
        sys.exit(1)

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        golden = json.load(f)

    old_hash = golden.get("trace_hash")
    if not old_hash:
        print("[GOLDEN] golden_traces.json missing 'trace_hash'")
        sys.exit(2)

    new_trace = run_flow()
    new_hash = hash_trace(new_trace)

    if new_hash != old_hash:
        print("\n=== GOLDEN TRACE MISMATCH ===")
        print("Old:", old_hash)
        print("New:", new_hash)
        print("Behavioral drift detected.")
        sys.exit(2)

    print("Golden trace audit PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
