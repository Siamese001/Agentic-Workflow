"""Fix ALL files with _emit_* calls that lack the corresponding import.

Two patterns:
A) File HAS a lifecycle_trace_contract import block but is missing specific symbols
B) File has NO lifecycle_trace_contract import block at all

For (A): add missing symbols to the existing block's closing ')'
For (B): add a new import block after the last import statement

Uses EXACT word-boundary matching to avoid substring false positives.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"
LTC = "agentic_core.runtime.lifecycle_trace_contract"

# All known emitter function names from lifecycle_trace_contract
ALL_EMITTERS = set()
# Read them from the actual module
ltc_path = os.path.join(ROOT, "agentic_core", "runtime", "lifecycle_trace_contract.py")
with open(ltc_path, encoding="utf-8") as f:
    for line in f:
        m = re.match(r"^def (_emit_\w+)\(", line.strip())
        if m:
            ALL_EMITTERS.add(m.group(1))
        m2 = re.match(r"^def (emit_\w+)\(", line.strip())
        if m2:
            ALL_EMITTERS.add(m2.group(1))

print(f"Found {len(ALL_EMITTERS)} emitter functions in lifecycle_trace_contract.py")

fixed = 0
total_syms_added = 0

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

            # Find all emitter calls in the file
            used = set()
            for emitter in ALL_EMITTERS:
                if re.search(r"\b" + re.escape(emitter) + r"\s*\(", content):
                    used.add(emitter)

            if not used:
                continue

            # Find which are imported
            imported = set()
            lines = content.split("\n")
            in_block = False
            for line in lines:
                s = line.strip()
                if s.startswith("#"):
                    continue
                if re.match(r"^from\s+\S+\s+import\s+\(", s):
                    in_block = True
                    for e in ALL_EMITTERS:
                        if re.search(r"\b" + re.escape(e) + r"\b", s):
                            imported.add(e)
                    continue
                if in_block:
                    if s == ")":
                        in_block = False
                        continue
                    for e in ALL_EMITTERS:
                        if re.search(r"\b" + re.escape(e) + r"\b", s):
                            imported.add(e)
                    continue
                if re.match(r"^from\s+\S+\s+import\s+", s):
                    for e in ALL_EMITTERS:
                        if re.search(r"\b" + re.escape(e) + r"\b", s):
                            imported.add(e)
                # Check for local definitions too
                for e in ALL_EMITTERS:
                    if f"def {e}" in s:
                        imported.add(e)

            missing = used - imported
            if not missing:
                continue

            # Pattern A: file has LTC import block
            has_ltc = LTC in content

            if has_ltc:
                # Find the LAST LTC import block's closing ')'
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
                    insert = [f"    {e}," for e in sorted(missing)]
                    for k, il in enumerate(insert):
                        lines.insert(best_close + k, il)
                else:
                    # Inline import - skip for now
                    continue
            else:
                # Pattern B: no LTC import at all
                last_import = -1
                in_imp = False
                for i, line in enumerate(lines):
                    s = line.strip()
                    if s.startswith("from ") or s.startswith("import "):
                        if "(" in s and ")" not in s:
                            in_imp = True
                        last_import = i
                    elif in_imp:
                        last_import = i
                        if s == ")":
                            in_imp = False

                if last_import < 0:
                    # No imports at all, insert at top after docstring
                    for i, line in enumerate(lines):
                        s = line.strip()
                        if s.startswith('"""') and i > 0:
                            # Check if single-line or multi-line docstring
                            if s.count('"""') >= 2:
                                last_import = i
                                break
                        elif s.endswith('"""') and i > 0:
                            last_import = i
                            break
                    if last_import < 0:
                        last_import = 0

                block = ["", f"from {LTC} import ("]
                for e in sorted(missing):
                    block.append(f"    {e},")
                block.append(")")

                insert_pos = last_import + 1
                for k, bl in enumerate(block):
                    lines.insert(insert_pos + k, bl)

            new_content = "\n".join(lines)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            total_syms_added += len(missing)
            rel = os.path.relpath(fp, ROOT)
            if fixed <= 20:
                print(f"  Fixed: {rel} (+{len(missing)} imports)")

if fixed > 20:
    print(f"  ... and {fixed - 20} more")
print(f"\nTotal: {fixed} files fixed, {total_syms_added} imports added")
