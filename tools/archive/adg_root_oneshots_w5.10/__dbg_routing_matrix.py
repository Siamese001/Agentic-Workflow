import subprocess
import sys

base = "tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_routing_matrix.py"

# Collect tests
r = subprocess.run(
    [sys.executable, "-m", "pytest", base, "--collect-only", "-q", "--no-header"],
    capture_output=True,
    text=True,
    timeout=10,
    cwd="C:/Git/Agentic-Workflow",
)
classes = set()
for l in r.stdout.splitlines():
    l = l.strip()
    if l.startswith("<Class"):
        classes.add(l.replace("<Class ", "").replace(">", ""))

print("Classes:", classes)
for cls in sorted(classes):
    path = f"{base}::{cls}"
    try:
        r2 = subprocess.run(
            [sys.executable, "-m", "pytest", path, "--tb=no", "-q", "--no-header"],
            capture_output=True,
            text=True,
            timeout=12,
            cwd="C:/Git/Agentic-Workflow",
        )
        out = (r2.stdout + r2.stderr).strip().split("\n")
        summary = [l for l in out if "passed" in l or "failed" in l or "error" in l]
        print(f"  {cls}: {summary[-1] if summary else 'no summary'}")
    except (TimeoutError, ValueError, TypeError, RuntimeError):
        print(f"  {cls}: TIMEOUT (HANGS)")
