import sqlite3

db = ".windsurf/state/refactor_decisions/refactor_decision_ledger.sqlite"
conn = sqlite3.connect(db)
conn.execute("DELETE FROM decisions WHERE decision_id = 'dec_27fa3a405863'")
conn.execute("DELETE FROM decisions_fts WHERE decision_id = 'dec_27fa3a405863'")
conn.commit()
total = conn.execute("SELECT COUNT(decision_id) FROM decisions").fetchone()[0]
orphan = conn.execute(
    "SELECT COUNT(decision_id) FROM decisions_fts WHERE decision_id = 'dec_27fa3a405863'"
).fetchone()[0]
conn.close()
print(f"decisions rows: {total}  fts orphan remaining: {orphan}")
