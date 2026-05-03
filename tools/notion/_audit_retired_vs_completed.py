"""Reclassify the 53 Retired Plans rows: was the scope DELIVERED (Completed)
or ABANDONED (true Retired)?

User's distinction (2026-05-03):
  - Retired  = scope considered then abandoned, no work done
  - Completed = work finished (even if under a different plan name)

Heuristic on existing Summary field:
  STRONG_DELIVERED — explicit successor named that landed the work
                     ("Folded into X", "Superseded by X" where X is shipped),
                     "gate already shipped", "ratcheting gate owns no-regression",
                     "decomposed into per-wave children" (parent done structurally)
  STRONG_ABANDONED — "stale by design", "never kicked off", "Draft never started",
                     "recreate fresh if scoped up", "stale since YYYY-MM-DD"
                     with no successor
  AMBIGUOUS_FILE_GONE — plan file deleted, summary doesn't say work landed
                     elsewhere (could be either)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DUMP = Path(sys.argv[1] if len(sys.argv) > 1 else
    "C:/Users/amita/AppData/Local/Temp/windsurf/mcp_output_4570bbeb1534c8d5.txt")

DELIVERED_MARKERS = (
    "folded into",
    "superseded by",
    "merged into",
    "absorbed",
    "explicitly listed in",
    "supersedes table",
    "decomposed into",
    "gate already shipped",
    "shipped strict-by-default",
    "ratcheting gate owns",
    "ci gate",
    "live verification",
    "violations=0",
    "no-regression invariant",
    "completes apps_",
    "either landed",
    "have either landed",
)

ABANDONED_MARKERS = (
    "stale by design",
    "never kicked off",
    "never started",
    "draft, never",
    "recreate fresh if scoped up",
    "awaiting /plan kick-off",
    "do not implement yet",
    "todo backlog framing retired",
    "stale-by-design",
    "all 17 phases still todo",
)

FILE_MISSING = re.compile(r"plan file (is )?(missing|deleted) from disk", re.I)


def classify(slug: str, summary: str) -> tuple[str, str]:
    s = summary.lower()
    file_gone = bool(FILE_MISSING.search(summary))

    # First, did the work demonstrably land?
    delivered_hits = [m for m in DELIVERED_MARKERS if m in s]
    abandoned_hits = [m for m in ABANDONED_MARKERS if m in s]

    # Combined signal: BOTH a successor AND abandonment language → mixed,
    # but successor wins because that's the primary "did work happen" signal.
    if delivered_hits:
        # Filter false positive: "abandoned" hint stronger if explicit
        if any(m in s for m in ("stale by design", "never kicked off",
                                "never started", "do not implement yet")):
            return ("MIXED", f"delivered+abandoned: {delivered_hits[:2]} / {abandoned_hits[:2]}")
        return ("DELIVERED", f"signal: {delivered_hits[:2]}")

    if abandoned_hits:
        return ("ABANDONED", f"signal: {abandoned_hits[:2]}")

    if file_gone:
        return ("AMBIGUOUS_FILE_GONE", "plan file deleted, summary lacks delivery signal")

    return ("UNCLEAR", "no strong markers either way")


def main() -> int:
    data = json.loads(DUMP.read_text(encoding="utf-8"))
    rows = data["results"]
    buckets: dict[str, list] = {"DELIVERED": [], "ABANDONED": [],
                                 "MIXED": [], "AMBIGUOUS_FILE_GONE": [], "UNCLEAR": []}
    for r in rows:
        props = r["properties"]
        title = props["Slug"]["title"]
        slug = title[0]["plain_text"] if title else "(no-slug)"
        summary = "".join(c["plain_text"] for c in props["Summary"]["rich_text"])
        page_id = r["id"]
        verdict, reason = classify(slug, summary)
        buckets[verdict].append((slug, page_id, reason, summary[:140]))

    print(f"Total Retired rows analyzed: {len(rows)}")
    print()
    for k, items in buckets.items():
        print(f"{k}: {len(items)}")
    print()

    if buckets["DELIVERED"]:
        print("--- DELIVERED (likely should be Completed, not Retired) ---")
        for slug, _pid, reason, summ in buckets["DELIVERED"]:
            print(f"  {slug}")
            print(f"      reason: {reason}")
            print(f"      summary: {summ}")
        print()

    if buckets["MIXED"]:
        print("--- MIXED (successor named AND abandonment language) ---")
        for slug, _pid, reason, summ in buckets["MIXED"]:
            print(f"  {slug}")
            print(f"      {reason}")
        print()

    if buckets["AMBIGUOUS_FILE_GONE"]:
        print("--- AMBIGUOUS (file gone, no delivery signal) ---")
        for slug, _pid, reason, summ in buckets["AMBIGUOUS_FILE_GONE"]:
            print(f"  {slug}")
        print()

    if buckets["ABANDONED"]:
        print("--- ABANDONED (true Retired) ---")
        for slug, _pid, reason, _ in buckets["ABANDONED"]:
            print(f"  {slug}  ({reason})")
        print()

    if buckets["UNCLEAR"]:
        print("--- UNCLEAR ---")
        for slug, _pid, _, summ in buckets["UNCLEAR"]:
            print(f"  {slug}")
            print(f"      summary: {summ}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
