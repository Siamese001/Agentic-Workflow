"""
Probe ADG behavioral edges relevant to Script vs Agent classification.
Shows what signals are already captured per-file and what gaps exist.
"""

import sqlite3
from pathlib import Path

DB = Path(r"c:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03132026_0745.sqlite")
con = sqlite3.connect(DB)
cur = con.cursor()

# --- 1. Behavioral edge types already in ADG that map to Script-vs-Agent signals ---
BEHAVIORAL_EDGES = [
    # Agent-side signals (goal-directed, adaptive, stateful)
    "orchestrates_healing",
    "dispatches_healing_run",
    "agent_executes_agent",
    "routes_through",
    "escalates_to_human",
    "generates_prompt",
    "consumes_prompt",
    "validated_by_llm_gateway",
    "gated_by_confidence",
    "retrieves_via",
    "pulls_context",
    "observes_policy_state",
    "observes_runtime_state",
    "scores_groundedness",
    "invokes_dynamic",
    "invokes_getattr_dynamic",
    "snapshots_state",
    # Script-side signals (deterministic, linear, side-effect)
    "reads_env",
    "reads_config",
    "reads_governed_config",
    "reads_policy_state",
    "reads_runtime_state",
    "uses_wall_clock",
    "uses_random",
    "writes_to",
    "reads_from",
    "external_http_call",
    "execution_terminates_at_uwg",
    # Observability / tracing signals
    "records_execution_trace",
    "signs_execution_trace",
    "emits_drift_alert",
    "emits_determinism_digest",
    "triggered_telemetry",
    "hard_fails_untranscripted",
]

print("=== BEHAVIORAL EDGE COVERAGE PER SIGNAL TYPE ===\n")
for edge in BEHAVIORAL_EDGES:
    cur.execute("SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type=?", (edge,))
    n_files = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (edge,))
    n_total = cur.fetchone()[0]
    print(f"  {edge:<40} {n_files:>5} files  {n_total:>6} edges")

# --- 2. Per-file behavioral profile for a sample AGENT file ---
print("\n=== BEHAVIORAL PROFILE: FileClassificationAgent.py ===\n")
cur.execute("SELECT id FROM nodes WHERE adg_name LIKE '%FileClassificationAgent%' AND entity_type='module'")
fca_row = cur.fetchone()
if fca_row:
    fca_id = fca_row[0]
    cur.execute(
        """
        SELECT relation_type, COUNT(*) as cnt, GROUP_CONCAT(symbol, ', ') as symbols
        FROM edges
        WHERE src_id=? OR dst_id=?
        GROUP BY relation_type
        ORDER BY cnt DESC
    """,
        (fca_id, fca_id),
    )
    for row in cur.fetchall():
        rtype, cnt, syms = row
        sym_preview = (syms or "")[:80]
        print(f"  {rtype:<40} {cnt:>4}  [{sym_preview}]")

# --- 3. Compare: a known script file vs a known agent file ---
print("\n=== EDGE TYPE COMPARISON: Script vs Agent ===\n")

# Find a script file
cur.execute("""
    SELECT n.adg_name, n.resolved_path
    FROM nodes n
    WHERE n.resolved_path LIKE '%scripts/%'
      AND n.entity_type='module'
    LIMIT 5
""")
scripts = cur.fetchall()
print("Sample script-territory files:")
for s in scripts:
    print(f"  {s[1]}")

# Find agent files
cur.execute("""
    SELECT n.adg_name, n.resolved_path
    FROM nodes n
    WHERE n.resolved_path LIKE '%reasoning/%'
      AND n.resolved_path LIKE '%Agent%'
      AND n.entity_type='module'
    LIMIT 5
""")
agents = cur.fetchall()
print("\nSample agent-territory files:")
for a in agents:
    print(f"  {a[1]}")

# --- 4. Which behavioral edges would distinguish them? ---
print("\n=== AGENT-SIDE SIGNALS: files that have them ===\n")
agent_signals = [
    "orchestrates_healing",
    "agent_executes_agent",
    "generates_prompt",
    "consumes_prompt",
    "gated_by_confidence",
    "scores_groundedness",
    "escalates_to_human",
    "snapshots_state",
    "observes_runtime_state",
    "dispatches_healing_run",
]
for sig in agent_signals:
    cur.execute(
        """
        SELECT n.resolved_path
        FROM edges e JOIN nodes n ON e.src_id = n.id
        WHERE e.relation_type=?
        LIMIT 3
    """,
        (sig,),
    )
    paths = [r[0] for r in cur.fetchall()]
    print(f"  {sig}:")
    for p in paths:
        print(f"    {p}")

# --- 5. What is entity_type breakdown? ---
print("\n=== ENTITY TYPE BREAKDOWN ===\n")
cur.execute("SELECT entity_type, COUNT(*) FROM nodes GROUP BY entity_type ORDER BY COUNT(*) DESC")
for row in cur.fetchall():
    print(f"  {row[0]:<30} {row[1]}")

# --- 6. identity_kind breakdown ---
print("\n=== IDENTITY KIND BREAKDOWN ===\n")
cur.execute(
    "SELECT identity_kind, COUNT(*) FROM nodes GROUP BY identity_kind ORDER BY COUNT(*) DESC LIMIT 20",
)
for row in cur.fetchall():
    print(f"  {row[0]:<30} {row[1]}")

con.close()
