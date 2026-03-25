"""HITL ADG Analysis — query refreshed ADG for HITL architecture coverage."""

import sqlite3
from pathlib import Path

DB = Path("artifacts/adg/adg_indexed_03252026_1332.sqlite")
db = sqlite3.connect(str(DB))
c = db.cursor()

print("=" * 70)
print("HITL ADG ANALYSIS — Refreshed ADG 03252026_1332")
print("=" * 70)

# 1. HITL-related edge types
print("\n[1] HITL-Related Edge Types")
c.execute("""
    SELECT relation_type, COUNT(*) as cnt
    FROM edges
    WHERE relation_type LIKE '%hitl%'
       OR relation_type LIKE '%human%'
       OR relation_type LIKE '%escalat%'
       OR relation_type LIKE '%dpo%'
       OR relation_type LIKE '%confidence%'
       OR relation_type LIKE '%rlhf%'
       OR relation_type LIKE '%preference%'
       OR relation_type LIKE '%approval%'
    GROUP BY relation_type
    ORDER BY cnt DESC
""")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

# 2. Key HITL wiring edges
print("\n[2] Key HITL Wiring Edge Counts")
key_types = [
    "escalates_to_human",
    "gated_by_confidence",
    "builds_dpo_batch",
    "produces_preference_pair",
    "requires_human_review",
    "proposal_commits_routing",
    "validated_by_safety_plane",
    "records_execution_trace",
    "signs_execution_trace",
    "dispatches_healing_run",
    "orchestrates_healing",
    "commits_optimization",
    "scores_groundedness",
]
for kt in key_types:
    c.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (kt,))
    cnt = c.fetchone()[0]
    if cnt > 0:
        print(f"  {kt}: {cnt}")

# 3. HITL-related nodes (modules)
print("\n[3] HITL-Related Modules")
c.execute("""
    SELECT adg_name, entity_type, layer
    FROM nodes
    WHERE (adg_name LIKE '%hitl%' OR adg_name LIKE '%HITL%'
           OR adg_name LIKE '%dpo%' OR adg_name LIKE '%DPO%'
           OR adg_name LIKE '%rlhf%' OR adg_name LIKE '%RLHF%')
      AND entity_type = 'module'
    ORDER BY layer, adg_name
""")
hitl_modules = c.fetchall()
print(f"  Found {len(hitl_modules)} HITL modules:")
for n in hitl_modules:
    print(f"    [{n[2]}] {n[0]}")

# 4. Edges FROM HITL modules
print("\n[4] Edges FROM HITL Modules (outgoing wiring)")
for mod in hitl_modules:
    mod_name = mod[0]
    c.execute(
        """
        SELECT e.relation_type, COUNT(*) as cnt
        FROM edges e
        JOIN nodes src ON e.src_id = src.id
        WHERE src.adg_name = ?
        GROUP BY e.relation_type
        ORDER BY cnt DESC
        LIMIT 10
    """,
        (mod_name,),
    )
    edges = c.fetchall()
    if edges:
        print(f"\n  {mod_name}:")
        for e in edges:
            print(f"    {e[0]}: {e[1]}")

# 5. Edges TO HITL modules (incoming wiring)
print("\n[5] Edges TO HITL Modules (incoming / who calls HITL)")
for mod in hitl_modules:
    mod_name = mod[0]
    c.execute(
        """
        SELECT e.relation_type, COUNT(*) as cnt
        FROM edges e
        JOIN nodes dst ON e.dst_id = dst.id
        WHERE dst.adg_name = ?
        GROUP BY e.relation_type
        ORDER BY cnt DESC
        LIMIT 5
    """,
        (mod_name,),
    )
    edges = c.fetchall()
    if edges:
        total = sum(e[1] for e in edges)
        print(f"\n  {mod_name} (total incoming: {total}):")
        for e in edges:
            print(f"    {e[0]}: {e[1]}")

# 6. Cross-layer HITL wiring check
print("\n[6] Cross-Layer HITL Wiring (L3→L5→L6 chain)")
c.execute("""
    SELECT src_n.layer as src_layer, dst_n.layer as dst_layer,
           e.relation_type, COUNT(*) as cnt
    FROM edges e
    JOIN nodes src_n ON e.src_id = src_n.id
    JOIN nodes dst_n ON e.dst_id = dst_n.id
    WHERE (e.relation_type IN ('escalates_to_human', 'gated_by_confidence',
           'builds_dpo_batch', 'produces_preference_pair',
           'requires_human_review', 'dispatches_healing_run'))
    GROUP BY src_n.layer, dst_n.layer, e.relation_type
    ORDER BY cnt DESC
""")
for row in c.fetchall():
    print(f"  {row[0]} -> {row[1]} [{row[2]}]: {row[3]}")

# 7. Confidence gating coverage
print("\n[7] Confidence Gating Coverage")
c.execute("""
    SELECT src_n.adg_name, dst_n.adg_name
    FROM edges e
    JOIN nodes src_n ON e.src_id = src_n.id
    JOIN nodes dst_n ON e.dst_id = dst_n.id
    WHERE e.relation_type = 'gated_by_confidence'
    LIMIT 30
""")
for row in c.fetchall():
    print(f"  {row[0]} -> {row[1]}")

# 8. Escalation paths
print("\n[8] Escalation Paths (escalates_to_human)")
c.execute("""
    SELECT src_n.adg_name, dst_n.adg_name, src_n.layer
    FROM edges e
    JOIN nodes src_n ON e.src_id = src_n.id
    JOIN nodes dst_n ON e.dst_id = dst_n.id
    WHERE e.relation_type = 'escalates_to_human'
""")
for row in c.fetchall():
    print(f"  [{row[2]}] {row[0]} -> {row[1]}")

# 9. DPO/RLHF edges
print("\n[9] DPO/RLHF Edges")
c.execute("""
    SELECT e.relation_type, src_n.adg_name, dst_n.adg_name
    FROM edges e
    JOIN nodes src_n ON e.src_id = src_n.id
    JOIN nodes dst_n ON e.dst_id = dst_n.id
    WHERE e.relation_type IN ('builds_dpo_batch', 'produces_preference_pair', 'commits_optimization')
""")
for row in c.fetchall():
    print(f"  [{row[0]}] {row[1]} -> {row[2]}")

db.close()
print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
