"""ADG + AST import-only test audit.

Dual-signal approach:
  1. ADG graph edges — classify by tests_execution_of / covers / calls
  2. AST source inspection — verify import-only status by parsing the actual file

A test file is TRULY import-only only if BOTH signals agree:
  - ADG: no behavioral edges (tests_execution_of, covers, calls, etc.)
  - AST: no assertions beyond `assert X is not None` / `assert callable(X)` / `assert hasattr(X, ...)`

This eliminates the false-positive problem where the ADG misclassifies rich
behavioral tests as import-only due to missing edge linkage.

Output: artifacts/adg/reports/import_only_audit.json
"""

from __future__ import annotations

import ast
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ── AST patterns that mark an import-only test ──
_IMPORT_ONLY_ASSERT_PATTERNS = {
    "is_not_none",  # assert X is not None
    "hasattr",  # assert hasattr(X, "method")
    "callable",  # assert callable(X)
    "isinstance",  # assert isinstance(X, type)
}


def find_latest_adg() -> Path | None:
    candidates = []
    for d in [Path("artifacts/adg"), Path("artifacts/adg_clean"), Path("artifacts")]:
        if d.exists():
            candidates.extend(d.glob("adg_indexed_*.sqlite"))
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def ast_is_import_only(file_path: Path) -> bool:
    """Return True if every test function in the file is import-only.

    A test function is import-only if its body contains ONLY:
      - import statements
      - assert X is not None
      - assert hasattr(X, ...)
      - assert callable(X)
      - assert isinstance(X, ...)
      - pass / docstrings / comments
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return False

    test_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                test_funcs.append(node)

    if not test_funcs:
        return False  # No test functions = not a test file (conftest/__init__)

    for func in test_funcs:
        if not _func_is_import_only(func, source):
            return False  # At least one test has real behavioral assertions

    return True


def _func_is_import_only(func: ast.FunctionDef, source: str) -> bool:
    """Check if a single test function is import-only."""
    for node in ast.walk(func):
        if isinstance(node, ast.Assert):
            if not _is_trivial_assert(node):
                return False
        elif isinstance(node, ast.Call):
            # pytest.raises, mock.patch, etc. = behavioral
            call_src = ast.get_source_segment(source, node) or ""
            if any(kw in call_src for kw in ("pytest.raises", "mock.", "patch", "monkeypatch")):
                return False
        elif isinstance(node, ast.With):
            # with pytest.raises(...) = behavioral
            with_src = ast.get_source_segment(source, node) or ""
            if "pytest.raises" in with_src or "mock" in with_src:
                return False
    return True


def _is_trivial_assert(node: ast.Assert) -> bool:
    """Return True if assert is a trivial import-only check."""
    test = node.test

    # assert X is not None
    if isinstance(test, ast.Compare):
        if len(test.ops) == 1 and isinstance(test.ops[0], ast.IsNot):
            if isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value is None:
                return True
        if len(test.ops) == 1 and isinstance(test.ops[0], ast.Is):
            if isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value is None:
                return True

    # assert hasattr(...) / callable(...) / isinstance(...)
    if isinstance(test, ast.Call) and isinstance(test.func, ast.Name):
        if test.func.id in ("hasattr", "callable", "isinstance"):
            return True

    # assert X (bare truthy check — common in import tests)
    if isinstance(test, ast.Name):
        return True

    return False


def main():
    db_path = find_latest_adg()
    if not db_path:
        print("ERROR: No ADG SQLite found")
        sys.exit(1)

    print(f"ADG: {db_path} ({db_path.stat().st_size / 1024 / 1024:.1f} MB)")
    conn = sqlite3.connect(str(db_path))

    # ═══ Phase 1: ADG graph classification ═══
    print("\n═══ PHASE 1: ADG graph classification ═══")

    test_edge_profile: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rows = conn.execute(
        "SELECT source_file, relation_type, COUNT(*) "
        "FROM edges WHERE source_file LIKE 'tests/%' "
        "GROUP BY source_file, relation_type",
    ).fetchall()
    for source_file, rel_type, cnt in rows:
        test_edge_profile[source_file][rel_type] = cnt

    BEHAVIORAL_EDGES = {
        "tests_execution_of",
        "covers",
        "calls",
        "controls_flow",
        "flows_to",
        "emits_side_effect",
        "resolves_callsite",
    }

    adg_behavioral = set()
    adg_import_only = set()
    for tf, profile in test_edge_profile.items():
        if set(profile.keys()) & BEHAVIORAL_EDGES:
            adg_behavioral.add(tf)
        else:
            adg_import_only.add(tf)

    print(f"ADG behavioral: {len(adg_behavioral)}")
    print(f"ADG import-only candidates: {len(adg_import_only)}")

    # ═══ Phase 2: AST source verification ═══
    print("\n═══ PHASE 2: AST source verification ═══")

    on_disk = set()
    for p in Path("tests").rglob("test_*.py"):
        on_disk.add(str(p).replace("\\", "/"))

    confirmed_import_only = []
    adg_false_positives = []  # ADG said import-only, AST says behavioral
    ast_only_import = []  # Not in ADG but AST says import-only

    # Check ADG import-only candidates with AST
    for tf in sorted(adg_import_only):
        if not tf.startswith("tests/") or not tf.split("/")[-1].startswith("test_"):
            continue  # Skip __init__.py, conftest.py
        fp = Path(tf)
        if not fp.exists():
            continue
        if ast_is_import_only(fp):
            confirmed_import_only.append(tf)
        else:
            adg_false_positives.append(tf)

    # Also scan on-disk files NOT in ADG
    not_in_adg = on_disk - set(test_edge_profile.keys())
    for tf in sorted(not_in_adg):
        fp = Path(tf)
        if fp.exists() and ast_is_import_only(fp):
            ast_only_import.append(tf)

    print(f"Confirmed import-only (ADG + AST agree): {len(confirmed_import_only)}")
    print(f"ADG false positives (ADG=import, AST=behavioral): {len(adg_false_positives)}")
    print(f"AST-only import (not in ADG): {len(ast_only_import)}")

    all_import_only = sorted(set(confirmed_import_only + ast_only_import))

    # ═══ Phase 3: Redundancy check — does module have OTHER behavioral tests? ═══
    print("\n═══ PHASE 3: Redundancy via ADG tests_execution_of ═══")

    module_testers: dict[str, set[str]] = defaultdict(set)
    tex_rows = conn.execute(
        "SELECT source_file, symbol FROM edges "
        "WHERE relation_type='tests_execution_of' AND source_file LIKE 'tests/%'",
    ).fetchall()
    for sf, sym in tex_rows:
        module_testers[sym].add(sf)

    # What does each import-only test import?
    import_targets: dict[str, set[str]] = defaultdict(set)
    imp_rows = conn.execute(
        "SELECT e.source_file, n.resolved_path FROM edges e "
        "JOIN nodes n ON e.dst_id = n.id "
        "WHERE e.relation_type='imports' AND e.source_file LIKE 'tests/%'",
    ).fetchall()
    for sf, rp in imp_rows:
        if rp and not rp.startswith("tests/"):
            import_targets[sf].add(rp)

    redundant = []
    sole_coverage = []
    for tf in all_import_only:
        targets = import_targets.get(tf, set())
        has_other = any((module_testers.get(t, set()) - {tf}) for t in targets)
        if has_other:
            redundant.append(tf)
        else:
            sole_coverage.append(tf)

    # ═══ Phase 4: Classify by line count for reporting ═══
    print("\n═══ PHASE 4: Size classification ═══")
    sizes = {"tiny_le15": [], "small_le50": [], "medium_le200": [], "large_gt200": []}
    for tf in all_import_only:
        fp = Path(tf)
        if fp.exists():
            lines = len(fp.read_text(encoding="utf-8").splitlines())
            if lines <= 15:
                sizes["tiny_le15"].append(tf)
            elif lines <= 50:
                sizes["small_le50"].append(tf)
            elif lines <= 200:
                sizes["medium_le200"].append(tf)
            else:
                sizes["large_gt200"].append(tf)

    for k, v in sizes.items():
        print(f"  {k}: {len(v)}")

    # ═══ Summary ═══
    print("\n" + "=" * 70)
    print("DEFINITIVE IMPORT-ONLY TEST AUDIT")
    print("=" * 70)
    print(f"Total test files on disk:                {len(on_disk)}")
    print(f"ADG behavioral (graph confirms):         {len(adg_behavioral)}")
    print(f"ADG false positives (AST overrides):     {len(adg_false_positives)}")
    print(f"TRUE import-only (ADG + AST confirmed):  {len(all_import_only)}")
    print(f"  ├─ REDUNDANT (safe to delete):         {len(redundant)}")
    print(f"  ├─ SOLE COVERAGE (enhance or keep):    {len(sole_coverage)}")
    print(f"  └─ Tiny (≤15 lines, likely stubs):     {len(sizes['tiny_le15'])}")
    print("=" * 70)

    # Directory breakdown
    print("\nBy directory:")
    dir_counts = Counter()
    for f in all_import_only:
        parts = f.split("/")
        key = "/".join(parts[:4]) if len(parts) >= 4 else "/".join(parts[:3])
        dir_counts[key] += 1
    for d, c in dir_counts.most_common(20):
        print(f"  {c:4d}  {d}")

    # Write results
    output = {
        "adg_path": str(db_path),
        "total_on_disk": len(on_disk),
        "adg_behavioral": len(adg_behavioral),
        "adg_false_positives": sorted(adg_false_positives),
        "true_import_only": all_import_only,
        "redundant_safe_to_delete": sorted(redundant),
        "sole_coverage": sorted(sole_coverage),
        "sizes": {k: sorted(v) for k, v in sizes.items()},
    }
    out_path = Path("artifacts/adg/reports/import_only_audit.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nFull results: {out_path}")
    conn.close()


if __name__ == "__main__":
    main()
