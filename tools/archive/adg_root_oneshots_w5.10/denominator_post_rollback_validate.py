"""Step 8+9: Validate denominator reduction and governance preservation."""
import glob
import json
import os
import sqlite3

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
GOV_DIR = r"C:\Git\Agentic-Workflow\artifacts\governance"

# Load pre-rollback snapshot
pre_path = os.path.join(GOV_DIR, "pre_denominator_snapshot.json")
with open(pre_path) as f:
    pre = json.load(f)

# Find latest (post-rollback) SQLite
pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
files = sorted(glob.glob(pattern))
db_path = files[-1]
print(f"Post-rollback DB: {db_path}")
print(f"Pre-rollback DB:  {pre['sqlite_path']}")

conn = sqlite3.connect(db_path)

# === STEP 8: Denominator reduction ===
print("\n" + "=" * 70)
print("STEP 8: DENOMINATOR REDUCTION VALIDATION")
print("=" * 70)

base_query = """
SELECT relation_type, COUNT(*)
FROM edges
WHERE relation_type IN ('writes_to','reads_from','records_execution_trace','calls')
GROUP BY relation_type
"""
post_base = dict(conn.execute(base_query).fetchall())

print(f"\n{'Edge Type':<30} {'Pre':>10} {'Post':>10} {'Delta':>10} {'Reduction':>10}")
print("-" * 70)
all_pass = True
for rt in sorted(set(list(pre["base_denominators"].keys()) + list(post_base.keys()))):
    pre_val = pre["base_denominators"].get(rt, 0)
    post_val = post_base.get(rt, 0)
    delta = post_val - pre_val
    pct = f"{(1 - post_val / pre_val) * 100:.1f}%" if pre_val > 0 else "N/A"
    status = "✓ REDUCED" if delta < 0 else ("= STABLE" if delta == 0 else "✗ INCREASED")
    if delta > 0:
        all_pass = False
    print(f"  {rt:<28} {pre_val:>10,} {post_val:>10,} {delta:>+10,} {pct:>10}  {status}")

total_pre = pre["total_edges"]
total_post = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
total_nodes_post = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
print(f"\n  Total edges:  {total_pre:>10,} -> {total_post:>10,}  ({total_post - total_pre:>+,})")
print(f"  Total nodes:  {pre['total_nodes']:>10,} -> {total_nodes_post:>10,}  ({total_nodes_post - pre['total_nodes']:>+,})")

# === STEP 9: Governance preservation ===
print("\n" + "=" * 70)
print("STEP 9: GOVERNANCE PRESERVATION VALIDATION")
print("=" * 70)

gov_query = """
SELECT relation_type, COUNT(*)
FROM edges
WHERE relation_type IN (
    'writes_through','reads_through','pulls_context',
    'emits_determinism_digest','applies_guardrail','emits_metric_event',
    'signs_execution_trace','snapshots_state','emits_replay_key',
    'validated_by_safety_plane','execution_terminates_at_uwg'
)
GROUP BY relation_type
"""
post_gov = dict(conn.execute(gov_query).fetchall())

print(f"\n{'Edge Type':<35} {'Pre':>8} {'Post':>8} {'Delta':>8} {'Status'}")
print("-" * 70)
gov_pass = True
for rt in sorted(set(list(pre["governance_numerators"].keys()) + list(post_gov.keys()))):
    pre_val = pre["governance_numerators"].get(rt, 0)
    post_val = post_gov.get(rt, 0)
    delta = post_val - pre_val
    if delta == 0:
        status = "= PRESERVED"
    elif delta > 0:
        status = "+ INCREASED"
    else:
        pct_loss = abs(delta) / pre_val * 100 if pre_val else 0
        if pct_loss > 5:
            status = f"✗ LOST {pct_loss:.1f}%"
            gov_pass = False
        else:
            status = f"~ MINOR -{pct_loss:.1f}%"
    print(f"  {rt:<33} {pre_val:>8,} {post_val:>8,} {delta:>+8,}  {status}")

# === Summary ===
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"  Denominator reduction: {'PASS' if all_pass else 'FAIL'}")
print(f"  Governance preserved:  {'PASS' if gov_pass else 'FAIL'}")
print(f"  Overall:               {'PASS ✓' if all_pass and gov_pass else 'FAIL ✗'}")

# === Save post-rollback snapshot ===
all_types = dict(conn.execute(
    "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC",
).fetchall())

post_snapshot = {
    "sqlite_path": db_path,
    "base_denominators": post_base,
    "governance_numerators": post_gov,
    "total_edges": total_post,
    "total_nodes": total_nodes_post,
    "all_relation_types": all_types,
}
out_path = os.path.join(GOV_DIR, "post_denominator_baseline.json")
with open(out_path, "w") as f:
    json.dump(post_snapshot, f, indent=2)
print(f"\n  Post-rollback baseline saved: {out_path}")

conn.close()
