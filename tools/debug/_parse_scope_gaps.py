"""One-shot: enumerate Notion rows with empty/TBD Files In Scope."""

import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
rows = []
for r in data["results"]:
    props = r["properties"]

    def _rt(key):
        arr = props.get(key, {}).get("rich_text", [])
        return arr[0]["plain_text"] if arr else ""

    def _title(key):
        arr = props.get(key, {}).get("title", [])
        return arr[0]["plain_text"] if arr else ""

    rows.append(
        {
            "id": r["id"],
            "title": _title("Phase Title"),
            "phase": _rt("Phase ID"),
            "wave": _rt("Wave ID"),
            "plan": _rt("Plan File"),
            "priority": props.get("Priority", {}).get("number"),
            "blocking": _rt("Blocking Items"),
            "tokens": props.get("Est Tokens", {}).get("number"),
            "files": _rt("Files In Scope"),
        }
    )

print(f"TOTAL ROWS: {len(rows)}\n")
for i, r in enumerate(rows, 1):
    pri = r["priority"] if r["priority"] is not None else "--"
    print(f"{i:2}. [P{pri}] {r['wave']}.{r['phase']} ({r['tokens']}t) plan={r['plan']}")
    print(f"    title: {r['title']}")
    print(f"    files: {r['files'][:100]}")
    print(f"    block: {r['blocking'][:180]}")
    print(f"    id: {r['id']}")
    print()
