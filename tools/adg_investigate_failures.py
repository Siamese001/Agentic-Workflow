#!/usr/bin/env python3
"""Investigate root causes of each validation failure."""

import sqlite3
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "artifacts" / "adg" / "adg_indexed_03242026_1825.sqlite"


def main():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # ═══════════════════════════════════════════════════════════════
    # ROOT CAUSE 1: Semantic accuracy — import line_no mismatches
    # ═══════════════════════════════════════════════════════════════
    print("=" * 70)
    print("ROOT CAUSE 1: IMPORT EDGE LINE_NO ANALYSIS")
    print("=" * 70)

    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type='imports' AND line_no=0")
    imports_line0 = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type='imports' AND line_no>0")
    imports_linepos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type='imports'")
    imports_total = c.fetchone()[0]

    print(f"  imports with line_no=0: {imports_line0}")
    print(f"  imports with line_no>0: {imports_linepos}")
    print(f"  total imports: {imports_total}")

    # Check 10 random import edges against actual files
    c.execute("""
        SELECT id, source_file, line_no, symbol
        FROM edges
        WHERE relation_type='imports' AND line_no > 0
        ORDER BY RANDOM() LIMIT 20
    """)
    print("\n  Spot-checking 20 random import edges:")
    match_count = 0
    mismatch_count = 0
    for eid, sf, ln, sym in c.fetchall():
        full = PROJECT_ROOT / sf
        if not full.exists():
            print(f"    edge {eid}: FILE MISSING {sf}")
            continue
        try:
            lines = full.read_text(encoding="utf-8", errors="replace").split("\n")
            if ln <= len(lines):
                line = lines[ln - 1]
                sym_short = sym.split(".")[-1] if sym else ""
                has_import = "import" in line or sym_short in line
                status = "MATCH" if has_import else "MISMATCH"
                if has_import:
                    match_count += 1
                else:
                    mismatch_count += 1
                    # Check nearby lines for the actual import
                    nearby = ""
                    for offset in range(-5, 6):
                        check_ln = ln - 1 + offset
                        if 0 <= check_ln < len(lines) and "import" in lines[check_ln]:
                            nearby = f" (found import at line {check_ln+1})"
                            break
                    print(f"    edge {eid}: {status} {sf}:{ln} sym={sym_short}")
                    print(f"      line: '{line.strip()[:80]}'{nearby}")
        except Exception as e:
            print(f"    edge {eid}: ERROR {e}")

    print(f"\n  Spot-check result: {match_count} match, {mismatch_count} mismatch out of 20")

    # ═══════════════════════════════════════════════════════════════
    # ROOT CAUSE 2: File ratio — which files are missing?
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ROOT CAUSE 2: FILE COVERAGE GAP ANALYSIS")
    print("=" * 70)

    # Get all ADG source files
    c.execute("SELECT DISTINCT source_file FROM edges WHERE source_file != ''")
    adg_files = set(r[0] for r in c.fetchall())

    c.execute("SELECT DISTINCT resolved_path FROM nodes WHERE entity_type='module' AND resolved_path != ''")
    adg_module_paths = set(r[0] for r in c.fetchall())

    adg_all = adg_files | adg_module_paths

    # Get all AST files
    skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env"}
    ast_files = set()
    for py_file in PROJECT_ROOT.rglob("*.py"):
        rel = py_file.relative_to(PROJECT_ROOT)
        if any(part in skip_dirs for part in rel.parts):
            continue
        ast_files.add(str(rel).replace("\\", "/"))

    missing = ast_files - adg_all
    extra = adg_all - ast_files

    print(f"  AST files: {len(ast_files)}")
    print(f"  ADG files (edges+nodes): {len(adg_all)}")
    print(f"  Missing from ADG: {len(missing)}")
    print(f"  Extra in ADG (not on disk): {len(extra)}")

    # Categorize missing files by directory
    missing_dirs = Counter()
    for f in missing:
        parts = f.split("/")
        top = parts[0] if parts else "?"
        missing_dirs[top] += 1

    print("\n  Missing files by top directory:")
    for d, cnt in missing_dirs.most_common(15):
        print(f"    {d}: {cnt}")

    # ═══════════════════════════════════════════════════════════════
    # ROOT CAUSE 3: Function ratio — ADG design limitation
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ROOT CAUSE 3: FUNCTION NODE GRANULARITY")
    print("=" * 70)

    c.execute("SELECT identity_kind, COUNT(*) FROM nodes GROUP BY identity_kind ORDER BY COUNT(*) DESC")
    print("  Node identity_kind distribution:")
    for kind, cnt in c.fetchall():
        print(f"    {kind}: {cnt}")

    # Check how functions are represented
    c.execute("""
        SELECT COUNT(*) FROM nodes
        WHERE adg_name LIKE '%::%'
          AND entity_type = 'symbol'
    """)
    symbol_with_scope = c.fetchone()[0]
    print(f"\n  Symbol nodes with '::' (scoped): {symbol_with_scope}")

    c.execute("""
        SELECT adg_name FROM nodes
        WHERE entity_type = 'symbol'
        LIMIT 10
    """)
    print("\n  Sample symbol node names:")
    for (name,) in c.fetchall():
        print(f"    {name}")

    # ═══════════════════════════════════════════════════════════════
    # ROOT CAUSE 4: Low-confidence edges
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ROOT CAUSE 4: LOW-CONFIDENCE EDGES (confidence < 0.5)")
    print("=" * 70)

    c.execute("""
        SELECT relation_type, COUNT(*), AVG(confidence_score)
        FROM edges
        WHERE confidence_score < 0.5
        GROUP BY relation_type
        ORDER BY COUNT(*) DESC
    """)
    print("  Low-confidence edges by type:")
    for rel, cnt, avg_conf in c.fetchall():
        print(f"    {rel}: {cnt} (avg conf={avg_conf:.2f})")

    # ═══════════════════════════════════════════════════════════════
    # ROOT CAUSE 5: Duplicate edges
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ROOT CAUSE 5: DUPLICATE EDGES")
    print("=" * 70)

    c.execute("""
        SELECT relation_type, COUNT(*) as dup_count
        FROM (
            SELECT src_id, dst_id, relation_type, line_no, COUNT(*) as cnt
            FROM edges
            GROUP BY src_id, dst_id, relation_type, line_no
            HAVING cnt > 1
        )
        GROUP BY relation_type
        ORDER BY dup_count DESC
        LIMIT 10
    """)
    print("  Duplicate edge groups by type:")
    for rel, cnt in c.fetchall():
        print(f"    {rel}: {cnt} duplicate groups")

    # ═══════════════════════════════════════════════════════════════
    # ROOT CAUSE 6: Signal ratio — reclassify debatable types
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("ROOT CAUSE 6: SIGNAL RATIO EDGE CLASSIFICATION")
    print("=" * 70)

    c.execute("""
        SELECT relation_type, COUNT(*) as cnt
        FROM edges
        GROUP BY relation_type
        ORDER BY cnt DESC
    """)
    all_types = c.fetchall()
    total = sum(cnt for _, cnt in all_types)

    print(f"  Total edges: {total}")
    print("\n  Full edge type distribution:")
    for rel, cnt in all_types:
        pct = cnt / total * 100
        print(f"    {rel:45} {cnt:>8} ({pct:5.2f}%)")

    conn.close()


if __name__ == "__main__":
    main()
