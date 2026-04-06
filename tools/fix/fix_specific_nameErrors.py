"""Find and fix specific files still missing _emit_writes_through/_emit_reads_through/_emit_links_incident_trace."""

import os

ROOT = r"C:\Git\Agentic-Workflow"
SYMS = ["_emit_reads_through", "_emit_writes_through", "_emit_links_incident_trace"]

fixed = 0

for dirpath, _, filenames in os.walk(os.path.join(ROOT, "agentic_core")):
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        fpath = os.path.join(dirpath, fn)
        try:
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
        except (ValueError, TypeError, RuntimeError) as e:
            continue

        needs = []
        for sym in SYMS:
            if sym + "(" in content:
                # Check all import-related lines
                found = False
                in_import = False
                for line in content.split("\n"):
                    s = line.strip()
                    if s.startswith("#"):
                        continue
                    if "from " in line and "import" in line and "(" in line:
                        in_import = True
                    if in_import:
                        if sym in s and not s.startswith("#"):
                            found = True
                            break
                        if s == ")":
                            in_import = False
                    elif "import" in line and sym in line:
                        found = True
                        break
                    if f"def {sym}" in line:
                        found = True
                        break
                if not found:
                    needs.append(sym)

        if not needs:
            continue

        lines = content.split("\n")

        # Find the best insertion point - last lifecycle_trace_contract import block
        best_close = -1
        i = 0
        while i < len(lines):
            if "lifecycle_trace_contract" in lines[i] and "import" in lines[i]:
                # Find closing ')'
                j = i
                while j < len(lines):
                    if lines[j].strip() == ")":
                        best_close = j
                        break
                    j += 1
                i = j + 1 if j < len(lines) else i + 1
            else:
                i += 1

        if best_close >= 0:
            insert_lines = [f"    {s},  # noqa: E402" for s in needs]
            for k, il in enumerate(insert_lines):
                lines.insert(best_close + k, il)
        else:
            # No lifecycle import block - add standalone
            last_import = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    last_import = i
            new_block = ["from agentic_core.runtime.contracts.lifecycle_trace_contract import ("]
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
        print(f"  Fixed: {rel} (added {', '.join(needs)})")

print(f"\nFixed {fixed} files")
