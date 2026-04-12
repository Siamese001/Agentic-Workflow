"""
Fix WRONG_IMPORT violations from ssot_violation_scan.json.

Replaces:
  from agentic_core.L5_safety.config.structure_blueprint_config import X
  from structure_blueprint_config import X

With:
  from agentic_core.L5_safety.config.structure_blueprint import X

Usage:
    python ops_scripts/ci/_fix_wrong_imports.py [--dry-run]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DRY_RUN = "--dry-run" in sys.argv
report = json.loads((ROOT / "artifacts" / "ssot_violation_scan.json").read_text())
wrong_import_hits = [h for h in report["all_hits"] if h["classification"] == "WRONG_IMPORT"]
files_to_fix: set[str] = {h["file"] for h in wrong_import_hits}
REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    (
        re.compile("\\bfrom\\s+agentic_core\\.L5_safety\\.config\\.structure_blueprint_config\\s+import\\b"),
        "from agentic_core.L5_safety.config.structure_blueprint import",
    ),
    (
        re.compile("\\bimport\\s+agentic_core\\.L5_safety\\.config\\.structure_blueprint_config\\b"),
        "import agentic_core.L5_safety.config.structure_blueprint",
    ),
    (
        re.compile("\\bfrom\\s+structure_blueprint_config\\s+import\\b"),
        "from agentic_core.L5_safety.config.structure_blueprint import",
    ),
    (
        re.compile("\\bimport\\s+structure_blueprint_config\\b"),
        "import agentic_core.L5_safety.config.structure_blueprint",
    ),
]
fixed_files = 0
fixed_lines = 0
skipped_files = 0
for rel_path in sorted(files_to_fix):
    abs_path = ROOT / rel_path
    if not abs_path.exists():
        print(f"  [MISSING] {rel_path}")
        skipped_files += 1
        continue
    original = abs_path.read_text(encoding="utf-8", errors="replace")
    updated = original
    file_line_count = 0
    for pattern, replacement in REPLACEMENTS:
        new, n = pattern.subn(replacement, updated)
        if n:
            file_line_count += n
            updated = new
    if updated == original:
        continue
    if DRY_RUN:
        print(f"  [DRY RUN] {rel_path} ({file_line_count} replacements)")
    else:
        abs_path.write_text(updated, encoding="utf-8")
        print(f"  [FIXED]   {rel_path} ({file_line_count} replacements)")
    fixed_files += 1
    fixed_lines += file_line_count
print(f"\n{('DRY RUN — ' if DRY_RUN else '')}Fixed {fixed_files} files, {fixed_lines} import lines")
if skipped_files:
    print(f"Skipped {skipped_files} missing files")
