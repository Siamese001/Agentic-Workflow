"""Run full test suite and capture summary stats to file."""
import subprocess

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--tb=no", "--no-header", "-p", "no:warnings", "-q"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=600
)
# Write full output to file
with open("artifacts/test_suite_output.txt", "w", encoding="utf-8") as f:
    f.write(r.stdout)
    f.write("\n--- STDERR ---\n")
    f.write(r.stderr)

# Print last 10 lines
lines = (r.stdout + "\n" + r.stderr).strip().split("\n")
for line in lines[-10:]:
    print(line)
print(f"\nExit code: {r.returncode}")
