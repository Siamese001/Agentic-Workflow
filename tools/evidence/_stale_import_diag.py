"""One-shot diagnostic: find truly stale ADG imports across the codebase."""

import collections
import pathlib
import re

root = pathlib.Path(r"C:\Git\Agentic-Workflow")

# Step 1: Build inventory of ALL existing ADG modules (dot-separated)
existing = set()
for py in (root / "agentic_core" / "adg").rglob("*.py"):
    if "__pycache__" in str(py):
        continue
    rel = py.relative_to(root).with_suffix("")
    mod = ".".join(rel.parts)
    existing.add(mod)

# Also add package paths (directories with __init__.py)
for d in (root / "agentic_core" / "adg").rglob("__init__.py"):
    rel = d.parent.relative_to(root)
    mod = ".".join(rel.parts)
    existing.add(mod)

print(f"Existing ADG modules: {len(existing)}")

# Step 2: Find ALL imported ADG module paths
imported = collections.Counter()
import_files = collections.defaultdict(set)
skip_parts = {"__pycache__", ".git", "archives", "node_modules", ".healing_backups"}
pattern = re.compile(r"(?:from|import)\s+(agentic_core\.adg(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)")

for py in root.rglob("*.py"):
    if any(s in py.parts for s in skip_parts):
        continue
    try:
        text = py.read_text(encoding="utf-8", errors="replace")
    except (ValueError, TypeError, RuntimeError) as e:
        continue
    for m in pattern.finditer(text):
        mod_path = m.group(1)
        imported[mod_path] += 1
        import_files[mod_path].add(str(py.relative_to(root)))

# Step 3: Find truly stale imports
stale = {}
for imp, count in sorted(imported.items(), key=lambda x: -x[1]):
    if imp in existing:
        continue
    parent = imp.rsplit(".", 1)[0]
    if parent in existing:
        continue
    gparent = parent.rsplit(".", 1)[0] if "." in parent else ""
    if gparent in existing:
        continue
    stale[imp] = count

print(f"\n=== TRULY STALE IMPORTS ({len(stale)} unique) ===")
for mod, count in sorted(stale.items(), key=lambda x: -x[1]):
    print(f"  {count:3d}x  {mod}")
    for f in sorted(import_files[mod])[:2]:
        print(f"         {f}")
    if len(import_files[mod]) > 2:
        print(f"         ... +{len(import_files[mod]) - 2} more")
