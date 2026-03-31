"""Find all files that call _emit_writes_through/_emit_pulls_context/_emit_validated_by_safety_plane
but don't import them. Uses word-boundary regex to avoid substring false positives."""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"

TARGETS = ["_emit_writes_through", "_emit_pulls_context", "_emit_validated_by_safety_plane",
           "_emit_execution_terminates_at_uwg", "_emit_invokes_eval", "_emit_proposal_commits_routing"]

results = []

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

            for sym in TARGETS:
                # Check if symbol is called
                if not re.search(r'\b' + re.escape(sym) + r'\s*\(', content):
                    continue
                # Check if symbol is imported (word boundary match in import context)
                imported = False
                in_block = False
                for line in content.split("\n"):
                    s = line.strip()
                    if s.startswith("#"):
                        continue
                    if re.match(r'^from\s+\S+\s+import\s+\(', s):
                        in_block = True
                        if re.search(r'\b' + re.escape(sym) + r'\b', s):
                            imported = True
                            break
                        continue
                    if in_block:
                        if s == ")":
                            in_block = False
                            continue
                        if re.search(r'\b' + re.escape(sym) + r'\b', s):
                            imported = True
                            break
                        continue
                    if re.match(r'^from\s+\S+\s+import\s+', s) and re.search(r'\b' + re.escape(sym) + r'\b', s):
                        imported = True
                        break
                    if f"def {sym}" in s:
                        imported = True
                        break
                if not imported:
                    rel = os.path.relpath(fp, ROOT)
                    results.append((rel, sym))

print(f"Found {len(results)} missing imports:")
for rel, sym in results[:50]:
    print(f"  {rel}: {sym}")
if len(results) > 50:
    print(f"  ... and {len(results) - 50} more")
