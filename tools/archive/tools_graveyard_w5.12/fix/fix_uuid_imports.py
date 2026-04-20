"""Fix uuid imports: add module-level 'import uuid' to all files that use uuid.uuid4().

Does NOT remove local imports - they're harmless. Just ensures module-level is present.
"""

import ast
import os
import re

SCAN_DIRS = ["agentic_core", "system_learning", "apps", "utils"]

fixed = 0
errors = 0
already_ok = 0

for scan_dir in SCAN_DIRS:
    if not os.path.isdir(scan_dir):
        continue
    for root, dirs, files in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(root, fn)
            src = open(fp, encoding="utf-8", errors="replace").read()
            if "uuid.uuid4()" not in src:
                continue

            # Check if already has module-level import uuid (unindented)
            has_module = bool(re.search(r"^import uuid", src, re.MULTILINE))
            if has_module:
                already_ok += 1
                continue

            lines = src.split("\n")

            # Find insertion point: after last stdlib import at module level
            insert_idx = 0
            local_pkgs = ("agentic_core", "system_learning", "apps", "tools", "utils", "ops_scripts", ".")
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Only consider unindented imports
                if line and line[0] not in (" ", "\t"):
                    if stripped.startswith("from __future__"):
                        insert_idx = i + 1
                    elif stripped.startswith("import ") and not any(
                        stripped.startswith("import " + pkg) for pkg in local_pkgs
                    ):
                        insert_idx = i + 1
                    elif stripped.startswith("from ") and not any(
                        stripped.startswith("from " + pkg) for pkg in local_pkgs
                    ):
                        insert_idx = i + 1

            if insert_idx == 0:
                # Put after first line
                insert_idx = 1

            lines.insert(insert_idx, "import uuid")
            new_src = "\n".join(lines)

            try:
                ast.parse(new_src)
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(new_src)
                fixed += 1
            except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
                errors += 1
                if errors <= 10:
                    print(f"SYNTAX ERROR after fix: {fp}: {e}")

print(f"Fixed: {fixed}, Already OK: {already_ok}, Syntax errors: {errors}")
