"""Check which bare/broad excepts already have guardian comments.

Per constitutional §15 + §8: `except Exception` requires
`# guardian: allow-<type> -- <specific justification>` on the same line or
the line immediately above/below. A generic `# type: ignore` or `# noqa`
does NOT count.

Outputs per-layer counts of:
  - covered: has guardian comment
  - uncovered: needs guardian or migration to specific exception
"""

from __future__ import annotations

import ast
import os
import re
from collections import Counter
from pathlib import Path

ROOTS = (
    "agentic_core",
    "apps_shared",
    "apps_rg",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_underwriting_ai",
    "apps_lic",
    "tools",
    "ops_scripts",
    "system_learning",
    "infrastructure",
)

GUARDIAN_RE = re.compile(r"guardian\s*:\s*allow-\S+", re.IGNORECASE)


def layer_of(path: str) -> str:
    p = path.replace("\\", "/")
    if "agentic_core/L0_" in p:
        return "L0"
    if "agentic_core/L1_" in p:
        return "L1"
    if "agentic_core/L2_" in p:
        return "L2"
    if "agentic_core/L3_" in p:
        return "L3"
    if "agentic_core/L4_" in p:
        return "L4"
    if "agentic_core/L5_" in p:
        return "L5"
    if "agentic_core/L6_" in p:
        return "L6"
    if p.startswith("apps_"):
        return "L_APP"
    if p.startswith("tools/"):
        return "L_TOOLS"
    if p.startswith("ops_scripts/"):
        return "L_OPS"
    if p.startswith("system_learning/"):
        return "L_SL"
    if p.startswith("infrastructure/"):
        return "L_INFRA"
    return "other"


covered: Counter[str] = Counter()
uncovered: Counter[str] = Counter()
uncovered_samples: dict[str, list[str]] = {}

for root in ROOTS:
    if not Path(root).exists():
        continue
    for dirpath, _dirnames, filenames in os.walk(root):
        p_dir = dirpath.replace("\\", "/")
        if "__pycache__" in p_dir or "archives" in p_dir or "_archive" in p_dir:
            continue
        if "/tests/" in p_dir or p_dir.endswith("/tests"):
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dirpath, fn).replace("\\", "/")
            try:
                text = Path(fp).read_text(encoding="utf-8", errors="replace")
                lines = text.splitlines()
                tree = ast.parse(text)
            except (SyntaxError, OSError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                t = node.type
                if t is None:
                    pass  # bare except
                elif isinstance(t, ast.Name) and t.id in ("Exception", "BaseException"):
                    pass
                else:
                    continue
                lay = layer_of(fp)
                ln = node.lineno
                # Check this line ± 1 for guardian comment
                ctx = " ".join(lines[i] for i in range(max(0, ln - 2), min(len(lines), ln + 2)))
                if GUARDIAN_RE.search(ctx):
                    covered[lay] += 1
                else:
                    uncovered[lay] += 1
                    samples = uncovered_samples.setdefault(lay, [])
                    if len(samples) < 3:
                        samples.append(f"{fp}:{ln}")


print("== Covered (has guardian comment) ==")
for lay in sorted(covered):
    print(f"  {covered[lay]:>5}  {lay}")
print(f"  TOTAL covered: {sum(covered.values())}")
print()
print("== Uncovered (needs guardian or migration) ==")
for lay in sorted(uncovered, key=lambda l: -uncovered[l]):
    print(f"  {uncovered[lay]:>5}  {lay}")
print(f"  TOTAL uncovered: {sum(uncovered.values())}")
print()
print("== Sample uncovered sites per layer (first 3) ==")
for lay in sorted(uncovered_samples, key=lambda l: -uncovered[l]):
    print(f"  {lay}:")
    for s in uncovered_samples[lay]:
        print(f"    - {s}")
