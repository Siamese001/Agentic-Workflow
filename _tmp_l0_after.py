#!/usr/bin/env python3
import os
import sqlite3

adg_dir = r"artifacts\adg"
sqls = sorted([f for f in os.listdir(adg_dir) if f.endswith(".sqlite")], reverse=True)
db = os.path.join(adg_dir, sqls[0])
print(f"DB: {sqls[0]}")
conn = sqlite3.connect(db)
c = conn.cursor()

proof_edges = [
    "routes_path",
    "routes_through",
    "emits_replay_key",
    "emits_determinism_digest",
    "proposal_commits_routing",
    "signs_execution_trace",
    "uses_wall_clock",
    "invokes_getattr_dynamic",
    "patches_time",
]


def count_edge(et, layer=None):
    if layer == "L0":
        c.execute(
            'SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id WHERE n.layer="L0" AND e.relation_type=?',
            (et,),
        )
    elif layer == "prod":
        c.execute(
            'SELECT COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id WHERE n.layer!="L_TEST" AND e.relation_type=?',
            (et,),
        )
    else:
        c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (et,))
    return c.fetchone()[0]


before_total = {
    "routes_path": 48,
    "routes_through": 61,
    "emits_replay_key": 8,
    "emits_determinism_digest": 6,
    "proposal_commits_routing": 42,
    "signs_execution_trace": 21,
    "uses_wall_clock": 857,
    "invokes_getattr_dynamic": 2992,
    "patches_time": 0,
}
before_l0 = {
    "routes_path": 0,
    "routes_through": 0,
    "emits_replay_key": 0,
    "emits_determinism_digest": 0,
    "proposal_commits_routing": 1,
    "signs_execution_trace": 0,
    "uses_wall_clock": 21,
    "invokes_getattr_dynamic": 193,
    "patches_time": 0,
}

print()
print(f"{'Edge':<35} {'B-total':>8} {'A-total':>8} {'B-L0':>7} {'A-L0':>7}")
print("-" * 68)
for et in proof_edges:
    bt = before_total.get(et, 0)
    at = count_edge(et)
    bl = before_l0.get(et, 0)
    al = count_edge(et, "L0")
    dt = f"+{at - bt}" if at > bt else (f"{at - bt}" if at < bt else "=")
    dl = f"+{al - bl}" if al > bl else (f"{al - bl}" if al < bl else "=")
    print(f"{et:<35} {bt:>8} {at:>8} ({dt:>5})  {bl:>7} {al:>7} ({dl:>5})")

# L0 routing proof coverage
c.execute('SELECT COUNT(*) FROM nodes WHERE layer="L0"')
total_l0 = c.fetchone()[0]
c.execute("""
    SELECT COUNT(DISTINCT n.id) FROM nodes n
    WHERE n.layer="L0"
    AND EXISTS (
        SELECT 1 FROM edges e WHERE e.src_id=n.id
        AND e.relation_type IN ("routes_path","emits_replay_key","emits_determinism_digest","proposal_commits_routing")
    )
""")
covered = c.fetchone()[0]
print(f"\nL0 routing proof coverage: {covered}/{total_l0} = {covered / total_l0 * 100:.2f}%")

# Per-file check for the 5 changed files
files = [
    "agentic_core/L0_routing/scripts/execute_ssot.py",
    "agentic_core/L0_routing/scripts/_ssot_routing.py",
    "agentic_core/L0_routing/seam/seam_audit.py",
    "agentic_core/L0_routing/artifacts/deterministic_routing_gateway.py",
    "agentic_core/L0_routing/policy/route_policy_governor.py",
]
check_edges = [
    "routes_path",
    "emits_replay_key",
    "emits_determinism_digest",
    "proposal_commits_routing",
    "uses_wall_clock",
    "patches_time",
]
print("\nPer-file routing proof edges after change:")
for f in files:
    c.execute(
        """
        SELECT e.relation_type, COUNT(*) FROM edges e JOIN nodes n ON e.src_id=n.id
        WHERE n.resolved_path=?
        AND e.relation_type IN ("routes_path","emits_replay_key","emits_determinism_digest",
            "proposal_commits_routing","uses_wall_clock","patches_time")
        GROUP BY e.relation_type
    """,
        (f,),
    )
    rows = {r[0]: r[1] for r in c.fetchall()}
    fname = f.split("/")[-1]
    hits = [f"{et}={rows[et]}" for et in check_edges if et in rows]
    print(f"  {fname}: {', '.join(hits) if hits else '(no proof/clock edges)'}")

conn.close()
