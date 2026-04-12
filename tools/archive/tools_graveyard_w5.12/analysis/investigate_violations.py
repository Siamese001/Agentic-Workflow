import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03242026_1825.sqlite")
cursor = conn.cursor()

# Get violation details
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "violates"')
total_violations = cursor.fetchone()[0]
print(f"Total violations in ADG: {total_violations}")

# Get violation types/severity
cursor.execute('SELECT DISTINCT edge_kind FROM edges WHERE relation_type = "violates"')
violation_kinds = cursor.fetchall()
print("Violation kinds:")
for kind in violation_kinds:
    cursor.execute(
        'SELECT COUNT(*) FROM edges WHERE relation_type = "violates" AND edge_kind = ?', (kind[0],)
    )
    count = cursor.fetchone()[0]
    print(f"  {kind[0]}: {count}")

# Get some sample violations with node names
cursor.execute("""
SELECT n1.adg_name as src_name, n2.adg_name as dst_name, e.edge_kind, e.source_file, e.line_no
FROM edges e
JOIN nodes n1 ON e.src_id = n1.id
JOIN nodes n2 ON e.dst_id = n2.id
WHERE e.relation_type = "violates"
LIMIT 10
""")
sample_violations = cursor.fetchall()
print("\nSample violations:")
for src, dst, kind, file, line in sample_violations:
    print(f"  {src} -> {dst} ({kind}) at {file}:{line}")

# Check if these are the same violations mentioned in CI
print("\nCI gate status check:")
print("M4 (Guardrail Coverage): WARN - applies_guardrail/calls = 173/20710 = 0.0084 < 0.1 required")
print("M5 (Trace Coverage): WARN - trace_coverage = 333/21285 = 0.0156 < 0.05 required")

conn.close()
