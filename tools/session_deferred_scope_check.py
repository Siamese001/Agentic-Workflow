"""One-off: audit this-chat DEFERRED_SCOPE markers vs. Notion posts."""
from __future__ import annotations
import json
from pathlib import Path

LOG = Path("artifacts/windsurf/deferred_scope_capture.jsonl")

# Plan slugs used by markers emitted during this chat session
SESSION_SLUGS = [
    "prompt-assembly-reception-hardening-9c4e2b",  # W5b.1, W5b.2 emitted during W5 close
    "prompt-reception-followups-a7b3c4",            # final 9-row plan
    "hook-tty-guard-rollout",                       # RCA response HOOK1.1
]

found: dict[str, list[dict]] = {s: [] for s in SESSION_SLUGS}
other_today: list[dict] = []

with LOG.open(encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "2026-04-23" not in rec.get("timestamp", ""):
            continue
        plan = rec.get("marker", {}).get("plan", "") or ""
        matched = False
        for slug in SESSION_SLUGS:
            if slug in plan:
                found[slug].append(rec)
                matched = True
                break
        if not matched:
            other_today.append(rec)

for slug, lst in found.items():
    print(f"=== {slug} ===")
    print(f"  entries: {len(lst)}")
    for r in lst:
        kind = r.get("kind", "?")
        m = r.get("marker", {})
        phase = m.get("phase", "?")
        band = r.get("band", "?")
        page = r.get("notion_page_id", "")
        print(f"  [{kind}] phase={phase} band={band} page={page}")
    print()

print(f"=== other today ({len(other_today)}) ===")
for r in other_today:
    kind = r.get("kind", "?")
    m = r.get("marker", {})
    plan = m.get("plan", "?")
    phase = m.get("phase", "?")
    print(f"  [{kind}] plan={plan} phase={phase}")
