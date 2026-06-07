"""Mixin / MRO consolidation audit driven by the ADG snapshot."""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import ast
import glob
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SNAP = sorted(glob.glob(str(REPO / "artifacts" / "adg" / "adg_indexed_*.sqlite")), key=os.path.getmtime)[-1]
OUT_DIR = REPO / "docs" / "reports" / "plans"
OUT_DIR.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(SNAP)
con.row_factory = sqlite3.Row
cur = con.cursor()

# 1. ADG nodes table is module/symbol level (entity_type values are
#    'module', 'symbol', etc. — not 'class'). We capture mixin classes via
#    AST below and join importer fan-in via the module path on the edges
#    table.
et_counts = list(cur.execute("SELECT entity_type, COUNT(*) FROM nodes GROUP BY entity_type ORDER BY 2 DESC"))
print(f"# entity_type histogram: {et_counts}", file=sys.stderr)
# Build a path -> module-node-id index for fan-in lookup
path_to_id: dict[str, int] = {}
for r in cur.execute("SELECT id, resolved_path FROM nodes WHERE resolved_path IS NOT NULL"):
    p = (r["resolved_path"] or "").replace("\\", "/")
    if p and p not in path_to_id:
        path_to_id[p] = r["id"]
print(f"# path index size: {len(path_to_id)}", file=sys.stderr)
mixin_nodes: list[dict] = []  # filled below from AST scan


# 2. Fan-in via 'inherits' (or 'imports') edges where dst is the mixin
def fanin(node_id: int, kind: str) -> int:
    row = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE dst_id = ? AND relation_type = ?",
        (node_id, kind),
    ).fetchone()
    return row[0]


# discover relation types
rel_types = [r[0] for r in cur.execute("SELECT DISTINCT relation_type FROM edges")]
print(f"# relation types: {rel_types}", file=sys.stderr)

inherit_kind = (
    "inherits" if "inherits" in rel_types else ("inherits_from" if "inherits_from" in rel_types else None)
)
import_kind = "imports" if "imports" in rel_types else None
print(f"# inherit_kind={inherit_kind}  import_kind={import_kind}", file=sys.stderr)

mixin_rows: list[dict] = []  # populated after AST pass below

# 3. Static AST scan: for every .py under the repo, find class defs whose base
#    list contains >=1 *Mixin name. Captures actual MRO consumers + their
#    full base list (the ADG models inheritance edge-by-edge, but we want the
#    full ordered tuple to reason about MRO).
EXCLUDE_DIRS = {
    "archives",
    "tools_graveyard_w5.12",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "_smoke_v1_coerce_e9aa09",
}

consumers: list[dict] = []
mixin_defs: list[dict] = []  # name -> file, line, base list
for py in REPO.rglob("*.py"):
    parts = set(py.relative_to(REPO).parts)
    if parts & EXCLUDE_DIRS:
        continue
    rel = str(py.relative_to(REPO)).replace("\\", "/")
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        continue
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        base_names: list[str] = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                base_names.append(b.id)
            elif isinstance(b, ast.Attribute):
                base_names.append(b.attr)
        mixin_bases = [b for b in base_names if b.endswith("Mixin")]
        # Definition (class name itself ends in Mixin)
        if node.name.endswith("Mixin"):
            mixin_defs.append(
                {
                    "name": node.name,
                    "file": rel,
                    "line": node.lineno,
                    "bases": base_names,
                    "body_size": len(node.body),
                }
            )
        # Consumer (subclasses >=1 Mixin)
        if mixin_bases:
            consumers.append(
                {
                    "class": node.name,
                    "file": rel,
                    "bases": base_names,
                    "mixin_bases": mixin_bases,
                    "mixin_count": len(mixin_bases),
                }
            )


# Build mixin_rows now that AST has run
def _layer_from_path(p: str) -> str:
    m = re.search(r"/(L[0-6]_[a-z_]+)/", p)
    if m:
        return m.group(1)
    if p.startswith("agentic_core/mixins/"):
        return "core_mixins"
    if p.startswith("apps_"):
        return p.split("/", 1)[0]
    return "other"


# Importer fan-in by mapping the mixin's defining file to a node id
def _file_fanin(rel_path: str) -> int:
    nid = path_to_id.get(rel_path)
    if nid is None and import_kind is None:
        return 0
    return fanin(nid, import_kind) if (nid is not None and import_kind) else 0


# usage as base (subclasser count) — count from consumers list
sub_count: Counter[str] = Counter()
for c in consumers:
    for mb in c["mixin_bases"]:
        sub_count[mb] += 1

for d in mixin_defs:
    mixin_rows.append(
        {
            "name": d["name"],
            "layer": _layer_from_path(d["file"]),
            "path": d["file"],
            "line": d["line"],
            "body_size": d["body_size"],
            "bases": d["bases"],
            "subclassers": sub_count.get(d["name"], 0),
            "importers": _file_fanin(d["file"]),
        }
    )

print(f"# mixin consumers (>=1 mixin base): {len(consumers)}", file=sys.stderr)


# 4. Cluster mixins by stem
def stem(name: str) -> str:
    n = re.sub(r"Mixin$", "", name)
    n = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", n).lower()
    return n.split("_", 1)[0]


clusters: dict[str, list[str]] = defaultdict(list)
for m in mixin_rows:
    clusters[stem(m["name"])].append(m["name"])
clusters = {k: sorted(set(v)) for k, v in clusters.items() if len(set(v)) > 1}

# 5. Top MRO consumers (deepest mixin chains)
deep = sorted(consumers, key=lambda c: c["mixin_count"], reverse=True)[:25]

# 6. Mixin usage Counter
mixin_use = Counter()
for c in consumers:
    for mb in c["mixin_bases"]:
        mixin_use[mb] += 1

# Mixins defined in code but NEVER used as base
defined_names = {m["name"] for m in mixin_rows}
unused = sorted(defined_names - set(mixin_use.keys()))

report = {
    "snapshot": os.path.basename(SNAP),
    "mixin_classes_total": len(mixin_rows),
    "mixin_consumers_total": len(consumers),
    "deepest_consumers": deep,
    "mixin_usage_top": mixin_use.most_common(40),
    "mixins_unused_as_base": unused,
    "stem_clusters_multi": clusters,
    "mixins": sorted(mixin_rows, key=lambda r: -r["subclassers"]),
}

out = OUT_DIR / "mixin_audit.json"
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"# wrote {out}", file=sys.stderr)
print(
    json.dumps(
        {
            "snapshot": report["snapshot"],
            "mixin_classes_total": report["mixin_classes_total"],
            "consumers": report["mixin_consumers_total"],
            "unused_mixins": len(report["mixins_unused_as_base"]),
            "multi_member_clusters": len(report["stem_clusters_multi"]),
        },
        indent=2,
    )
)
