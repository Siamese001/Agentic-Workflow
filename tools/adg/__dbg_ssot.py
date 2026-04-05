import subprocess
import sys

r = subprocess.run(
    [sys.executable, "-c", "import agentic_core.L0_routing.scripts.execute_ssot; print('ok')"],
    capture_output=True,
    text=True,
    timeout=10,
    cwd="C:/Git/Agentic-Workflow",
)
print("rc:", r.returncode)
print("stdout:", r.stdout)
print("stderr:", r.stderr[:800])
