"""W1 one-shot: triage miss log — how many rescuable via on-disk plan register?"""
import json
from pathlib import Path
from collections import Counter

log = Path("artifacts/cursor/backlog_plan_linkage_misses.jsonl")
slugs = Counter()
for line in log.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    try:
        rec = json.loads(line)
        slugs[rec["slug"]] += 1
    except Exception:
        pass

plans_dir = Path("docs/archive/windsurf/legacy-tree/plans")
on_disk = {p.stem for p in plans_dir.glob("*.md")}

miss_total = sum(slugs.values())
on_disk_rescue = sum(n for s, n in slugs.items() if s in on_disk)
on_disk_slugs = [s for s in slugs if s in on_disk]
truly_orphan_slugs = [s for s in slugs if s not in on_disk]

print(f"Total miss rows:              {miss_total}")
print(f"Unique miss slugs:            {len(slugs)}")
print(f"Slugs with on-disk plan file: {len(on_disk_slugs)}  (rescuable via register+relink)")
print(f"Slugs with NO on-disk file:   {len(truly_orphan_slugs)}  (true orphan)")
print(f"Rows rescuable by registering on-disk plans: {on_disk_rescue}")
print(f"Rows that are true orphans:                  {miss_total - on_disk_rescue}")
print()
print("Top 15 miss slugs (R=rescuable on-disk, O=orphan):")
for s, n in slugs.most_common(15):
    tag = "R" if s in on_disk else "O"
    print(f"  [{tag}] {n:>3}  {s[:80]}")
