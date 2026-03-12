"""Audit overlap between ADG-derived (_adg.py) and foundational (non-_adg) tests.

Outputs:
  - Overlap count (module covered by both ADG stub AND foundational test)
  - Redundancy classification (ADG stub is superfluous when foundational has depth)
  - fan_in distribution with threshold analysis
  - High-fan_in modules that have only an ADG stub (need foundational)
"""
from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


# ── Helpers ───────────────────────────────────────────────────────────────────

def layer_from_path(path: str) -> str:
    p = path.replace("\\", "/")
    for prefix, label in [
        ("agentic_core/L0", "L0"), ("agentic_core/L1", "L1"),
        ("agentic_core/L2", "L2"), ("agentic_core/L3", "L3"),
        ("agentic_core/L4", "L4"), ("agentic_core/L5", "L5"),
        ("agentic_core/L6", "L6"), ("apps_rg", "L_APP_RG"),
        ("apps_shared", "L_SHARED"), ("system_learning", "L_SL"),
        ("agentic_core/runtime", "L_RUNTIME"),
        ("agentic_core/enforcement", "L_ENF"),
        ("agentic_core/utils", "L_UTILS"),
        ("agentic_core/adg", "L_ADG"),
    ]:
        if p.startswith(prefix):
            return label
    return "OTHER"


def is_production(path: str) -> bool:
    p = path.replace("\\", "/")
    return (
        not p.startswith("tests/")
        and not p.startswith("tools/")
        and not "ops_scripts" in p
        and not "__pycache__" in p
        and p.endswith(".py")
    )


def module_to_test_paths(module_path: str):
    parts = Path(module_path.replace("\\", "/")).parts
    stem = Path(parts[-1]).stem
    test_dir = ROOT / "tests" / "unit" / Path(*parts[:-1])
    adg_path = test_dir / f"test_{stem}_adg.py"
    return adg_path, test_dir, stem


def count_assertions(test_path: Path) -> int:
    """Count assert + pytest.raises as proxy for test depth."""
    if not test_path.exists():
        return 0
    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "raises":
                count += 1
    return count


# ── Scan ──────────────────────────────────────────────────────────────────────

print("[AUDIT] Scanning ADG (this takes ~30s)...")
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True)
result = scanner.scan()
print(f"[AUDIT] Scan done: {len(result.modules)} modules, {len(result.edges)} edges")

# Build fan_in: count inbound `imports` edges per production module
# Edge.to_name is an ADG canonical name like "agentic_core.L0_routing.foo"
# Edge.from_name matches the module adg_name (dotted, no .py)
# result.modules are file-relative paths like "agentic_core/L0_routing/foo.py"

def adg_name_to_path(name: str) -> str:
    """agentic_core.L0_routing.foo -> agentic_core/L0_routing/foo.py (best-effort)."""
    # Strip ADG::Symbol:: or ADG::Module:: prefixes if present
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if name.startswith(pfx):
            name = name[len(pfx):]
    # If already a path-like string
    if name.endswith(".py"):
        return name
    return name.replace(".", "/") + ".py"

# Build set of production module paths
prod_paths = {m for m in result.modules if is_production(m)}

# Normalise path → dotted for lookup
def path_to_dotted(p: str) -> str:
    return p.replace("\\", "/").removesuffix(".py").replace("/", ".")

prod_dotted = {path_to_dotted(p): p for p in prod_paths}

# Count inbound imports edges (fan_in)
fan_in: dict[str, int] = defaultdict(int)
for edge in result.edges:
    if edge.relation_type != "imports":
        continue
    to_raw = edge.to_name
    # to_name can be dotted module like "agentic_core.L0_routing.foo"
    # or "ADG::Symbol::agentic_core.L0_routing.foo"
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if to_raw.startswith(pfx):
            to_raw = to_raw[len(pfx):]
    # Find matching production module
    if to_raw in prod_dotted:
        fan_in[prod_dotted[to_raw]] += 1
    else:
        # try stripping last component (symbol import → module)
        parts = to_raw.rsplit(".", 1)
        if parts[0] in prod_dotted:
            fan_in[prod_dotted[parts[0]]] += 1

print(f"[AUDIT] fan_in computed for {len(fan_in)} modules")

# ── Per-module classification ─────────────────────────────────────────────────
overlap_both: list[dict] = []
adg_only: list[dict] = []
foundational_only: list[dict] = []
neither: list[dict] = []

for mod_path in sorted(prod_paths):
    fi = fan_in.get(mod_path, 0)
    layer = layer_from_path(mod_path)
    adg_path, test_dir, stem = module_to_test_paths(mod_path)

    has_adg = adg_path.exists()

    foundational_files = []
    if test_dir.exists():
        for f in test_dir.iterdir():
            if (f.name.startswith(f"test_{stem}")
                    and f.suffix == ".py"
                    and not f.name.endswith("_adg.py")):
                foundational_files.append(f)

    has_foundational = bool(foundational_files)
    adg_asserts = count_assertions(adg_path) if has_adg else 0
    found_asserts = sum(count_assertions(f) for f in foundational_files)

    entry = {
        "module": mod_path,
        "layer": layer,
        "fan_in": fi,
        "adg_asserts": adg_asserts,
        "foundational_asserts": found_asserts,
        "foundational_files": [str(f.relative_to(ROOT)) for f in foundational_files],
    }

    if has_adg and has_foundational:
        overlap_both.append(entry)
    elif has_adg and not has_foundational:
        adg_only.append(entry)
    elif not has_adg and has_foundational:
        foundational_only.append(entry)
    else:
        neither.append(entry)

