"""Fast per-file test scan: categorize failures vs timeouts."""

import pathlib
import re
import subprocess
import sys

root = pathlib.Path(r"C:\Git\Agentic-Workflow")

test_dirs = [
    root / "tests" / "architecture",
    root / "tests" / "adg",
    root / "tests" / "guardian",
]

total_p = total_f = total_s = 0
failures = []
timeouts = []
errors = []

for tdir in test_dirs:
    for tf in sorted(tdir.glob("test_*.py")):
        try:
            r = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(tf),
                    "-c",
                    "tools/pytest_minimal.ini",
                    "--tb=line",
                    "-p",
                    "no:warnings",
                    "-q",
                    "--timeout=15",
                    "--continue-on-collection-errors",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(root),
                timeout=30,
                stdin=subprocess.DEVNULL,
            )
            for line in r.stdout.splitlines():
                mp = re.search(r"(\d+) passed", line)
                mf = re.search(r"(\d+) failed", line)
                ms = re.search(r"(\d+) skipped", line)
                me = re.search(r"(\d+) error", line)
                if mp or mf or me:
                    p = int(mp.group(1)) if mp else 0
                    f = int(mf.group(1)) if mf else 0
                    s = int(ms.group(1)) if ms else 0
                    e = int(me.group(1)) if me else 0
                    total_p += p
                    total_f += f
                    total_s += s
                    if f > 0 or e > 0:
                        rel = tf.relative_to(root)
                        # Get first failure reason
                        reason = ""
                        for fline in r.stdout.splitlines():
                            if "Error" in fline or "assert" in fline.lower():
                                reason = fline.strip()[:120]
                                break
                        if e > 0:
                            errors.append(f"{rel}: {e}E — {reason}")
                        if f > 0:
                            failures.append(f"{rel}: {f}F — {reason}")
                    break
        except subprocess.TimeoutExpired:
            rel = tf.relative_to(root)
            timeouts.append(str(rel))

print(f"=== RESULTS: {total_p}P {total_f}F {total_s}S ===")
print(f"\n--- REAL FAILURES ({len(failures)}) ---")
for f in failures:
    print(f"  {f}")
print(f"\n--- COLLECTION ERRORS ({len(errors)}) ---")
for e in errors:
    print(f"  {e}")
print(f"\n--- TIMEOUTS ({len(timeouts)}) ---")
for t in timeouts:
    print(f"  {t}")
