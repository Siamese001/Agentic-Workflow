"""Run test suite with all output redirected to file to avoid fd exhaustion."""
import subprocess
import os
import sys

# Suppress all lifecycle trace logging via env var
env = os.environ.copy()
env["LOG_LEVEL"] = "CRITICAL"
env["PYTHONDONTWRITEBYTECODE"] = "1"

# Write output to file
with open("artifacts/test_output.txt", "w", encoding="utf-8") as outf:
    proc = subprocess.Popen(
        [sys.executable, "-m", "pytest", "tests/unit/",
         "--tb=no", "--no-header", "-q",
         "-p", "no:warnings", "-p", "no:logging", "-p", "no:cacheprovider",
         "-s"],  # disable capture
        stdout=outf, stderr=subprocess.STDOUT,
        encoding="utf-8", errors="replace",
        env=env
    )
    try:
        proc.wait(timeout=600)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("TIMEOUT after 600s")

# Read last 10 lines
with open("artifacts/test_output.txt", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()
    for line in lines[-10:]:
        print(line.rstrip())
print(f"\nReturn code: {proc.returncode}")