# ── Print results ─────────────────────────────────────────────────────────────

print(f"\n=== OVERLAP AUDIT RESULTS ===")
print(f"  Total production modules   : {len(prod_paths)}")
print(f"  ADG + Foundational (BOTH)  : {len(overlap_both)}")
print(f"  ADG only                   : {len(adg_only)}")
print(f"  Foundational only          : {len(foundational_only)}")
print(f"  Neither                    : {len(neither)}")

# Redundant = both exist but foundational already deep, ADG adds nothing
redundant = [
    e for e in overlap_both
    if e["foundational_asserts"] >= 5
]
print(f"\n  Redundant ADG stubs (foundational has >=5 asserts): {len(redundant)}")

# True overlap = both have meaningful depth
both_deep = [
    e for e in overlap_both
    if e["adg_asserts"] >= 5 and e["foundational_asserts"] >= 5
]
print(f"  True deep overlap (both >=5 asserts): {len(both_deep)}")

# ADG-only with meaningful depth (ADG doing real work, no foundational)
adg_only_deep = [e for e in adg_only if e["adg_asserts"] >= 5]
print(f"  ADG-only with >=5 asserts (ADG is primary): {len(adg_only_deep)}")

print(f"\n=== TOP 20 REDUNDANT ADG STUBS (safe to remove) ===")
for e in sorted(redundant, key=lambda x: -x["foundational_asserts"])[:20]:
    print(f"  fan_in={e['fan_in']:>3}  adg={e['adg_asserts']:>3} asserts  "
          f"found={e['foundational_asserts']:>4} asserts  {e['module']}")

print(f"\n=== FAN_IN DISTRIBUTION ===")
all_fi = list(fan_in.values()) + [0] * (len(prod_paths) - len(fan_in))
buckets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, "6-10": 0, "11-20": 0, "21+": 0}
for fi_val in all_fi:
    if fi_val == 0: buckets[0] += 1
    elif fi_val == 1: buckets[1] += 1
    elif fi_val == 2: buckets[2] += 1
    elif fi_val == 3: buckets[3] += 1
    elif fi_val == 4: buckets[4] += 1
    elif fi_val == 5: buckets[5] += 1
    elif fi_val <= 10: buckets["6-10"] += 1
    elif fi_val <= 20: buckets["11-20"] += 1
    else: buckets["21+"] += 1
total = len(all_fi)
for k, v in buckets.items():
    print(f"  fan_in={k:>5}: {v:>4} modules  ({100*v/total:4.1f}%)")

print(f"\n=== THRESHOLD ANALYSIS (impact of requiring foundational test) ===")
print(f"  {'threshold':>10}  {'modules':>8}  {'%total':>7}  {'have_found':>11}  {'gap':>6}")
for threshold in [1, 2, 3, 5, 10]:
    above = [m for m in prod_paths if fan_in.get(m, 0) >= threshold]
    have_f = [e for e in (overlap_both + foundational_only) if e["fan_in"] >= threshold]
    gap = len(above) - len(have_f)
    print(f"  {threshold:>10}  {len(above):>8}  {100*len(above)/total:>6.1f}%  "
          f"{len(have_f):>11}  {gap:>6}")

print(f"\n=== HIGH FAN_IN, ADG-ONLY (top 30 — need foundational tests) ===")
needs_foundational = sorted(
    [e for e in adg_only if e["fan_in"] >= 3],
    key=lambda x: (-x["fan_in"], x["module"])
)
print(f"  Total fan_in>=3, adg-only: {len(needs_foundational)}")
for e in needs_foundational[:30]:
    print(f"  fan_in={e['fan_in']:>3}  {e['module']}")

# ── Save JSON ─────────────────────────────────────────────────────────────────
out = {
    "summary": {
        "total_production": len(prod_paths),
        "overlap_both": len(overlap_both),
        "adg_only": len(adg_only),
        "foundational_only": len(foundational_only),
        "neither": len(neither),
        "redundant_adg_stubs": len(redundant),
        "both_deep": len(both_deep),
    },
    "redundant_adg_stubs": sorted(redundant, key=lambda x: -x["foundational_asserts"]),
    "needs_foundational_fan_in_ge3": needs_foundational,
    "fan_in_buckets": {str(k): v for k, v in buckets.items()},
}
out_path = ROOT / "tools" / "evidence" / "overlap_audit.json"
out_path.write_text(json.dumps(out, indent=2))
print(f"\n[AUDIT] Saved → {out_path.relative_to(ROOT)}")
