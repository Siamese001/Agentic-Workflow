import sqlite3

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04232026_0925.sqlite")

prefix = "ADG::Symbol::agentic_core.runtime.contracts.lifecycle_trace_contract"
like = prefix + "%"

print("symbols in module:", c.execute("SELECT COUNT(*) FROM nodes WHERE adg_name LIKE ?", (like,)).fetchone())

print(
    "fan-in to all those symbols:",
    c.execute(
        "SELECT COUNT(*) FROM edges WHERE dst_id IN (SELECT id FROM nodes WHERE adg_name LIKE ?)", (like,)
    ).fetchone(),
)

print("\nby relation_type:")
for r in c.execute(
    "SELECT e.relation_type, COUNT(*) FROM edges e "
    "WHERE e.dst_id IN (SELECT id FROM nodes WHERE adg_name LIKE ?) "
    "GROUP BY e.relation_type ORDER BY 2 DESC",
    (like,),
):
    print(r)

print(
    "\ndistinct caller files:",
    c.execute(
        "SELECT COUNT(DISTINCT n.resolved_path) FROM edges e "
        "JOIN nodes n ON n.id=e.src_id "
        "WHERE e.dst_id IN (SELECT id FROM nodes WHERE adg_name LIKE ?)",
        (like,),
    ).fetchone(),
)

print("\ntop 10 caller files:")
for r in c.execute(
    "SELECT n.resolved_path, COUNT(*) c FROM edges e "
    "JOIN nodes n ON n.id=e.src_id "
    "WHERE e.dst_id IN (SELECT id FROM nodes WHERE adg_name LIKE ?) "
    "GROUP BY n.resolved_path ORDER BY c DESC LIMIT 10",
    (like,),
):
    print(r)

print("\ntop 10 referenced symbols in this module (by fan-in):")
for r in c.execute(
    "SELECT n.adg_name, COUNT(*) c FROM edges e "
    "JOIN nodes n ON n.id=e.dst_id "
    "WHERE n.adg_name LIKE ? "
    "GROUP BY n.adg_name ORDER BY c DESC LIMIT 10",
    (like,),
):
    print(r)
