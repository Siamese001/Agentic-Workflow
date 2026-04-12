import sqlite3

DB = r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0558.sqlite"
conn = sqlite3.connect(DB)
c = conn.cursor()

# Gap 1 - execution ordering relations
print("=== GAP 1: Execution ordering ===")
for rel in [
    "dag_precedes",
    "schedules",
    "orders_before",
    "task_depends_on",
    "routes_path",
    "routes_through",
    "dispatches_healing_run",
    "orchestrates_healing",
    "proposal_commits_routing",
]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

# Gap 2 - elevator shaft / state bus
print("\n=== GAP 2: State bus / elevator shaft ===")
for rel in [
    "pulls_context",
    "snapshots_state",
    "freezes_context",
    "unfreezes_context",
    "reads_runtime_state",
    "observes_runtime_state",
]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

# Gap 3 - policy coverage vs execution surface
print("\n=== GAP 3: Policy coverage vs execution ===")
exec_rels = ["calls", "invokes_eval", "invokes_dynamic", "invokes_getattr_dynamic"]
policy_rels = [
    "references_policy_hash",
    "applies_guardrail",
    "validated_by_llm_gateway",
    "validated_by_registry",
    "validated_by_safety_plane",
    "verifies_policy",
    "gated_by_confidence",
]
for rel in exec_rels + policy_rels:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

# Gap 6 - dynamic dispatch details: which files are sources
print("\n=== GAP 6: invokes_getattr_dynamic sources (top 10 files) ===")
c.execute("""
    SELECT source_file, COUNT(*) as cnt
    FROM edges
    WHERE relation_type='invokes_getattr_dynamic'
    GROUP BY source_file
    ORDER BY cnt DESC
    LIMIT 10
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Gap 7 - credential access governance
print("\n=== GAP 7: Credential governance ===")
for rel in [
    "accesses_credential",
    "reads_secret",
    "applies_guardrail",
    "reenters_safety",
    "hard_fails_untranscripted",
    "validated_by_safety_plane",
]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

# Gap 8 - network surface
print("\n=== GAP 8: Network surface ===")
for rel in ["external_http_call", "enters_sandbox", "intercepts_io", "grants_resource", "invokes_provider"]:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    print(f"  {rel}: {c.fetchone()[0]}")

# Check for DAGManager / Orchestrator / ActionNode nodes
print("\n=== GAP 1: Node existence for orchestration classes ===")
for name in ["DAGManager", "Orchestrator", "ActionNode", "ToolIntentExecutor"]:
    c.execute("SELECT COUNT(*) FROM nodes WHERE adg_name LIKE ?", (f"%{name}%",))
    cnt = c.fetchone()[0]
    print(f"  nodes containing '{name}': {cnt}")
    if cnt > 0 and cnt <= 5:
        c.execute(
            "SELECT adg_name, entity_type, layer FROM nodes WHERE adg_name LIKE ? LIMIT 5",
            (f"%{name}%",),
        )
        for row in c.fetchall():
            print(f"    -> {row}")

# Check for elevator shaft / state bus nodes
print("\n=== GAP 2: State bus node existence ===")
for name in ["elevator", "state_bus", "StateBus", "ElevatorShaft", "semantic_clock"]:
    c.execute("SELECT COUNT(*) FROM nodes WHERE adg_name LIKE ?", (f"%{name}%",))
    cnt = c.fetchone()[0]
    print(f"  nodes containing '{name}': {cnt}")

conn.close()
