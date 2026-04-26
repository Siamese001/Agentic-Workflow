"""Verify py_compile across files we changed in Wave 2."""
import subprocess
import sys
from pathlib import Path

# Reconstruct list from git status
r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=30)
changed = []
for line in r.stdout.splitlines():
    parts = line.strip().split(maxsplit=1)
    if len(parts) == 2:
        path = parts[1]
        if path.endswith(".py") and not path.startswith("tools/analysis/"):
            changed.append(Path(path))

print(f"Found {len(changed)} changed .py files")

failures = []
for path in changed:
    if not path.exists():
        continue
    r = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        failures.append((path, r.stderr.strip()))

print(f"py_compile failures: {len(failures)}/{len(changed)}")
for p, e in failures[:30]:
    print(f"  FAIL {p}")
    for line in e.splitlines()[:3]:
        print(f"     {line}")
