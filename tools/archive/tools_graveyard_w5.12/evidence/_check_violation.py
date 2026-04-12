"""Query ADG SQLite for violation details."""

import sqlite3
from pathlib import Path

sqlite_path = Path("artifacts/adg/adg_indexed_04062026_2106.sqlite")

conn = sqlite3.connect(str(sqlite_path))
cursor = conn.cursor()

cursor.execute("SELECT source_file, line_no FROM edges WHERE relation_type='violates'")
violations = cursor.fetchall()

for sf, ln in violations:
    print(f"{sf}:{ln}")

conn.close()
