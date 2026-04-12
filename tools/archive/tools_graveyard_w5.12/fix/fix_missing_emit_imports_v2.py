"""Fix all files that call _emit_* functions but have NO lifecycle_trace_contract import at all.

This targets a different pattern than previous scripts: files where the batch
wiring added _emit_* CALLS but never added the import block.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"
LTC = "agentic_core.runtime.lifecycle_trace_contract"

# All known emitter patterns (call sites)
EMIT_CALL_RE = re.compile(r"\b(_emit_\w+)\s*\(")
EMIT_NOPREFIX_RE = re.compile(r"\b(emit_determinism_digest|emit_replay_key)\s*\(")

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

            # Skip files that already have an LTC import
            if LTC in content:
                continue

            # Find all _emit_* calls
            emit_calls = set(EMIT_CALL_RE.findall(content))
            emit_calls |= set(EMIT_NOPREFIX_RE.findall(content))

            if not emit_calls:
                continue

            # Check which are NOT defined/imported in the file
            missing = set()
            for sym in emit_calls:
                # Skip if defined in this file
                if f"def {sym}" in content:
                    continue
                missing.add(sym)

            if not missing:
                continue

            # Find the last import line to insert after
            lines = content.split("\n")
            last_import = -1
            in_import = False
            for i, line in enumerate(lines):
                s = line.strip()
                if s.startswith("from ") or s.startswith("import "):
                    if "(" in s and ")" not in s:
                        in_import = True
                    last_import = i
                elif in_import:
                    last_import = i
                    if s == ")":
                        in_import = False

            if last_import < 0:
                # No imports at all - find end of docstring
                for i, line in enumerate(lines):
                    s = line.strip()
                    if s and not s.startswith("#") and not s.startswith('"""') and not s.startswith("'"):
                        last_import = max(0, i - 1)
                        break

            # Build import block
            import_block = [f"from {LTC} import ("]
            for sym in sorted(missing):
                import_block.append(f"    {sym},")
            import_block.append(")")

            # Insert after last import
            insert_pos = last_import + 1
            for k, il in enumerate(import_block):
                lines.insert(insert_pos + k, il)

            new_content = "\n".join(lines)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fp, ROOT)
            if fixed <= 30:
                print(f"  Fixed: {rel} ({len(missing)} symbols)")

if fixed > 30:
    print(f"  ... and {fixed - 30} more")
print(f"\nTotal: {fixed} files fixed")
