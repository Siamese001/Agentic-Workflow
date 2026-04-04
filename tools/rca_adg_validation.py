# Deep analysis of the ADG validation failure
import json
import sqlite3

conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_1955.sqlite')

print('=== ADG EDGE SEMANTIC PRECISION VALIDATION RCA ===')
print()

# Read the validation report
with open('artifacts/adg/closure_validation_report_03272026_1955.json') as f:
    report = json.load(f)

# Find the EDGE SEMANTIC PRECISION row
semantic_row = None
for row in report['closure_rows']:
    if row['capability'] == 'EDGE SEMANTIC PRECISION':
        semantic_row = row
        break

if semantic_row:
    print(f"Validation status: {'PASSED' if semantic_row['passed'] else 'FAILED'}")
    print(f"Numerator: {semantic_row['numerator']}")
    print(f"Denominator: {semantic_row['denominator']}")
    print(f"Ratio: {semantic_row['ratio']}")
    print(f"Threshold: {semantic_row['threshold']}")
    print()

    evidence = semantic_row.get('evidence', {})
    print("Evidence from validation:")
    for key, value in evidence.items():
        print(f"  {key}: {value}")
    print()

# Check the actual validation logic in the scanner
print('=== VALIDATION LOGIC ANALYSIS ===')
print()

# The issue is in _check_semantic_depth function
# Let's check what it's measuring

cursor = conn.execute('SELECT COUNT(*) FROM edges')
total_edges = cursor.fetchone()[0]
print(f"Total edges in database: {total_edges}")

cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE semantic_type IS NOT NULL AND semantic_type != \"\"')
semantic_edges = cursor.fetchone()[0]
print(f"Edges with semantic_type: {semantic_edges}")

cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = \"execution\"')
execution_total = cursor.fetchone()[0]
print(f"Execution edges: {execution_total}")

# Check for the specific generic semantics the validation checks
generic_semantics = ['execution', 'execution_generic', 'execution_trace']
cursor = conn.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = \"execution\" AND semantic_type IN ({})'.format(
    ','.join(['?' for _ in generic_semantics])
), generic_semantics)
execution_generic = cursor.fetchone()[0]
print(f"Execution edges with generic semantic types: {execution_generic}")

# The validation expects this to be < 1% of execution edges
generic_ratio = execution_generic / execution_total if execution_total > 0 else 0
print(f"Generic semantic ratio: {generic_ratio:.6f}")
print("Threshold: < 0.01 (1%)")

if generic_ratio >= 0.01:
    print("❌ VALIDATION WOULD FAIL: Generic semantic ratio too high")
else:
    print("✅ VALIDATION SHOULD PASS: Generic semantic ratio acceptable")

# Check if there's a mismatch between what the validation expects and reality
print()
print('=== ROOT CAUSE ANALYSIS ===')
print()

if semantic_row and not semantic_row['passed']:
    print("The validation failed but our analysis shows it should pass.")
    print("This suggests:")
    print("1. The validation is checking different data than what's in the database")
    print("2. There's a timing issue between when validation runs and when data is written")
    print("3. The validation logic has a bug")

    # Check if the issue is in the evidence reporting
    evidence = semantic_row.get('evidence', {})
    reported_generic = evidence.get('execution_generic_semantic_count', 0)
    reported_total = evidence.get('execution_total', 0)

    print(f"Validation reports: {reported_generic}/{reported_total} generic execution edges")
    print(f"Database shows: {execution_generic}/{execution_total} generic execution edges")

    if reported_generic != execution_generic or reported_total != execution_total:
        print("❌ DATA MISMATCH: Validation report doesn't match database")
    else:
        print("✅ Data matches - issue is elsewhere")
else:
    print("Validation passed - no issue detected")

conn.close()
