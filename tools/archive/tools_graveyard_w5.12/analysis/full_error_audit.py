"""Full audit of ALL collection errors across ALL test directories."""

import os
import re
import subprocess
from collections import Counter

root = r"C:\Git\Agentic-Workflow"
# Scan each testpath independently to avoid cross-collection
test_dirs = [
    "tests/unit",
    "tests/architecture",
    "tests/enforcement",
    "tests/governance",
    "tests/sovereign_hardening",
    "tests/system_learning",
    "tests/unit_min_deps",
    "tests/integration/agentic_core",
]

all_errors = []
summary = []

for td in test_dirs:
    full_path = os.path.join(root, td.replace("/", os.sep))
    if not os.path.isdir(full_path):
        continue

    r = subprocess.run(
        ["python", "-m", "pytest", td, "--co", "--tb=short", "-q", "--override-ini=testpaths=" + td],
        capture_output=True,
        text=True,
        cwd=root,
        timeout=60,
        encoding="utf-8",
        errors="replace",
    )
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)

    # Parse collected/errors from last line
    m = re.search(r"(\d+) tests? collected(?:, (\d+) errors?)?", out)
    collected = int(m.group(1)) if m else 0
    nerr = int(m.group(2)) if m and m.group(2) else 0
    summary.append((td, collected, nerr))

    # Parse individual errors
    lines = out.split("\n")
    i = 0
    while i < len(lines):
        if "ERROR collecting" in lines[i]:
            test_file = re.search(r"(tests/\S+\.py)", lines[i])
            tf = test_file.group(1) if test_file else "unknown"
            src = ""
            cause = ""
            for j in range(i + 1, min(i + 25, len(lines))):
                s = lines[j].strip()
                sm = re.match(r"((?:agentic_core|apps_\w+|system_learning)[/\\].+\.py):(\d+)", s)
                if sm:
                    src = sm.group(1).replace("\\", "/")
                if s.startswith("E   ") and len(s) > 6:
                    msg = s[4:].strip()
                    if not msg.startswith("File ") and not msg.startswith("import "):
                        cause = msg
                        break
            all_errors.append({"dir": td, "test": tf, "src": src, "cause": cause})
        i += 1

# Print summary
print("=" * 70)
print(f"{'Directory':<45} {'Collected':>10} {'Errors':>8}")
print("-" * 70)
total_c, total_e = 0, 0
for td, c, e in summary:
    print(f"{td:<45} {c:>10} {e:>8}")
    total_c += c
    total_e += e
print("-" * 70)
print(f"{'TOTAL':<45} {total_c:>10} {total_e:>8}")

# Group errors by cause
print(f"\n{'=' * 70}")
print(f"Errors by root cause ({len(all_errors)} total):")
cause_counter = Counter()
for e in all_errors:
    c = e["cause"][:100] if e["cause"] else "unknown/parse-failed"
    cause_counter[c] += 1

for cause, count in cause_counter.most_common(30):
    print(f"  [{count:3d}] {cause}")

# Group errors by source file
print("\nErrors by source file:")
src_counter = Counter()
for e in all_errors:
    s = e["src"] if e["src"] else "unknown"
    src_counter[s] += 1

for src, count in src_counter.most_common(20):
    print(f"  [{count:3d}] {src}")
