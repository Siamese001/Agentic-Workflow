"""Get detailed error breakdown from pytest collection."""

import re
import subprocess
from collections import Counter

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--co", "--tb=short", "-q"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=30,
)
out = r.stdout + "\n" + r.stderr

# Save raw output
with open("artifacts/collection_raw.txt", "w", encoding="utf-8") as f:
    f.write(out)

# Find all "ERROR collecting" blocks
lines = out.split("\n")
errors = []
current_test = None
current_cause = None
for line in lines:
    if "ERROR collecting" in line:
        m = re.search(r"(tests/\S+\.py)", line)
        current_test = m.group(1) if m else "unknown"
    elif current_test and ("Error" in line or "error" in line.lower()):
        if any(
            kw in line
            for kw in [
                "NameError",
                "FileNotFoundError",
                "ModuleNotFoundError",
                "ImportError",
                "PydanticUserError",
                "OSError",
                "AttributeError",
            ]
        ):
            current_cause = line.strip()
            errors.append((current_test, current_cause))
            current_test = None

# Group by cause
cause_counter = Counter()
for test, cause in errors:
    # Simplify cause
    short = cause[:100]
    cause_counter[short] += 1

print(f"Parsed {len(errors)} errors")
for cause, count in cause_counter.most_common(20):
    print(f"  [{count:3d}] {cause}")
