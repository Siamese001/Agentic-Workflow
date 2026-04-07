"""Get detailed breakdown of all collection errors grouped by root cause."""
import re
import subprocess
from collections import Counter

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--co", "-q", "--tb=short"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=60,
)
out = r.stdout + "\n" + r.stderr

# Write raw output for inspection
with open("artifacts/collection_errors_raw.txt", "w", encoding="utf-8") as f:
    f.write(out)

# Parse ERROR blocks
lines = out.split("\n")
errors = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith("ERROR") and "collecting" in line.lower():
        test_file = re.search(r"(tests/\S+)", line)
        # Collect the error cause from subsequent lines
        cause_lines = []
        for j in range(i+1, min(i+20, len(lines))):
            l = lines[j].strip()
            if l.startswith("ERROR") or l.startswith("="):
                break
            if "Error" in l or "error" in l.lower() or "NameError" in l or "FileNotFoundError" in l or "ModuleNotFoundError" in l or "ImportError" in l:
                cause_lines.append(l)
        errors.append({
            "test": test_file.group(1) if test_file else "unknown",
            "cause": cause_lines[-1] if cause_lines else "unknown",
        })
    i += 1

# Group by cause
cause_counter = Counter()
cause_tests = {}
for e in errors:
    cause = e["cause"][:120]
    cause_counter[cause] += 1
    cause_tests.setdefault(cause, []).append(e["test"])

print(f"Total collection errors: {len(errors)}")
print("\nErrors by root cause (top 20):")
for cause, count in cause_counter.most_common(20):
    print(f"  [{count:3d}] {cause}")
