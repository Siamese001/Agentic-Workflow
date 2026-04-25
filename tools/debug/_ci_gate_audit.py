import pathlib, re

root = pathlib.Path("ops_scripts/ci")
rows = []
for f in sorted(root.glob("check_*.py")):
    txt = f.read_text(encoding="utf-8")
    if "WiringGate" not in txt:
        continue
    m = re.search(r"tier\s*=\s*[\"'](\w)[\"']", txt)
    gid = re.search(r"GATE_ID\s*=\s*[\"']([^\"']+)", txt) or re.search(r"gate_id\s*=\s*[\"']([^\"']+)", txt)
    rows.append((m.group(1) if m else "?", gid.group(1) if gid else "?", f.name))
rows.sort()
print(f"{'TIER':<5}{'GATE_ID':<48}SCRIPT")
for t, g, n in rows:
    print(f"{t:<5}{g:<48}{n}")
print(f"\ntotal: {len(rows)}")
from collections import Counter

print("by tier:", Counter(r[0] for r in rows))
