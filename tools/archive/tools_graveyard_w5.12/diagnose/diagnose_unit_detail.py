"""Get error details for unit test subdirectories with errors."""

import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

# Process each error-having subdirectory
for subdir in ["agentic_core", "apps_lic", "apps_rg", "apps_shared", "system_learning"]:
    path = f"tests/unit/{subdir}"
    r = subprocess.run(
        ["python", "-m", "pytest", path, "--co", "-q", "-p", "no:logging", "--tb=line"],
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)

    # Collect unique E   lines
    errors = set()
    for line in clean.split("\n"):
        s = line.strip()
        if s.startswith("E   ") and len(s) > 6:
            # Simplify the error message
            msg = s[4:].strip()
            if msg.startswith("File "):
                continue  # Skip traceback file references
            errors.add(msg[:150])

    if errors:
        print(f"\n=== tests/unit/{subdir}/ ===")
        for e in sorted(errors):
            print(f"  {e}")
