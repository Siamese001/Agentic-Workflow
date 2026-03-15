"""P2/L5 Safety Audit Trails baseline audit."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L5_FILTER = f"AND source_file LIKE '%L5%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Runtime edge counts (non-test) ===")
for rel in (
    "applies_guardrail",
    "validated_by_safety_plane",
    "requires_human_review",
    "escalates_to_human",
    "references_policy_hash",
    "safety_audit_emitted",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {FILTERS}", (rel,))
    total = c.fetchone()[0]
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {L5_FILTER}", (rel,))
    l5 = c.fetchone()[0]
    print(f"  {rel:<45} total={total:4d}  L5={l5:4d}")

print("\n=== L5 key symbols (non-test) ===")
for sym in (
    "SafetyAuditRecord",
    "emit_safety_audit_record",
    "SafetyContext",
    "DecisionContext",
    "TraceContext",
    "SafetyAuditMissingError",
    "HumanReviewAuditError",
    "safety_audit_id",
    "policy_hash",
    "decision_outcome",
    "reason_hash",
    "actor_id",
    "action_class",
    "evaluated_input_hash",
    "evaluated_output_hash",
    "reviewer_id",
    "reviewer_outcome",
    "override_flag",
    "override_reason_hash",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {FILTERS}", (f"%{sym}%",))
    n = c.fetchone()[0]
    print(f"  symbol:{sym:<40} sources={n:4d}")

print("\n=== L5 non-test source files ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L5%' {FILTERS} ORDER BY source_file LIMIT 60"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== applies_guardrail edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='applies_guardrail' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== validated_by_safety_plane edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='validated_by_safety_plane' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== requires_human_review edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='requires_human_review' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
