"""Fix remaining _emit_* NameErrors that the first batch missed.

Strategy: For each .py file under agentic_core/ and tests/, check if
_emit_reads_through, _emit_writes_through, or _emit_links_incident_trace
are called but not properly imported. If so, add them to the existing
lifecycle_trace_contract import block or create a new one.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"
SCAN_DIRS = [
    os.path.join(ROOT, "agentic_core"),
    os.path.join(ROOT, "tests"),
    os.path.join(ROOT, "system_learning"),
    os.path.join(ROOT, "apps_shared"),
]

SYMS = ["_emit_reads_through", "_emit_writes_through", "_emit_links_incident_trace"]
IMPORT_MOD = "agentic_core.runtime.lifecycle_trace_contract"

fixed = 0
broken_fixed = 0

for scan_dir in SCAN_DIRS:
    if not os.path.isdir(scan_dir):
        continue
    for dirpath, _, filenames in os.walk(scan_dir):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
            except (ValueError, TypeError, RuntimeError) as e:
                continue

            # Check which syms are used but not properly imported
            needs = []
            for sym in SYMS:
                if sym + "(" in content:
                    # Check if properly imported (in an import line, not just mentioned)
                    properly_imported = False
                    for line in content.split("\n"):
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            continue
                        if "import" in line and sym in line and ("from " in line or "import " in line):
                            # Verify it's actually in an import statement
                            if re.search(rf"(?:from\s+\S+\s+import\s+.*{sym}|import\s+.*{sym})", line):
                                properly_imported = True
                                break
                            # Multi-line import: just sym on a line within an import block
                            if stripped == f"{sym}," or stripped == f"{sym},  # noqa: E402":
                                properly_imported = True
                                break
                        if f"def {sym}" in line:
                            properly_imported = True
                            break
                    if not properly_imported:
                        needs.append(sym)

            if not needs:
                continue

            lines = content.split("\n")

            # Strategy: Find the last ')' line that closes a lifecycle_trace_contract import
            # and insert the missing symbols before it
            inserted = False
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line == ")" and i > 0:
                    # Check if this closes a lifecycle_trace_contract import
                    # Walk backwards to find the 'from ... import (' line
                    j = i - 1
                    while j >= 0:
                        if "lifecycle_trace_contract" in lines[j] and "import" in lines[j]:
                            # Found it - insert before the closing ')'
                            indent = "    "
                            insert_lines = [f"{indent}{s},  # noqa: E402" for s in needs]
                            for k, insert_line in enumerate(insert_lines):
                                lines.insert(i + k, insert_line)
                            inserted = True
                            break
                        if lines[j].strip().startswith("from ") and "import" in lines[j]:
                            break  # Different import block
                        if lines[j].strip() == "" and j < i - 1:
                            # Blank line means we left the import block
                            break
                        j -= 1
                    if inserted:
                        break

            if not inserted:
                # No existing import block found - add a new one after last import
                last_import = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last_import = i
                new_block = [
                    f"from {IMPORT_MOD} import (",
                ]
                for sym in needs:
                    new_block.append(f"    {sym},")
                new_block.append(")")
                for k, nb_line in enumerate(new_block):
                    lines.insert(last_import + 1 + k, nb_line)
                inserted = True

            if inserted:
                new_content = "\n".join(lines)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                fixed += 1

            # Also fix broken import insertions from previous batch
            # (where the sym was inserted BEFORE the ')' but with wrong indentation)

print(f"Fixed {fixed} files with missing _emit_* imports")
