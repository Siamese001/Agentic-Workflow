"""One-shot import-health scan for apps_lic. Safe to delete after audit."""
from __future__ import annotations

import importlib
import pathlib
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PKG = "apps_lic"
pkg_root = ROOT / PKG

results = {"ok": [], "failed": []}
for p in sorted(pkg_root.rglob("*.py")):
    if "__pycache__" in p.parts:
        continue
    rel = p.relative_to(ROOT)
    mod = ".".join(rel.with_suffix("").parts)
    if mod.endswith(".__init__"):
        mod = mod[: -len(".__init__")]
    try:
        importlib.import_module(mod)
        results["ok"].append(mod)
    except BaseException as exc:  # guardian: allow-broad -- one-shot scanner, surface all failure types
        results["failed"].append((mod, f"{type(exc).__name__}: {exc}"))

print(f"OK: {len(results['ok'])}  FAILED: {len(results['failed'])}")
print("-" * 80)
for mod, err in results["failed"]:
    print(f"[FAIL] {mod}")
    print(f"       {err}")
