"""Check what RootHygieneAgent actually scanned vs what exists."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
data = json.loads((ROOT / "logs/compliance_reports/heal_run_complete.json").read_text())

print("=== WHAT ROOTHYGIENEAGENT REPORTED ===")
for a in data["healing_actions"]:
    if "RootHygiene" in a["agent"]:
        print(f"Agent: {a['agent']}")
        print(f"Territory: {a['territory']}")
        print(f"Outcome: {a['outcome']}")
        print(f"Summary: {a['fix_summary']}")
        print()

print("\n=== APPROVED ROOT FILES (from agent code) ===")
approved_files = {
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    ".env",
    ".env.example",
    ".flake8",
    ".mypy.ini",
    ".pre-commit-config.yaml",
    ".windsurfrules",
    ".windsurfrules.bak",
    ".windsurf.code-workspace",
    ".windsurfignore",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "requirements-dev.txt",
    "noxfile.py",
    "Makefile",
    "pytest.ini",
    "tox.ini",
    "MANIFEST.in",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    ".coverage",
    "progress.txt",
    "conftest.py",
    "runtime_state.json",
}

print("\n=== ACTUAL UNAPPROVED ROOT FILES ===")
unapproved = []
for f in ROOT.iterdir():
    if f.is_file() and f.name not in approved_files and not f.name.startswith(".git"):
        unapproved.append((f.name, f.stat().st_size))

print(f"Found {len(unapproved)} unapproved root files:")
for name, size in sorted(unapproved):
    print(f"  {name:<35} {size:>10,} bytes")

print("\n=== RCA: WHY DID ROOTHYGIENEAGENT MISS THESE? ===")
print("Checking agent's scan_root_violations() logic...")

# The agent scans self.project_root.iterdir() and flags anything not in approved_files
# So it SHOULD have found all 15 files. Let's check if it ran at all.
rh_actions = [a for a in data["healing_actions"] if "RootHygiene" in a["agent"]]
if not rh_actions:
    print("  ❌ RootHygieneAgent did NOT run at all")
else:
    for a in rh_actions:
        print(f"  Territory: {a['territory']}")
        print(f"  Outcome: {a['outcome']}")
        print(f"  Fix summary: {a['fix_summary']}")

        # Parse the fix summary to see what it actually found
        import re

        m = re.search(r"(\d+) violation", a["fix_summary"] or "")
        if m:
            found_count = int(m.group(1))
            print(f"  Violations found: {found_count}")
            print(f"  Expected: {len(unapproved)}")
            if found_count < len(unapproved):
                print(f"  ❌ MISSED {len(unapproved) - found_count} violations")
