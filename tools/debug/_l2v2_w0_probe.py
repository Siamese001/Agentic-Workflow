"""W0 ADG probe for plan l2-execute-v2-agent-conformance-c8e4f1.

Ranks agent files by fan-in (imports into them) + archetype + surface.
Produces a hotspot report for plan sections §10/§11.
"""

from __future__ import annotations

import glob
import os
import sqlite3
import sys

# -- locate latest ADG snapshot
snapshots = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)
if not snapshots:
    sys.stderr.write("No ADG snapshot found\n")
    sys.exit(2)
SNAP = snapshots[-1]
print(f"snapshot={SNAP}\n")

con = sqlite3.connect(SNAP)
cur = con.cursor()

# Validator/Healer exemplar pairs to rank
AGENTS_OF_INTEREST = [
    # stub heal methods (W3 targets)
    ("StructuredEngineAgent", "agentic_core/L2_execution/reasoning/StructuredEngineAgent.py"),
    ("ResumeAssemblyAgent", "apps_rg/reasoning/ResumeAssemblyAgent.py"),
    ("BaseProactiveAgent", "apps_shared/reasoning/BaseProactiveAgent.py"),
    ("BaseReflectionAgent", "apps_shared/reasoning/BaseReflectionAgent.py"),
    # co-located validate+heal (W6 exemplar candidates)
    ("ArchitectureGovernorAgent", "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py"),
    (
        "ArchitectureGovernorValidatorAgent",
        "agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py",
    ),
    ("ContentQualityAgent", "apps_rg/reasoning/ContentQualityAgent.py"),
    ("RedisSovereignAgent", "agentic_core/L2_execution/reasoning/RedisSovereignAgent.py"),
    ("EmbeddingSovereignAgent", "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py"),
    ("SubAtomicRegistryAgent", "agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py"),
    ("MetaLearningAgent", "agentic_core/L1_cognition/reasoning/MetaLearningAgent.py"),
    ("NamingAgent", "agentic_core/L5_safety/reasoning/NamingAgent.py"),
    ("DocstringComplianceAgent", "agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py"),
    ("DDDAlignmentAgent", "agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py"),
    ("CodeJanitorAgent", "agentic_core/L5_safety/reasoning/CodeJanitorAgent.py"),
    # base class
    ("SovereignBaseAgent", "agentic_core/base_agents/SovereignBaseAgent.py"),
]

print(f"{'agent':<40} {'fan_in':>7} {'fan_out':>8}  {'layer':<4}  resolved_path")
rows: list[tuple[str, int, int, str, str]] = []
for name, path_hint in AGENTS_OF_INTEREST:
    # Match on resolved_path LIKE
    cur.execute(
        "SELECT id, resolved_path, layer FROM nodes WHERE resolved_path LIKE ? AND entity_type='module'",
        (f"%{name}.py",),
    )
    nrows = cur.fetchall()
    for nid, rp, layer in nrows:
        cur.execute(
            "SELECT COUNT(*) FROM edges WHERE dst_id=? AND relation_type='imports'",
            (nid,),
        )
        fi = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM edges WHERE src_id=? AND relation_type='imports'",
            (nid,),
        )
        fo = cur.fetchone()[0]
        rows.append((name, fi, fo, layer or "?", rp))
        print(f"{name:<40} {fi:>7} {fo:>8}  {layer or '?':<4}  {rp}")

# -- graph layer evidence: check which MVs contain any of our target files
print("\n--- MV hits for target files ---")
target_basenames = [os.path.basename(p) for _, p in AGENTS_OF_INTEREST]

cur.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'mv_%' ORDER BY name")
mv_names = [r[0] for r in cur.fetchall()]

interesting_mvs = [
    "mv_l2_phase_coverage",
    "mv_agent_specialization_overlap",
    "mv_actionable_surface_without_schema",
    "mv_tool_surface_overlap",
    "mv_agent_tool_ratio",
    "mv_graph_reverse_dependency_hotspots",
]
for mv in interesting_mvs:
    if mv not in mv_names:
        print(f"  {mv}: [not present in snapshot]")
        continue
    try:
        cur.execute(f"SELECT COUNT(*) FROM {mv}")
        n = cur.fetchone()[0]
        print(f"  {mv}: {n} rows")
    except sqlite3.Error as e:
        print(f"  {mv}: ERROR {e}")

# -- P-view hits: which P-views mention any agent of interest
print("\n--- P-view hits for agents ---")
cur.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_p%' ORDER BY name")
pv_names = [r[0] for r in cur.fetchall()]
for pv in pv_names:
    try:
        cur.execute(f"PRAGMA table_info({pv})")
        cols = [c[1] for c in cur.fetchall()]
        if "file_path" not in cols and "resolved_path" not in cols:
            continue
        col = "file_path" if "file_path" in cols else "resolved_path"
        hit_count = 0
        for bn in target_basenames:
            cur.execute(f"SELECT COUNT(*) FROM {pv} WHERE {col} LIKE ?", (f"%{bn}",))
            hit_count += cur.fetchone()[0]
        if hit_count:
            print(f"  {pv}: {hit_count} hits on target agents")
    except sqlite3.Error:
        continue

# -- rank candidate W6 exemplars: lowest fan_in among co-located agents
print("\n--- W6 exemplar candidates (lowest fan-in co-located agents) ---")
colocated = {
    "ContentQualityAgent",
    "NamingAgent",
    "DocstringComplianceAgent",
    "DDDAlignmentAgent",
    "CodeJanitorAgent",
    "RedisSovereignAgent",
    "EmbeddingSovereignAgent",
    "SubAtomicRegistryAgent",
    "MetaLearningAgent",
    "ArchitectureGovernorAgent",
}
col_ranked = sorted(
    [(n, fi, fo, layer, rp) for (n, fi, fo, layer, rp) in rows if n in colocated],
    key=lambda x: (x[1], x[2]),
)
for n, fi, fo, layer, rp in col_ranked[:5]:
    print(f"  {n:<35} fan_in={fi:>3} fan_out={fo:>4} layer={layer}  {rp}")

con.close()
