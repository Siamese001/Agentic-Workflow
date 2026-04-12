import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03242026_1825.sqlite")
cursor = conn.cursor()

# Test coverage relations (STATIC - design-time)
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "covers"')
covers_count = cursor.fetchone()[0]
print(f"Covers relations (test coverage): {covers_count}")

# Test definition relations (STATIC - design-time)
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "defines_test_case"')
test_case_count = cursor.fetchone()[0]
print(f"Defines test case relations: {test_case_count}")

cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "defines_test_suite"')
test_suite_count = cursor.fetchone()[0]
print(f"Defines test suite relations: {test_suite_count}")

# Test execution traces (RUNTIME - execution-time)
cursor.execute(
    'SELECT COUNT(*) FROM edges WHERE relation_type = "records_execution_trace" AND src_id IN (SELECT id FROM nodes WHERE adg_name LIKE "%test%")'
)
test_execution_count = cursor.fetchone()[0]
print(f"Test execution traces: {test_execution_count}")

# Check what layer tests belong to
cursor.execute(
    'SELECT DISTINCT to_name FROM edges WHERE relation_type = "belongs_to_layer" AND src_id IN (SELECT id FROM nodes WHERE adg_name LIKE "%test%" LIMIT 1)'
)
test_layer = cursor.fetchone()
if test_layer:
    print(f"Tests belong to layer: {test_layer[0]}")

# Get some examples of test modules
cursor.execute('SELECT adg_name FROM nodes WHERE adg_name LIKE "ADG::Module::test%" LIMIT 5')
test_modules = cursor.fetchall()
print("\nExample test modules:")
for module in test_modules:
    print(f"  {module[0]}")

# Get some examples of test coverage edges
cursor.execute('SELECT src_name, dst_name FROM edges WHERE relation_type = "covers" LIMIT 5')
sample_covers = cursor.fetchall()
print("\nSample test coverage edges:")
for src, dst in sample_covers:
    print(f"  {src} covers {dst}")

conn.close()
