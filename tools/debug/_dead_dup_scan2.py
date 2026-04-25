"""Dead-code scan v2 — correct the symbol-vs-module fan-in confusion.

A module is truly dead only if:
  - entity_type='module'
  - NOT an entry point (hooks/CI scripts/CLI tools run standalone)
  - NOT a test
  - NOT an __init__.py or conftest
  - neither the module node NOR any of its symbol nodes have inbound
    imports / calls / resolves_callsite / instantiates / implements edges
"""

from __future__ import annotations
import sqlite3
from pathlib import Path

DB = Path(r"artifacts/adg/adg_indexed_04232026_0925.sqlite")


ENTRY_POINT_PREFIXES = (
    ".windsurf/scripts/",
    "ops_scripts/ci/",
    "ops_scripts/dev_tools/",
    "ops_scripts/enforcement/",
    "ops_scripts/environment/",
    "tools/debug/",
    "tools/diag/",
    "tools/bench/",
)


def sec(t):
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def main():
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row

    # Build ADG-name prefix for each module so we can match its symbols.
    # A module node resolved_path=foo/bar/baz.py has adg_name=
    #   'ADG::Module::foo/bar/baz.py'
    # Its symbols have adg_name='ADG::Symbol::foo.bar.baz.<name>'.
    # We convert path -> dotted prefix.
    mods = c.execute("""
        SELECT id, resolved_path, adg_name, layer
          FROM nodes
         WHERE entity_type='module'
           AND resolved_path IS NOT NULL
    """).fetchall()
    print(f"total modules: {len(mods)}")

    # For each module, count edges into module_id OR any symbol node
    # whose adg_name starts with ADG::Symbol::<dotted_prefix>.
    # Do this efficiently in SQL using a temp table of prefixes.

    c.executescript("""
        DROP TABLE IF EXISTS _mod_prefix;
        CREATE TEMP TABLE _mod_prefix(
            mod_id INTEGER,
            resolved_path TEXT,
            layer TEXT,
            sym_prefix TEXT
        );
        CREATE INDEX _mod_prefix_sym ON _mod_prefix(sym_prefix);
    """)

    to_insert = []
    for m in mods:
        rp = m["resolved_path"]
        if not rp.endswith(".py"):
            continue
        dotted = rp[:-3].replace("/", ".").replace("\\", ".")
        to_insert.append((m["id"], rp, m["layer"] or "?", f"ADG::Symbol::{dotted}."))
    c.executemany("INSERT INTO _mod_prefix VALUES(?,?,?,?)", to_insert)

    # Now find modules where NEITHER the module node NOR any symbol
    # with matching prefix has inbound "live" edges.
    dead_sql = """
        SELECT mp.mod_id, mp.resolved_path, mp.layer
          FROM _mod_prefix mp
         WHERE NOT EXISTS (
                 SELECT 1 FROM edges e
                  WHERE e.dst_id = mp.mod_id
                    AND e.relation_type IN (
                        'imports','calls','resolves_callsite',
                        'instantiates','implements','exports'))
           AND NOT EXISTS (
                 SELECT 1
                   FROM nodes n
                   JOIN edges e ON e.dst_id = n.id
                  WHERE n.adg_name LIKE mp.sym_prefix || '%'
                    AND e.relation_type IN (
                        'imports','calls','resolves_callsite',
                        'instantiates','implements'))
    """
    dead = c.execute(dead_sql).fetchall()
    print(f"\ntruly unreferenced modules (raw): {len(dead)}")

    # Partition: entry points (kept, executed standalone) vs real dead.
    entry, init_like, tests, real_dead = [], [], [], []
    for row in dead:
        rp = row["resolved_path"]
        if rp.startswith("tests/") or rp.endswith("conftest.py"):
            tests.append(row)
        elif rp.endswith("/__init__.py") or rp.endswith("__init__.py"):
            init_like.append(row)
        elif any(rp.startswith(p) for p in ENTRY_POINT_PREFIXES):
            entry.append(row)
        else:
            real_dead.append(row)

    sec("1. PARTITION SUMMARY")
    print(f"  entry-point scripts (execute standalone, NOT dead): {len(entry)}")
    print(f"  __init__.py files   (tree markers, NOT dead):       {len(init_like)}")
    print(f"  test files          (tracked separately):           {len(tests)}")
    print(f"  REAL DEAD MODULES                                    {len(real_dead)}")

    sec("2. REAL DEAD MODULES (by layer)")
    by_layer = {}
    for r in real_dead:
        by_layer.setdefault(r["layer"], []).append(r["resolved_path"])
    for layer, files in sorted(by_layer.items(), key=lambda x: -len(x[1])):
        print(f"\n  -- {layer}  ({len(files)}) --")
        for f in files[:30]:
            print(f"    {f}")
        if len(files) > 30:
            print(f"    ... +{len(files) - 30} more")

    sec("3. REAL DEAD MODULES — concentration by directory (top 20)")
    from collections import Counter

    dirs = Counter()
    for r in real_dead:
        parts = r["resolved_path"].split("/")
        d = "/".join(parts[:-1]) if len(parts) > 1 else "<root>"
        dirs[d] += 1
    for d, n in dirs.most_common(20):
        print(f"  {n:>4}  {d}/")

    sec("4. ENTRY-POINT 'DEAD' MODULES BY DIRECTORY (for confirmation)")
    from collections import Counter

    e_dirs = Counter()
    for r in entry:
        parts = r["resolved_path"].split("/")
        d = "/".join(parts[:-1]) if len(parts) > 1 else "<root>"
        e_dirs[d] += 1
    for d, n in e_dirs.most_common(10):
        print(f"  {n:>4}  {d}/  (entry points, keep)")

    # Bytes estimate for real dead
    sec("5. REAL DEAD — file-size totals")
    total_bytes = 0
    total_files = 0
    for r in real_dead:
        fp = Path(r["resolved_path"])
        if fp.exists():
            total_bytes += fp.stat().st_size
            total_files += 1
    print(f"  {total_files} files · {total_bytes / 1024:.1f} KB ({total_bytes / 1024 / 1024:.2f} MB)")

    # Estimate ADG shrinkage from removing real dead
    sec("6. ADG SHRINKAGE ESTIMATE FROM REMOVING REAL DEAD")
    # sum symbols + edges originating from real dead modules
    mod_ids = tuple(r["mod_id"] for r in real_dead)
    if mod_ids:
        placeholders = ",".join("?" * len(mod_ids))
        n_edges_out = c.execute(
            f"SELECT COUNT(*) FROM edges WHERE src_id IN ({placeholders})", mod_ids
        ).fetchone()[0]
        n_edges_in = c.execute(
            f"SELECT COUNT(*) FROM edges WHERE dst_id IN ({placeholders})", mod_ids
        ).fetchone()[0]
        # Count symbols owned by these modules
        sym_count = 0
        for r in real_dead[:]:
            pref = f"ADG::Symbol::{r['resolved_path'][:-3].replace('/', '.')}."
            sym_count += c.execute(
                "SELECT COUNT(*) FROM nodes WHERE adg_name LIKE ?", (pref + "%",)
            ).fetchone()[0]
        print(f"  module nodes removed:   {len(real_dead)}")
        print(f"  symbol nodes removed:   ~{sym_count}")
        print(f"  outbound edges removed: ~{n_edges_out}")
        print(f"  inbound edges removed:  ~{n_edges_in} (should be 0)")
        print(f"  TOTAL nodes delta:      ~{len(real_dead) + sym_count}")

    sec("7. __init__.py FILES WITH NO REFS TO SIBLINGS (candidates for slim)")
    # an __init__ is genuinely dead if its symbols AND the dotted module
    # have no inbound — but since __init__'s existence makes the package
    # importable, we separate them.
    # Emit the 227-file list elsewhere; just count here.
    print(f"  candidate count: {len(init_like)}")
    # List a few
    for r in init_like[:15]:
        print(f"    {r['resolved_path']}")


if __name__ == "__main__":
    main()
