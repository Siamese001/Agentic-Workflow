"""Find files with new HIGH-severity violations not in old snapshot."""
import sqlite3, glob, os
old = "artifacts/adg/adg_indexed_04252026_0521.sqlite"
new = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]

def fetch_high(path):
    c = sqlite3.connect(path)
    cur = c.cursor()
    cur.execute("SELECT category, severity, evidence, file_path, line_no FROM violations WHERE disposition='untriaged' AND severity IN ('HIGH','CRITICAL','P0')")
    rows = cur.fetchall()
    c.close()
    return rows

old_rows = fetch_high(old)
new_rows = fetch_high(new)
print(f"Old HIGH+: {len(old_rows)}")
print(f"New HIGH+: {len(new_rows)}\n")

old_set = set((r[3], r[4]) for r in old_rows)  # by (file, line)
new_set = set((r[3], r[4]) for r in new_rows)

added_keys = new_set - old_set
print(f"Added high-severity loci: {len(added_keys)}")

new_by_key = {(r[3], r[4]): r for r in new_rows}
files_count = {}
for k in added_keys:
    fp = k[0]
    files_count[fp] = files_count.get(fp, 0) + 1

# Top files
sorted_files = sorted(files_count.items(), key=lambda x: -x[1])
print("\nTop files with NEW high-severity violations:")
for fp, cnt in sorted_files[:25]:
    print(f"  {cnt:>3d}  {fp}")

# Sample evidence
print("\nSample new HIGH-severity violations:")
for k in list(added_keys)[:15]:
    r = new_by_key[k]
    print(f"  [{r[1]}] {r[3]}:{r[4]}  ev={r[2]}")
