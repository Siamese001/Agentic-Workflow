import sqlite3

c = sqlite3.connect("artifacts/adg/adg_indexed_04232026_2248.sqlite").cursor()
print("edges cols:")
print([d[0] for d in c.execute("SELECT * FROM edges LIMIT 0").description])
print()
rows = c.execute(
    "SELECT v.id, v.file_path, v.line_no, v.evidence, v.edge_id, e.* "
    "FROM violations v LEFT JOIN edges e ON v.edge_id = e.id "
    "WHERE v.severity='HIGH'"
).fetchall()
for r in rows:
    print(r)
