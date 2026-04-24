"""Broader inventory of all violation categories + guardian-related patterns."""
from __future__ import annotations

import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
print(f"snapshot={snap.name}\n")
con = sqlite3.connect(str(snap))
cur = con.cursor()

cur.execute("SELECT category, COUNT(*) FROM violations GROUP BY category ORDER BY 2 DESC")
print("== all categories ==")
for r in cur.fetchall():
    print(f"  {r[1]:>6}  {r[0]}")
print()

cur.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity ORDER BY 2 DESC")
print("== severities ==")
for r in cur.fetchall():
    print(f"  {r[1]:>6}  {r[0]}")
print()

cur.execute(
    "SELECT evidence, COUNT(*) FROM violations "
    "GROUP BY evidence ORDER BY 2 DESC LIMIT 15"
)
print("== top 15 evidence strings ==")
for r in cur.fetchall():
    ev = (r[0] or "")[:100]
    print(f"  {r[1]:>6}  {ev}")
print()

# AST-based fallback: count bare `except Exception:` / `except:` in source tree
# to understand the real population Cascade would encounter in W6.1.
import ast
import os

ROOTS = ("agentic_core", "apps_shared", "apps_rg", "apps_eval", "apps_exec",
         "apps_research", "apps_rfp", "apps_underwriting_ai", "apps_lic",
         "tools", "ops_scripts", "system_learning", "infrastructure")

from collections import Counter
by_layer: Counter[str] = Counter()
by_type: Counter[str] = Counter()
total = 0

def layer_of(path: str) -> str:
    if "agentic_core/L0_" in path: return "L0"
    if "agentic_core/L1_" in path: return "L1"
    if "agentic_core/L2_" in path: return "L2"
    if "agentic_core/L3_" in path: return "L3"
    if "agentic_core/L4_" in path: return "L4"
    if "agentic_core/L5_" in path: return "L5"
    if "agentic_core/L6_" in path: return "L6"
    if path.startswith("apps_"): return "L_APP"
    if path.startswith("tools/"): return "L_TOOLS"
    if path.startswith("ops_scripts/"): return "L_OPS"
    if path.startswith("system_learning/"): return "L_SL"
    if path.startswith("infrastructure/"): return "L_INFRA"
    return "other"

for root in ROOTS:
    if not Path(root).exists():
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath or "archives" in dirpath or "_archive" in dirpath:
            continue
        if "/tests/" in dirpath.replace("\\", "/") or dirpath.endswith("tests"):
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = os.path.join(dirpath, fn).replace("\\", "/")
            try:
                tree = ast.parse(Path(fp).read_text(encoding="utf-8", errors="replace"))
            except (SyntaxError, OSError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                t = node.type
                if t is None:
                    kind = "bare_except"
                elif isinstance(t, ast.Name) and t.id == "Exception":
                    kind = "except_Exception"
                elif isinstance(t, ast.Name) and t.id == "BaseException":
                    kind = "except_BaseException"
                else:
                    continue
                # Check for guardian comment on the line
                total += 1
                by_layer[layer_of(fp)] += 1
                by_type[kind] += 1

print(f"== AST-scanned bare/broad except handlers: total={total} ==")
print()
print("By type:")
for t, n in by_type.most_common():
    print(f"  {n:>5}  {t}")
print()
print("By layer:")
for lay, n in by_layer.most_common():
    print(f"  {n:>5}  {lay}")
