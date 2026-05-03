"""One-off audit: classify Retired Plans rows by accuracy signals.

Reads the Notion MCP output dump and prints a categorized summary so the
operator can decide which retirements are safe vs which need review.

Not part of any gate -- ad-hoc audit script for the 2026-05-03 question
"are these retired plans accurately retired?"
"""
import json
import sys
from pathlib import Path

DUMP = Path(sys.argv[1] if len(sys.argv) > 1 else
    "C:/Users/amita/AppData/Local/Temp/windsurf/mcp_output_4570bbeb1534c8d5.txt")

data = json.loads(DUMP.read_text(encoding="utf-8"))
rows = data["results"]

cats = {
    "superseded_documented": [],
    "retired_with_reason": [],
    "plan_file_missing": [],
    "no_summary": [],
}
seen = {}
duplicates = []

for r in rows:
    props = r["properties"]
    title = props["Slug"]["title"]
    slug = title[0]["plain_text"] if title else "(no-slug)"
    summary = "".join(c["plain_text"] for c in props["Summary"]["rich_text"]).strip()
    exists = props["Exists On Disk"]["checkbox"]
    edited = props["Last edited time"]["last_edited_time"][:10]

    if slug in seen:
        duplicates.append((slug, seen[slug], r["id"][:8]))
    seen[slug] = r["id"][:8]

    if not summary:
        cats["no_summary"].append((slug, exists, edited))
    elif not exists:
        cats["plan_file_missing"].append((slug, summary[:90], edited))
    elif "SUPERSEDED" in summary or "superseded" in summary.lower():
        cats["superseded_documented"].append((slug, edited))
    elif any(k in summary.lower() for k in (
        "retired", "stale", "replaced", "completed", "folded", "merged into", "decomposed"
    )):
        cats["retired_with_reason"].append((slug, edited))
    else:
        cats["no_summary"].append((slug, exists, edited))

print(f"Retired total: {len(rows)}")
print()
print(f"A) Superseded, documented in Summary: {len(cats['superseded_documented'])}")
print(f"B) Retired with reason in Summary:    {len(cats['retired_with_reason'])}")
print(f"C) Plan file missing from disk:       {len(cats['plan_file_missing'])}")
print(f"D) NO Summary (suspicious):           {len(cats['no_summary'])}")
print(f"E) Duplicate slug rows:               {len(duplicates)}")
print()

if cats["plan_file_missing"]:
    print("--- C) Plan file MISSING from disk (Exists On Disk=false) ---")
    for s, summ, ed in cats["plan_file_missing"]:
        print(f"  {ed}  {s}")
        print(f"           reason: {summ}")
    print()

if cats["no_summary"]:
    print("--- D) Retired with NO Summary (bulk-flip casualties?) ---")
    for s, exists, ed in cats["no_summary"]:
        print(f"  exists={exists}  edited={ed}  {s}")
    print()

if duplicates:
    print("--- E) Duplicate slugs ---")
    for s, id1, id2 in duplicates:
        print(f"  {s}: ids={id1}, {id2}")
    print()
