"""Render the tech_debt_audit.json into a human-readable summary."""

import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
data = json.loads((REPO / "docs/reports/plans/tech_debt_audit.json").read_text(encoding="utf-8"))


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


# P1
section("P1 — Rename shim files (full list)")
for r in data["p1_rename_shims"]:
    print(f"  {r['file']}  classes={r['classes']}  lines={r['lines']}")

# P2 top by class count
section("P2 — try/except ImportError stub pattern (top by file)")
by_file = Counter(r["file"] for r in data["p2_import_error_stubs"])
for f, n in by_file.most_common(20):
    classes = sorted({r["class"] for r in data["p2_import_error_stubs"] if r["file"] == f})
    print(f"  {n}x  {f}  classes={classes}")
print(f"  ... total: {len(data['p2_import_error_stubs'])} stubs across {len(by_file)} files")

# P3 sample (it has many; need to verify ground-truth)
section("P3 — Dead-import targets (top 25 missing modules)")
modules = Counter(r["module"] for r in data["p3_dead_imports"])
for m, n in modules.most_common(25):
    print(f"  {n}x  from {m} import ...")
print(
    f"  ... total: {len(data['p3_dead_imports'])} dead imports across {len(set(r['file'] for r in data['p3_dead_imports']))} files (NEEDS GROUND-TRUTH SAMPLING)"
)

# P4 duplicate pairs
section("P4 — Duplicate file pairs (identical normalized body)")
for r in data["p4_duplicate_pairs"]:
    print(f"  {r['hash']}: {r['files']}")

# P5 worst synthetic emit files
section("P5 — Synthetic `_emit_*`-heavy files (top 20)")
for r in sorted(data["p5_synthetic_emit_files"], key=lambda x: -x["emit_calls"])[:20]:
    print(
        f"  emits={r['emit_calls']:4d}  ratio={r['ratio']}  total_stmts={r['non_blank_stmts']:4d}  {r['file']}"
    )
print(f"  ... total: {len(data['p5_synthetic_emit_files'])} emit-heavy files")

# P6 zero-body
section("P6 — Zero-body classes/functions at module scope (top files)")
by_file_p6 = Counter(r["file"] for r in data["p6_zero_body_definitions"])
for f, n in by_file_p6.most_common(15):
    items = [r["name"] for r in data["p6_zero_body_definitions"] if r["file"] == f]
    print(f"  {n}x  {f}  {items[:5]}{'...' if len(items) > 5 else ''}")
print(f"  ... total: {len(data['p6_zero_body_definitions'])} zero-body defs in {len(by_file_p6)} files")

# P7 stale __all__
section("P7 — Stale __all__ (top 20)")
for r in data["p7_stale_all"][:20]:
    print(f"  missing={r['missing'][:5]}  in {r['file']}")
print(f"  ... total: {len(data['p7_stale_all'])} files with stale __all__ entries")

# P8 empty init
section("P8 — Empty __init__.py (sample 15)")
for r in data["p8_empty_init"][:15]:
    print(f"  {r['file']}")
print(f"  ... total: {len(data['p8_empty_init'])} empty __init__.py files")

# P9 name collisions, top by # of files
section("P9 — Name collisions (top 25 by file count)")
sorted_p9 = sorted(data["p9_name_collisions"], key=lambda x: -len(x["files"]))[:25]
for r in sorted_p9:
    print(f"  {len(r['files'])}x  {r['name']}: {r['files']}")
print(f"  ... total: {len(data['p9_name_collisions'])} name collisions")

# Summary
section("HEADLINE")
print(f"  P1 rename shims:                  {len(data['p1_rename_shims'])}")
print(f"  P2 import-error stubs:            {len(data['p2_import_error_stubs'])}")
print(f"  P3 dead-import targets:           {len(data['p3_dead_imports'])} (needs validation)")
print(f"  P4 duplicate file pairs:          {len(data['p4_duplicate_pairs'])}")
print(f"  P5 synthetic emit-only files:     {len(data['p5_synthetic_emit_files'])}")
print(f"  P6 zero-body defs:                {len(data['p6_zero_body_definitions'])}")
print(f"  P7 stale __all__:                 {len(data['p7_stale_all'])}")
print(f"  P8 empty __init__.py:             {len(data['p8_empty_init'])}")
print(f"  P9 name collisions:               {len(data['p9_name_collisions'])}")
