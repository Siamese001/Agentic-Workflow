import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03242026_1825.sqlite")
cursor = conn.cursor()

# Check if test modules are in the ADG
cursor.execute(
    'SELECT adg_name FROM entities WHERE adg_name LIKE "%tests%" OR adg_name LIKE "%test%" LIMIT 10'
)
test_entities = cursor.fetchall()

print("Test-related entities in ADG:")
for entity in test_entities:
    print(f"  {entity[0]}")

# Count test modules
cursor.execute('SELECT COUNT(*) FROM entities WHERE adg_name LIKE "%tests%" OR adg_name LIKE "%test%"')
test_count = cursor.fetchone()[0]
print(f"\nTotal test entities: {test_count}")

# Check specific test coverage relations
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "covers"')
covers_count = cursor.fetchone()[0]
print(f"Covers relations (test coverage): {covers_count}")

# Check defines_test_case relations
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "defines_test_case"')
test_case_count = cursor.fetchone()[0]
print(f"Defines test case relations: {test_case_count}")

# Check defines_test_suite relations
cursor.execute('SELECT COUNT(*) FROM edges WHERE relation_type = "defines_test_suite"')
test_suite_count = cursor.fetchone()[0]
print(f"Defines test suite relations: {test_suite_count}")

conn.close()
