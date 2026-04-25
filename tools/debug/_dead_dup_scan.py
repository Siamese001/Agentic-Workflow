"""Dead-code + duplication scan for ADG shrinkage.

Goal: find nodes/edges that can be removed with low risk to reduce
ADG size without changing behavior.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path

DB = Path(r"artifacts/adg/adg_indexed_04232026_0925.sqlite")


def sec(t):
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def rows(c, sql, params=()):
    return c.execute(sql, params).fetchall()


def main():
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    # 0. Baseline
    sec("0. BASELINE NODE/EDGE COUNTS")
    print("  nodes:", rows(c, "SELECT COUNT(*) FROM nodes")[0][0])
    print("  edges:", rows(c, "SELECT COUNT(*) FROM edges")[0][0])
    print("  node count by entity_type:")
    for r in rows(c, "SELECT entity_type,COUNT(*) FROM nodes GROUP BY entity_type ORDER BY 2 DESC"):
        print(f"    {r[1]:>7}  {r[0]}")

    # 1. unused_import edges (ruff F401 territory)
    sec("1. UNUSED IMPORTS (relation_type=unused_import)")
    tot = rows(c, "SELECT COUNT(*) FROM edges WHERE relation_type='unused_import'")[0][0]
    print(f"  total unused_import edges: {tot}")
    print("\n  top 20 files by unused-import count:")
    for f, n in rows(
        c,
        """
        SELECT source_file, COUNT(*) c FROM edges
         WHERE relation_type='unused_import'
         GROUP BY source_file ORDER BY c DESC LIMIT 20
    """,
    ):
        print(f"    {n:>4}  {f}")

    # 2. Zero-caller symbols (dead symbols inside live modules)
    sec("2. ZERO-CALLER NON-PRIVATE SYMBOLS (potentially dead)")
    q = """
        SELECT n.adg_name, n.entity_type,
               (SELECT resolved_path FROM nodes p
                 WHERE p.adg_name = substr(n.adg_name,1,
                       length(n.adg_name)-length(
                         substr(n.adg_name,instr(n.adg_name,'::')+2)))
                 LIMIT 1) AS module_path
          FROM nodes n
         WHERE n.entity_type IN ('function','class','method')
           AND n.adg_name NOT LIKE '%._%'
           AND n.adg_name NOT LIKE '%.__%'
           AND NOT EXISTS (
                SELECT 1 FROM edges e
                 WHERE e.dst_id = n.id
                   AND e.relation_type IN (
                        'imports','calls','resolves_callsite',
                        'instantiates','implements'))
         LIMIT 25
    """
    try:
        for r in rows(c, q):
            print(" ", r)
    except sqlite3.Error as exc:
        print(" err:", exc)

    # simpler: count by file
    sec("2b. FILES BY ZERO-CALLER SYMBOL COUNT (top 25)")
    q2 = """
        WITH no_caller AS (
          SELECT n.id, n.adg_name
            FROM nodes n
           WHERE n.entity_type IN ('function','class','method')
             AND NOT EXISTS (
                   SELECT 1 FROM edges e
                    WHERE e.dst_id = n.id
                      AND e.relation_type IN (
                          'imports','calls','resolves_callsite',
                          'instantiates','implements')
             )
        )
        SELECT SUBSTR(adg_name, 14,
                 INSTR(SUBSTR(adg_name,14), '.') - 1) AS mod_prefix,
               COUNT(*) AS n
          FROM no_caller
         WHERE adg_name LIKE 'ADG::Symbol::%'
         GROUP BY mod_prefix
         ORDER BY n DESC LIMIT 25
    """
    try:
        for r in rows(c, q2):
            print(f"    {r[1]:>5}  {r[0]}")
    except sqlite3.Error as exc:
        print(" err:", exc)

    # 3. Zero-caller MODULES (by file)
    sec("3. ZERO-CALLER MODULES (module-level no inbound imports)")
    q3 = """
        SELECT n.resolved_path, n.layer
          FROM nodes n
         WHERE n.entity_type='module'
           AND n.resolved_path IS NOT NULL
           AND n.resolved_path NOT LIKE 'tests/%'
           AND n.resolved_path NOT LIKE '%/__init__.py'
           AND n.resolved_path NOT LIKE '%conftest.py'
           AND NOT EXISTS (
                SELECT 1 FROM edges e
                 WHERE e.dst_id = n.id
                   AND e.relation_type = 'imports')
         ORDER BY n.resolved_path
    """
    r3 = rows(c, q3)
    print(f"  count: {len(r3)}")
    print("\n  first 40 by path:")
    for fp, layer in r3[:40]:
        print(f"    [{layer or '?':>10}]  {fp}")

    # 4. Modules with 0 inbound imports AND 0 edges defined (true orphans)
    sec("4. TRUE ORPHAN MODULES (no inbound, no outbound imports)")
    q4 = """
        SELECT n.resolved_path, n.layer
          FROM nodes n
         WHERE n.entity_type='module'
           AND n.resolved_path IS NOT NULL
           AND n.resolved_path NOT LIKE 'tests/%'
           AND NOT EXISTS (
                SELECT 1 FROM edges e
                 WHERE e.dst_id = n.id AND e.relation_type='imports')
           AND NOT EXISTS (
                SELECT 1 FROM edges e
                 WHERE e.src_id = n.id AND e.relation_type='imports')
         ORDER BY n.resolved_path LIMIT 60
    """
    for r in rows(c, q4):
        print(f"    [{r[1] or '?':>10}]  {r[0]}")
    total_true_orphans = rows(c, q4.replace("ORDER BY n.resolved_path LIMIT 60", ""))
    print(f"  total: {len(total_true_orphans)}")

    # 5. Duplicated adapters (pre-classified by ADG)
    sec("5. v_p2_duplicated_adapters (full content)")
    for r in rows(c, "SELECT * FROM v_p2_duplicated_adapters"):
        print(" ", r)

    # 6. Isolated experimental
    sec("6. v_p3_isolated_experimental (full content)")
    for r in rows(c, "SELECT * FROM v_p3_isolated_experimental"):
        print(" ", r)

    # 7. Unknown taxonomy / orphans MV
    sec("7. mv_unknown_taxonomy_and_orphans (top 30)")
    cols = [r[1] for r in rows(c, "PRAGMA table_info(mv_unknown_taxonomy_and_orphans)")]
    print("  cols:", cols)
    for r in rows(c, "SELECT * FROM mv_unknown_taxonomy_and_orphans LIMIT 30"):
        print(" ", r)

    # 8. Agent tool ratio / agent specialization overlap
    sec("8. mv_agent_specialization_overlap (candidates to collapse)")
    cols = [r[1] for r in rows(c, "PRAGMA table_info(mv_agent_specialization_overlap)")]
    print("  cols:", cols)
    n = rows(c, "SELECT COUNT(*) FROM mv_agent_specialization_overlap")[0][0]
    print(f"  rows: {n}")
    for r in rows(c, "SELECT * FROM mv_agent_specialization_overlap LIMIT 20"):
        print(" ", r)

    # 9. archives/ imports — should be zero per constitutional §12
    sec("9. IMPORTS FROM archives/ (constitutional §12 check)")
    q9 = """
        SELECT e.source_file, e.symbol, COUNT(*)
          FROM edges e
          JOIN nodes n ON n.id=e.dst_id
         WHERE e.relation_type='imports'
           AND (n.resolved_path LIKE 'archives/%'
                OR e.symbol LIKE 'archives.%')
         GROUP BY e.source_file, e.symbol
         ORDER BY 3 DESC LIMIT 30
    """
    for r in rows(c, q9):
        print(" ", r)

    # 10. Files with ONLY violations-type edges and no real use
    sec("10. POTENTIAL SHRINKAGE ESTIMATE")
    unused = rows(c, "SELECT COUNT(*) FROM edges WHERE relation_type='unused_import'")[0][0]
    zero_mods = len(r3)
    print(f"  delete unused_imports     -> ~{unused:>6} edges gone")
    print(f"  remove {zero_mods} zero-caller modules -> ~{zero_mods * 20:>6} edges gone (est 20/file)")
    print("  collapse duplicated adapters ->   ~few hundred edges")


if __name__ == "__main__":
    main()
