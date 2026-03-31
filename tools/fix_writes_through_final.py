"""Final pass: fix all files that use _emit_writes_through/_emit_reads_through/_emit_links_incident_trace
/_emit_pulls_context/_emit_validated_by_safety_plane/_emit_execution_terminates_at_uwg/_emit_invokes_eval
/_emit_proposal_commits_routing but don't import them.

This does a thorough check by parsing import blocks properly.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"
LTC = "agentic_core.runtime.lifecycle_trace_contract"

# All potentially missing emitter symbols
ALL_EMITTERS = [
    "_emit_reads_through",
    "_emit_writes_through",
    "_emit_links_incident_trace",
    "_emit_pulls_context",
    "_emit_validated_by_safety_plane",
    "_emit_execution_terminates_at_uwg",
    "_emit_invokes_eval",
    "_emit_proposal_commits_routing",
    "_emit_reads_environ",
    "_emit_reads_runtime_state",
]

fixed = 0

for base_dir in ["agentic_core", "tests", "system_learning"]:
    scan_dir = os.path.join(ROOT, base_dir)
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

            # Find which syms are used but not imported
            needs = []
            for sym in ALL_EMITTERS:
                if sym + "(" not in content:
                    continue
                # Check if it's in an import statement
                imported = False
                lines = content.split("\n")
                in_import = False
                for line in lines:
                    s = line.strip()
                    if s.startswith("#"):
                        continue
                    # Track multi-line imports
                    if re.match(r"from\s+\S+\s+import\s+\(", s):
                        in_import = True
                        if sym in s:
                            imported = True
                            break
                        continue
                    if in_import:
                        if s == ")":
                            in_import = False
                            continue
                        if sym in s:
                            imported = True
                            break
                        continue
                    # Single-line imports
                    if re.match(r"from\s+\S+\s+import\s+", s) and sym in s:
                        imported = True
                        break
                    if f"def {sym}" in s:
                        imported = True
                        break
                if not imported:
                    needs.append(sym)

            if not needs:
                continue

            lines = content.split("\n")

            # Find the LAST lifecycle_trace_contract import block closing ')'
            best_close = -1
            i = 0
            while i < len(lines):
                if LTC in lines[i] and "import" in lines[i]:
                    j = i
                    if "(" in lines[i]:
                        while j < len(lines):
                            if lines[j].strip() == ")":
                                best_close = j
                                break
                            j += 1
                    i = j + 1 if j > i else i + 1
                else:
                    i += 1

            if best_close >= 0:
                insert_lines = [f"    {s},  # noqa: E402" for s in needs]
                for k, il in enumerate(insert_lines):
                    lines.insert(best_close + k, il)
            else:
                # No existing import block - add a new one
                last_import = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last_import = i
                new_block = [f"from {LTC} import ("]
                for s in needs:
                    new_block.append(f"    {s},")
                new_block.append(")")
                for k, nb in enumerate(new_block):
                    lines.insert(last_import + 1 + k, nb)

            new_content = "\n".join(lines)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fpath, ROOT)
            if fixed <= 20:
                print(f"  Fixed: {rel} (added {', '.join(needs)})")

if fixed > 20:
    print(f"  ... and {fixed - 20} more")
print(f"\nTotal: {fixed} files fixed")
