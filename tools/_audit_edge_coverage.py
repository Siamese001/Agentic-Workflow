"""Audit: which edge types appear in SQLite vs split planes, find gaps."""

import sqlite3
from pathlib import Path

adg = Path("artifacts/adg")

# All edge types defined in layer_splitter.py
FILE_GRAPH_RELS = {
    "imports",
    "belongs_to_layer",
    "covers",
    "in_cycle",
    "dead_imports",
    "exports",
    "influences",
}
SYMBOL_GRAPH_RELS = {
    "calls",
    "instantiates",
    "implements",
    "reads_from",
    "writes_to",
    "writes_through",
    "invokes_provider",
    "routes_through",
    "type_annotation",
    "decorated_by",
}
TEST_GRAPH_RELS = {"covers", "covers_module", "covers_symbol"}
GOVERNANCE_GRAPH_RELS = {
    "generates_prompt",
    "consumes_prompt",
    "assembles_into",
    "injects_into",
    "overrides_prompt",
    "executed_with_prompt",
    "triggered_telemetry",
    "proposed_improvement",
    "updated_prompt",
    "executes_action",
    "invokes_tool",
    "crosses_layer",
    "bypasses_uwg",
    "routes_through_uwg",
    "layer_authority_violation",
    "policy_hash_mismatch",
    "lineage_of",
    "violates",
    "dynamic_exec",
    "in_cycle",
    "antipattern",
}

ALL_PLANE_RELS = FILE_GRAPH_RELS | SYMBOL_GRAPH_RELS | TEST_GRAPH_RELS | GOVERNANCE_GRAPH_RELS

# Actual edge types in SQLite
conn = sqlite3.connect(str(adg / "adg_LATEST.sqlite"))
sqlite_rels = {
    row[0]: row[1] for row in conn.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
}
conn.close()

print("=== EDGE TYPES IN SQLITE (actual data) ===")
for r, n in sorted(sqlite_rels.items(), key=lambda x: -x[1]):
    in_file = r in FILE_GRAPH_RELS
    in_sym = r in SYMBOL_GRAPH_RELS
    in_test = r in TEST_GRAPH_RELS
    in_gov = r in GOVERNANCE_GRAPH_RELS
    planes = "+".join(
        p for p, flag in [("FILE", in_file), ("SYM", in_sym), ("TEST", in_test), ("GOV", in_gov)] if flag
    )
    unassigned = " *** UNASSIGNED ***" if not planes else ""
    print(f"  {r:<30} {n:>7}  planes=[{planes}]{unassigned}")

print()
print("=== OVERLAP (same rel_type in multiple planes) ===")
overlaps = []
all_plane_map = {
    "FILE": FILE_GRAPH_RELS,
    "SYM": SYMBOL_GRAPH_RELS,
    "TEST": TEST_GRAPH_RELS,
    "GOV": GOVERNANCE_GRAPH_RELS,
}
for rel in sorted(ALL_PLANE_RELS):
    in_planes = [p for p, rels in all_plane_map.items() if rel in rels]
    if len(in_planes) > 1:
        count = sqlite_rels.get(rel, 0)
        overlaps.append((rel, in_planes, count))
        print(f"  {rel:<30} appears in {in_planes}  (count={count})")

print()
print("=== SUMMARY ===")
unassigned = [r for r in sqlite_rels if r not in ALL_PLANE_RELS]
print(f"  Total edge types in SQLite: {len(sqlite_rels)}")
print(f"  Edge types covered by planes: {len([r for r in sqlite_rels if r in ALL_PLANE_RELS])}")
print(f"  UNASSIGNED (in SQLite but no plane): {unassigned}")
print(f"  Overlap (duplication): {len(overlaps)} edge types appear in >1 plane")
