import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
con = sqlite3.connect(db)
cur = con.cursor()

print("=== ALL L0 edges by relation_type and source_file (routing engines) ===")
cur.execute(
    "SELECT e.relation_type, e.source_file, e.line_no, e.symbol"
    " FROM edges e JOIN nodes n ON e.src_id=n.id"
    " WHERE n.layer='L0'"
    " AND e.source_file LIKE '%L0_routing/engines/%'"
    " AND e.relation_type NOT IN ('imports','dead_imports','implements','calls')"
    " ORDER BY e.source_file, e.relation_type, e.line_no"
)
for r in cur.fetchall():
    print(f"  {r[1][-50:]:<52} rel={r[0]:<35} line={r[2]}  sym={r[3]}")

print()
print("=== stamp_decision detection check ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.relation_type, e.symbol"
    " FROM edges e"
    " WHERE e.symbol LIKE '%stamp_decision%'"
    " ORDER BY e.source_file"
)
for r in cur.fetchall():
    print(f"  {r[0][-60:]:<62} line={r[1]}  rel={r[2]}  sym={r[3]}")

print()
print("=== proof_op detection check ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.relation_type, e.symbol"
    " FROM edges e"
    " WHERE e.symbol LIKE '%proof_op%'"
    " ORDER BY e.source_file"
)
for r in cur.fetchall():
    print(f"  {r[0][-60:]:<62} line={r[1]}  rel={r[2]}  sym={r[3]}")

print()
print("=== emit_proof detection check ===")
cur.execute(
    "SELECT e.source_file, e.line_no, e.relation_type, e.symbol"
    " FROM edges e"
    " WHERE e.symbol LIKE '%emit_proof%'"
    " ORDER BY e.source_file"
)
for r in cur.fetchall():
    print(f"  {r[0][-60:]:<62} line={r[1]}  rel={r[2]}  sym={r[3]}")

con.close()
