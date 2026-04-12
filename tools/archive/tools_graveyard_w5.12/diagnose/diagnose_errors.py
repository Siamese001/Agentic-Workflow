"""Diagnose test collection errors by directory."""

import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

r = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--co", "-q", "-p", "no:logging", "--tb=line"],
    capture_output=True,
    text=True,
    cwd=ROOT,
    timeout=120,
)
clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)

# Count errors by type
error_types = {}
for line in clean.split("\n"):
    s = line.strip()
    if s.startswith("E   "):
        # Extract the error type
        msg = s[4:].strip()
        # Get first part up to ':'
        if ":" in msg:
            etype = msg.split(":")[0].strip()
        else:
            etype = msg[:80]
        error_types[etype] = error_types.get(etype, 0) + 1

print("=== Error type frequency ===")
for etype, count in sorted(error_types.items(), key=lambda x: -x[1]):
    print(f"  {count:3d}x  {etype}")

# Count by file
print("\n=== Error source files ===")
file_errors = {}
for line in clean.split("\n"):
    s = line.strip()
    if s.startswith("E     File "):
        fpath = s.split('"')[1] if '"' in s else s[11:]
        fpath = fpath.replace(ROOT + "\\", "").replace(ROOT + "/", "")
        file_errors[fpath] = file_errors.get(fpath, 0) + 1

for fpath, count in sorted(file_errors.items(), key=lambda x: -x[1])[:30]:
    print(f"  {count:3d}x  {fpath}")

# Count ERROR collecting lines
print("\n=== ERROR collecting by directory ===")
dir_errors = {}
for line in clean.split("\n"):
    if "ERROR collecting" in line:
        # Extract test path
        match = re.search(r"tests[/\\](\w+)", line)
        if match:
            d = match.group(1)
            dir_errors[d] = dir_errors.get(d, 0) + 1

for d, count in sorted(dir_errors.items(), key=lambda x: -x[1]):
    print(f"  {count:3d}x  tests/{d}/")

print(f"\nTotal: {sum(dir_errors.values())} collection errors")
