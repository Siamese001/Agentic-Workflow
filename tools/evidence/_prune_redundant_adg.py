"""Prune redundant ADG stubs.

A module's ADG stub is redundant when a foundational test (non-_adg) already
covers it via `covers` edges AND the foundational test has >= FOUNDATIONAL_DEPTH_THRESHOLD
assert/raises calls (meaning it has real behavioral depth).

Redundant stubs are DELETED. The `covers` edge is preserved by the foundational test.
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

FOUNDATIONAL_DEPTH_THRESHOLD = 5  # foundational test must have >= this many asserts


def is_prod(p: str) -> bool:
    p2 = p.replace("\\", "/")
    return (
        not p2.startswith("tests/")
        and not p2.startswith("tools/")
        and "ops_scripts" not in p2
        and "__pycache__" not in p2
        and p2.endswith(".py")
    )


def adg_to_dotted(name: str) -> str:
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if name.startswith(pfx):
            name = name[len(pfx):]
    return name.removesuffix(".py")


def count_assertions(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "raises":
                count += 1
    return count


def module_to_adg_stub(module_path: str) -> Path:
    parts = Path(module_path.replace("\\", "/")).parts
    stem = Path(parts[-1]).stem
    return ROOT / "tests" / "unit" / Path(*parts[:-1]) / f"test_{stem}_adg.py"


print("[PRUNE] Scanning ADG...")
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True)
result = scanner.scan()
print(f"[PRUNE] Done: {len(result.modules)} modules, {len(result.edges)} edges")

prod_set = {m for m in result.modules if is_prod(m)}
prod_dotted_to_path: dict[str, str] = {
    m.replace("\\", "/").removesuffix(".py").replace("/", "."): m
    for m in prod_set
}

# Build covers map: prod_path -> {adg_test_dotted_names}, {foundational_test_dotted_names}
covered_by_adg: dict[str, list[str]] = defaultdict(list)
covered_by_foundational: dict[str, list[str]] = defaultdict(list)

for e in result.edges:
    if e.relation_type != "covers":
        continue
    from_d = adg_to_dotted(e.from_name)
    to_d = adg_to_dotted(e.to_name)
    if to_d not in prod_dotted_to_path:
        continue
    prod_path = prod_dotted_to_path[to_d]
    if from_d.split(".")[-1].endswith("_adg"):
        covered_by_adg[prod_path].append(from_d)
    else:
        covered_by_foundational[prod_path].append(from_d)

# Find redundant: both covered, foundational has enough depth
deleted = []
kept = []
not_present = []

both = [p for p in prod_set if covered_by_adg[p] and covered_by_foundational[p]]
print(f"[PRUNE] {len(both)} modules covered by both ADG + foundational")

for prod_path in sorted(both):
    adg_stub = module_to_adg_stub(prod_path)
    if not adg_stub.exists():
        not_present.append(prod_path)
        continue

    # Check foundational depth: resolve dotted names to file paths
    foundational_depth = 0
    for test_dotted in covered_by_foundational[prod_path]:
        # Convert dotted to file path under tests/
        test_rel = test_dotted.replace(".", "/") + ".py"
        test_path = ROOT / test_rel
        # Also try with tests/ prefix stripped
        if not test_path.exists():
            # try directly under ROOT
            for candidate in (ROOT / test_rel,):
                if candidate.exists():
                    test_path = candidate
                    break
        foundational_depth += count_assertions(test_path)

    adg_depth = count_assertions(adg_stub)

    if foundational_depth >= FOUNDATIONAL_DEPTH_THRESHOLD:
        # Redundant: foundational covers it well enough
        adg_stub.unlink()
        deleted.append({
            "module": prod_path,
            "adg_stub": str(adg_stub.relative_to(ROOT)),
            "foundational_depth": foundational_depth,
            "adg_depth": adg_depth,
        })
    else:
        kept.append({
            "module": prod_path,
            "foundational_depth": foundational_depth,
            "adg_depth": adg_depth,
            "reason": "foundational too shallow to be sole coverage",
        })

print(f"\n[PRUNE] Results:")
print(f"  Deleted redundant ADG stubs : {len(deleted)}")
print(f"  Kept (foundational shallow) : {len(kept)}")
print(f"  ADG stub not present        : {len(not_present)}")

print(f"\n[PRUNE] Deleted stubs (top 20 by foundational depth):")
for e in sorted(deleted, key=lambda x: -x["foundational_depth"])[:20]:
    print(f"  found={e['foundational_depth']:>4} asserts  adg={e['adg_depth']:>3}  {e['module']}")

print(f"\n[PRUNE] Kept (foundational too shallow):")
for e in sorted(kept, key=lambda x: -x["adg_depth"])[:20]:
    print(f"  found={e['foundational_depth']:>3} asserts  adg={e['adg_depth']:>3}  {e['module']}")
