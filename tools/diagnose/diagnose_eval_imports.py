"""Trace all missing modules in the evaluation import chain."""

import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

# Test each eval test file individually
eval_tests = [
    "tests/evaluation/test_eval_completeness_retrieval.py",
    "tests/evaluation/test_eval_feedback.py",
    "tests/evaluation/test_eval_metrics.py",
    "tests/evaluation/test_eval_monitoring.py",
    "tests/evaluation/test_eval_retrieval.py",
    "tests/evaluation/test_eval_runners.py",
    "tests/evaluation/test_hardening.py",
]

for test_file in eval_tests:
    r = subprocess.run(
        ["python", "-m", "pytest", test_file, "--co", "--tb=long", "-p", "no:logging", "-q"],
        capture_output=True, text=True, cwd=ROOT, timeout=30,
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)

    # Extract the full traceback for module errors
    for line in clean.split("\n"):
        s = line.strip()
        if "ModuleNotFoundError" in s or "ImportError" in s:
            print(f"[{test_file.split('/')[-1]}] {s[:200]}")
