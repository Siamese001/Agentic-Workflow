# golden_trace_auditor.py
# Executes golden flows, captures traces, compares against golden_traces.json.

import os
import sys
import json
import hashlib
import subprocess

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
GOLDEN_PATH = os.path.join(REPO_ROOT, "golden_traces.json")

def run_golden_flows():
    """
    You customize this to run your end-to-end flows.
    For example:
        python main.py --golden-flow resume
    It must output a JSON trace representing:
      - tools used
      - policies triggered
      - memory writes
      - reasoning trajectory
    """
    proc = subprocess.run(
        ["python", "main.py", "--golden-flow"],
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        print("Golden flow execution failed:")
        print(proc.stderr)
        sys.exit(2)

    try:
        trace = json.loads(proc.stdout)
        return trace
    except Exception as e:
        print("Failed to parse golden flow trace:", e)
        sys.exit(2)

def hash_trace(obj):
    s = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    if not os.path.exists(GOLDEN_PATH):
        print(f"Missing golden_traces.json at {GOLDEN_PATH}")
        sys.exit(1)

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        golden = json.load(f)

    new_trace = run_golden_flows()
    new_hash = hash_trace(new_trace)

    old_hash = golden.get("trace_hash")
    if not old_hash:
        print("golden_traces.json missing 'trace_hash'.")
        sys.exit(2)

    if new_hash != old_hash:
        print("\n=== GOLDEN TRACE MISMATCH ===")
        print(f"Old hash: {old_hash}")
        print(f"New hash: {new_hash}")
        print("Behavioral drift detected.")
        sys.exit(2)

    print("Golden trace validation PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
