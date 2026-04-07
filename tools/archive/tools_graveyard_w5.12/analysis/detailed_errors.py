"""Get detailed breakdown of all collection errors grouped by root cause."""
import re
import subprocess
from collections import Counter

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--co", "-q", "--tb=line"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    timeout=60,
)
out = r.stdout + "\n" + r.stderr

# Parse ERROR lines
error_lines = []
for line in out.split("\n"):
    if "ERROR" in line and "tests/" in line:
        error_lines.append(line.strip())

# Parse the actual error causes
causes = Counter()
source_to_tests = {}
for line in error_lines:
    # Format: ERROR tests/unit/path/test_file.py - ErrorType: message
    m = re.match(r"ERROR\s+(tests/\S+)\s*-\s*(.*)", line)
    if m:
        test_file = m.group(1)
        error = m.group(2).strip()
        causes[error] += 1
        source_to_tests.setdefault(error, []).append(test_file)

print(f"Total collection errors: {len(error_lines)}")
print("\nErrors by root cause:")
for cause, count in causes.most_common(20):
    print(f"  [{count:3d}] {cause[:120]}")
    if count <= 3:
        for tf in source_to_tests[cause]:
            print(f"        -> {tf}")
