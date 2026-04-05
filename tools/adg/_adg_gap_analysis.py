"""Temporary ADG gap-analysis script – run once, then delete."""

import sqlite3
from pathlib import Path

db = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(str(db))

print("=== LOW-COUNT RELATIONS (< 100 edges) ===")
for row in conn.execute(
    "SELECT relation_type, COUNT(*) as cnt FROM edges GROUP BY relation_type ORDER BY cnt ASC"
):
    if row[1] < 100:
        print(f"  {row[1]:5d}  {row[0]}")

print()
print("=== ALL RELATION TYPES BY COUNT ===")
for row in conn.execute(
    "SELECT relation_type, COUNT(*) as cnt FROM edges GROUP BY relation_type ORDER BY cnt DESC"
):
    print(f"  {row[1]:6d}  {row[0]}")

print()
print("=== ENTITY TYPES ===")
for row in conn.execute(
    "SELECT entity_type, COUNT(*) as cnt FROM entities GROUP BY entity_type ORDER BY cnt DESC"
):
    print(f"  {row[1]:6d}  {row[0]}")

print()
print("=== MOST-CALLED agentic_core MODULES ===")
for row in conn.execute(
    "SELECT to_name, COUNT(*) as cnt FROM edges "
    "WHERE relation_type='calls' AND to_name LIKE 'ADG::Module::agentic_core%' "
    "GROUP BY to_name ORDER BY cnt DESC LIMIT 20"
):
    print(f"  {row[1]:5d}  {row[0]}")

print()
print("=== TOP ANTIPATTERN TARGETS ===")
for row in conn.execute(
    "SELECT to_name, COUNT(*) as cnt FROM edges "
    "WHERE relation_type='antipattern' "
    "GROUP BY to_name ORDER BY cnt DESC LIMIT 20"
):
    print(f"  {row[1]:5d}  {row[0]}")

print()
print("=== TOP VIOLATION TARGETS ===")
for row in conn.execute(
    "SELECT to_name, COUNT(*) as cnt FROM edges "
    "WHERE relation_type='violates' "
    "GROUP BY to_name ORDER BY cnt DESC LIMIT 20"
):
    print(f"  {row[1]:5d}  {row[0]}")

print()
print("=== READS_SECRET COUNT BY FROM MODULE ===")
for row in conn.execute(
    "SELECT from_name, COUNT(*) as cnt FROM edges "
    "WHERE relation_type='reads_secret' "
    "GROUP BY from_name ORDER BY cnt DESC LIMIT 15"
):
    print(f"  {row[1]:5d}  {row[0]}")

print()
print("=== INVOKES_DYNAMIC COUNT ===")
for row in conn.execute(
    "SELECT from_name, COUNT(*) as cnt FROM edges "
    "WHERE relation_type='invokes_dynamic' "
    "GROUP BY from_name ORDER BY cnt DESC LIMIT 10"
):
    print(f"  {row[1]:5d}  {row[0]}")

print()
print("=== READS_CONFIG COUNT BY FROM MODULE ===")
for row in conn.execute(
    "SELECT from_name, COUNT(*) as cnt FROM edges "
    "WHERE relation_type='reads_config' "
    "GROUP BY from_name ORDER BY cnt DESC LIMIT 10"
):
    print(f"  {row[1]:5d}  {row[0]}")

conn.close()
