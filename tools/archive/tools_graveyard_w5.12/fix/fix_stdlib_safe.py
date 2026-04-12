"""Fix missing stdlib imports SAFELY.

Strategy: Insert ONLY single-line import statements at module level.
NEVER insert inside multi-line import blocks or indented code.

Safe anchor: Insert right AFTER the line 'import logging' (which every
affected file has at module level), BEFORE the lifecycle_trace_contract block.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"

# Map: symbol name -> (module, import_line)
STDLIB = {
    "Any": ("typing", "from typing import Any"),
    "Optional": ("typing", "from typing import Optional"),
    "dataclass": ("dataclasses", "from dataclasses import dataclass"),
    "field": ("dataclasses", "from dataclasses import field"),
    "Enum": ("enum", "from enum import Enum"),
    "Path": ("pathlib", "from pathlib import Path"),
    "BaseModel": ("pydantic", "from pydantic import BaseModel"),
    "ConfigDict": ("pydantic", "from pydantic import ConfigDict"),
}

fixed = 0

for base in ["agentic_core", "apps_shared", "apps_lic", "apps_rg", "system_learning"]:
    scan = os.path.join(ROOT, base)
    if not os.path.isdir(scan):
        continue
    for dp, _, fns in os.walk(scan):
        for fn in fns:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dp, fn)
            try:
                with open(fp, encoding="utf-8") as f:
                    content = f.read()
            except (ValueError, TypeError, RuntimeError) as e:
                continue

            # Find which symbols are used but not imported
            needed = {}  # module -> set of (symbol, import_line)
            for sym, (mod, imp_line) in STDLIB.items():
                # Usage check (word boundary)
                if sym == "field":
                    if not re.search(r"\bfield\s*\(", content):
                        continue
                elif sym == "Path":
                    if not re.search(r"\bPath\b(?![A-Za-z_])", content):
                        continue
                else:
                    if not re.search(r"\b" + re.escape(sym) + r"\b", content):
                        continue

                # Already imported? Check multiple patterns
                if re.search(r"^import\s+" + re.escape(sym) + r"\b", content, re.MULTILINE):
                    continue
                if re.search(r"^\s*" + re.escape(sym) + r"\s*[,)]", content, re.MULTILINE):
                    # Inside a multi-line import block
                    continue
                if re.search(r"from\s+\S+\s+import\s+.*\b" + re.escape(sym) + r"\b", content):
                    continue
                # Local definition?
                if f"class {sym}" in content or (
                    f"{sym} =" in content and sym not in ("Any", "Optional", "Enum", "BaseModel", "dataclass")
                ):
                    continue

                needed.setdefault(mod, set()).add((sym, imp_line))

            if not needed:
                continue

            # Build import lines to insert (combine by module)
            insert_lines = []
            for mod, syms in sorted(needed.items()):
                sym_names = sorted(s[0] for s in syms)
                insert_lines.append(f"from {mod} import {', '.join(sym_names)}")

            # Find safe insertion point: right after 'import logging' at column 0
            lines = content.split("\n")
            insert_pos = None
            for i, line in enumerate(lines):
                # Must be at column 0 (module level)
                if line == "import logging" or line.startswith("import logging "):
                    insert_pos = i + 1
                    break

            if insert_pos is None:
                # Fallback: after first module-level 'import' or 'from __future__'
                for i, line in enumerate(lines):
                    if (
                        line.startswith("import ") or line.startswith("from __future__")
                    ) and not line.startswith("    "):
                        insert_pos = i + 1
                        # Keep looking for a better spot
                        continue

            if insert_pos is None:
                # Last resort: after docstring
                for i, line in enumerate(lines):
                    s = line.strip()
                    if i > 0 and s == '"""':
                        insert_pos = i + 1
                        break
                    if s.startswith('"""') and s.endswith('"""') and len(s) > 3:
                        insert_pos = i + 1
                        break

            if insert_pos is None:
                continue

            # Verify insertion point is at module level (column 0 or empty line)
            if insert_pos < len(lines):
                next_line = lines[insert_pos] if insert_pos < len(lines) else ""
                # Don't insert if next line is indented (inside a block)
                if next_line and next_line[0] in (" ", "\t") and not next_line.strip().startswith("#"):
                    # This might be inside a function - skip
                    continue

            # Insert the import lines
            for k, imp in enumerate(insert_lines):
                lines.insert(insert_pos + k, imp)

            new_content = "\n".join(lines)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fp, ROOT)
            if fixed <= 15:
                syms = "; ".join(
                    f"{m}: {','.join(sorted(s[0] for s in ss))}" for m, ss in sorted(needed.items())
                )
                print(f"  Fixed: {rel} ({syms})")

if fixed > 15:
    print(f"  ... and {fixed - 15} more")
print(f"\nTotal: {fixed} files fixed")
