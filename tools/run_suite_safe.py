"""Run full test suite with capture disabled to avoid fd exhaustion."""
import subprocess, os

env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/",
     "--tb=no", "--no-header", "-q",
     "-p", "no:warnings",
     "--capture=no",
     "--log-cli-level=CRITICAL",
     "--log-level=CRITICAL"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=600, env=env
)

# Get the summary line
all_out = r.stdout + "\n" + r.stderr
lines = all_out.strip().split("\n")
for line in lines[-10:]:
    print(line)
print(f"\nReturn code: {r.returncode}")
