"""Fix broken import insertions where _emit_* was inserted incorrectly.

The batch script may have inserted imports in the wrong position in some files,
causing syntax errors or NameErrors. This script:
1. Finds files where _emit_reads_through/_emit_writes_through/_emit_links_incident_trace
   appear as standalone lines NOT inside an import block
2. Removes those broken lines and ensures proper import at top
"""

import os

ROOT = r"C:\Git\Agentic-Workflow"
SCAN_DIRS = [
    os.path.join(ROOT, "agentic_core"),
    os.path.join(ROOT, "tests"),
    os.path.join(ROOT, "system_learning"),
]

SYMS = ["_emit_reads_through", "_emit_writes_through", "_emit_links_incident_trace"]

fixed = 0

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

            # Quick check: does it use any of the syms?
            uses_any = any(sym + "(" in content for sym in SYMS)
            if not uses_any:
                continue

            # Check for NameError scenario: sym used but import line is broken
            # Specifically look for lines like:
            #   _emit_reads_through,  # noqa: E402
            # that appear OUTSIDE an import block (i.e., not preceded by 'from ... import (')
            lines = content.split("\n")

            # Track which syms are properly imported
            in_import_block = False
            import_block_start = -1
            properly_imported = set()
            broken_lines = []  # (line_index, sym) tuples

            for i, line in enumerate(lines):
                stripped = line.strip()

                # Detect start of import block
                if "from " in line and "import (" in line:
                    in_import_block = True
                    import_block_start = i
                    continue

                # Detect end of import block
                if in_import_block and stripped == ")":
                    in_import_block = False
                    continue

                # Inside import block - check if our syms are here
                if in_import_block:
                    for sym in SYMS:
                        if sym in stripped and not stripped.startswith("#"):
                            properly_imported.add(sym)
                    continue

                # Outside import block - check for orphaned import lines
                for sym in SYMS:
                    if stripped == f"{sym},  # noqa: E402" or stripped == f"{sym},":
                        broken_lines.append((i, sym))

            if not broken_lines:
                continue

            # Remove broken lines
            lines_to_remove = set(idx for idx, _ in broken_lines)
            new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

            # Check which syms still need importing
            still_needs = set()
            for _, sym in broken_lines:
                if sym not in properly_imported:
                    still_needs.add(sym)

            if still_needs:
                # Find last lifecycle_trace_contract import block closing ')'
                found_insert = False
                for i in range(len(new_lines) - 1, -1, -1):
                    if new_lines[i].strip() == ")":
                        # Check if it closes a lifecycle_trace_contract import
                        j = i - 1
                        while j >= 0:
                            if "lifecycle_trace_contract" in new_lines[j] and "import" in new_lines[j]:
                                # Insert before ')'
                                for k, sym in enumerate(sorted(still_needs)):
                                    new_lines.insert(i + k, f"    {sym},  # noqa: E402")
                                found_insert = True
                                break
                            if new_lines[j].strip().startswith("from ") and "import" in new_lines[j]:
                                break
                            if new_lines[j].strip() == "" and j < i - 2:
                                break
                            j -= 1
                        if found_insert:
                            break

            new_content = "\n".join(new_lines)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1

print(f"Fixed {fixed} files with broken import insertions")
