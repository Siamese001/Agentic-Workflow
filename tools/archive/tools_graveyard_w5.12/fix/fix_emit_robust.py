"""Robust final-pass fix for all missing emitter imports.

Uses word-boundary matching to avoid false positive substring matches
(e.g., _emit_routes_through matching _emit_writes_through).
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"
LTC = "agentic_core.runtime.lifecycle_trace_contract"

# Emitters that are commonly missing after batch wiring
TARGET_EMITTERS = [
    "_emit_writes_through",
    "_emit_reads_through",
    "_emit_links_incident_trace",
    "_emit_pulls_context",
    "_emit_validated_by_safety_plane",
    "_emit_execution_terminates_at_uwg",
    "_emit_invokes_eval",
    "_emit_proposal_commits_routing",
]

fixed = 0
fixed_files = []

for base_dir in ["agentic_core", "tests", "system_learning", "apps_shared"]:
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

            # Find which target emitters are called but not imported
            missing = []
            for emitter in TARGET_EMITTERS:
                # Check if emitter is CALLED (not just substring-mentioned)
                call_pattern = re.compile(r"\b" + re.escape(emitter) + r"\s*\(")
                if not call_pattern.search(content):
                    continue

                # Check if emitter is IMPORTED (exact word boundary match in import context)
                imported = False
                lines = content.split("\n")
                in_import_block = False

                for line in lines:
                    s = line.strip()
                    if s.startswith("#"):
                        continue

                    # Multi-line import start
                    if re.match(r"^from\s+\S+\s+import\s+\(", s):
                        in_import_block = True
                        # Check this line too
                        if re.search(r"\b" + re.escape(emitter) + r"\b", s):
                            imported = True
                            break
                        continue

                    if in_import_block:
                        if s == ")":
                            in_import_block = False
                            continue
                        if re.search(r"\b" + re.escape(emitter) + r"\b", s):
                            imported = True
                            break
                        continue

                    # Single-line import
                    if re.match(r"^from\s+\S+\s+import\s+", s):
                        if re.search(r"\b" + re.escape(emitter) + r"\b", s):
                            imported = True
                            break

                    # Function definition
                    if f"def {emitter}" in s:
                        imported = True
                        break

                if not imported:
                    missing.append(emitter)

            if not missing:
                continue

            lines = content.split("\n")

            # Find the LAST lifecycle_trace_contract import block's closing ')'
            best_close = -1
            i = 0
            while i < len(lines):
                if LTC in lines[i] and "import" in lines[i] and "(" in lines[i]:
                    j = i + 1
                    while j < len(lines):
                        if lines[j].strip() == ")":
                            best_close = j
                            break
                        j += 1
                    i = j + 1 if j > i else i + 1
                else:
                    i += 1

            if best_close >= 0:
                insert = [f"    {e},  # noqa: E402" for e in sorted(missing)]
                for k, il in enumerate(insert):
                    lines.insert(best_close + k, il)
            else:
                last_import = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last_import = i
                block = [f"from {LTC} import ("]
                for e in sorted(missing):
                    block.append(f"    {e},")
                block.append(")")
                for k, bl in enumerate(block):
                    lines.insert(last_import + 1 + k, bl)

            new_content = "\n".join(lines)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fpath, ROOT)
            fixed_files.append(rel)

for ff in fixed_files[:40]:
    print(f"  Fixed: {ff}")
if len(fixed_files) > 40:
    print(f"  ... and {len(fixed_files) - 40} more")
print(f"\nTotal: {fixed} files fixed")
