import subprocess
import sys

base = "tests/unit/agentic_core/L0_routing/scripts"

# Check individual test methods in the hanging files
hanging_files = [
    "test_execute_ssot_healing_routing_fixes.py",
    "test_execute_ssot_routing_matrix.py",
    "test_sovereign_decision_engine.py",
]

for f in hanging_files:
    # Collect tests first
    r = subprocess.run(
        [sys.executable, "-m", "pytest", base + "/" + f, "--collect-only", "-q", "--no-header"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd="C:/Git/Agentic-Workflow",
    )
    tests = [l.strip() for l in r.stdout.splitlines() if "::" in l and not l.startswith("=")]
    print(f"=== {f}: {len(tests)} tests ===")
    for t in tests[:5]:  # check first 5 only
        try:
            r2 = subprocess.run(
                [sys.executable, "-m", "pytest", t, "--tb=no", "-q", "--no-header"],
                capture_output=True,
                text=True,
                timeout=8,
                cwd="C:/Git/Agentic-Workflow",
            )
            out = (r2.stdout + r2.stderr).strip().split("\n")
            summary = [l for l in out if "passed" in l or "failed" in l or "error" in l]
            print(f"  {t.split('::')[-1]}: {summary[-1] if summary else 'no summary'}")
        except (TimeoutError, ValueError, TypeError, RuntimeError):
            print(f"  {t.split('::')[-1]}: TIMEOUT (HANGS)")
