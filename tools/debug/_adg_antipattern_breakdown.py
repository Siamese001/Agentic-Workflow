import sqlite3

c = sqlite3.connect("artifacts/adg/adg_indexed_04232026_2248.sqlite").cursor()
print("ANTIPATTERN BY violation_class:")
for k, n in c.execute(
    "SELECT violation_class, COUNT(*) FROM violations "
    "WHERE category='antipattern' GROUP BY violation_class ORDER BY COUNT(*) DESC"
).fetchall():
    print(f"  {n:>6}  {k}")
print("\nBY severity:")
for k, n in c.execute(
    "SELECT severity, COUNT(*) FROM violations "
    "WHERE category='antipattern' GROUP BY severity ORDER BY COUNT(*) DESC"
).fetchall():
    print(f"  {n:>6}  {k}")
print("\nBY disposition:")
for k, n in c.execute(
    "SELECT disposition, COUNT(*) FROM violations "
    "WHERE category='antipattern' GROUP BY disposition ORDER BY COUNT(*) DESC"
).fetchall():
    print(f"  {n:>6}  {k}")
print("\nANTIPATTERN (severity HIGH+MEDIUM) BY violation_class:")
for k, n in c.execute(
    "SELECT violation_class, COUNT(*) FROM violations "
    "WHERE category='antipattern' AND severity IN ('HIGH','MEDIUM','high','medium','P1','P2') "
    "GROUP BY violation_class ORDER BY COUNT(*) DESC"
).fetchall():
    print(f"  {n:>6}  {k}")
