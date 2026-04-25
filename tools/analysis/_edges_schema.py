import sqlite3

con = sqlite3.connect("artifacts/adg/adg_r6_test.sqlite")
print("=== edges columns ===")
for c in con.execute("SELECT name FROM pragma_table_info('edges')"):
    print(f"  {c[0]}")
print("\n=== nodes columns ===")
for c in con.execute("SELECT name FROM pragma_table_info('nodes')"):
    print(f"  {c[0]}")
print("\n=== sample edge row ===")
row = con.execute("SELECT * FROM edges LIMIT 1").fetchone()
print(f"  {row}")
