"""Check how many files import from L0_routing/scripts/ — assess move feasibility."""

import pathlib
import re

REPO = pathlib.Path(".")
SCRIPTS_DIR = "agentic_core/L0_routing/scripts"

# Collect all script filenames
script_files = list(pathlib.Path(SCRIPTS_DIR).glob("*.py"))
script_modules = {f.stem for f in script_files}

# Search for imports of these modules across the repo
import_counts = {}
for stem in sorted(script_modules):
    pattern = re.compile(
        rf"from agentic_core\.L0_routing\.scripts\.{re.escape(stem)}|import agentic_core\.L0_routing\.scripts\.{re.escape(stem)}",
    )
    matches = []
    for py in REPO.rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                matches.append(str(py.relative_to(REPO)))
        except OSError:    # guardian: Add error context logging
            pass
    if matches:
        import_counts[stem] = matches

print(f"Scripts with external importers: {len(import_counts)}")
for stem, importers in sorted(import_counts.items()):
    print(f"\n  {stem}: {len(importers)} importer(s)")
    for imp in importers:
        print(f"    {imp}")

print(f"\nScripts with NO external importers: {len(script_modules) - len(import_counts)}")
standalone = sorted(script_modules - set(import_counts.keys()))
for s in standalone:
    print(f"  {s}")
