"""Generate AI Summary candidates for Retired Plans rows.

Reads the dump from query-data-source(Status=Retired) and emits a JSON
mapping page_id -> {slug, ai_summary, why} for the operator to apply via
API-patch-page in sequence.

Heuristic: parse Summary for "Folded into X" / "Superseded by X" /
"replaced by X" / "decomposed into" markers and produce a one-line
≤ 14-word descriptor. Fall back to a generic "stale orphan" line when
Summary says the plan file is missing from disk.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DUMP = Path(sys.argv[1] if len(sys.argv) > 1 else
    "C:/Users/amita/AppData/Local/Temp/windsurf/mcp_output_4570bbeb1534c8d5.txt")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else
    "artifacts/notion/retired_ai_summaries.json")

_SUCCESSOR_PATTERNS = [
    re.compile(r"folded into\s+([a-z0-9-]+)", re.I),
    re.compile(r"superseded by\s+([a-z0-9-]+)", re.I),
    re.compile(r"replaced by\s+([a-z0-9-]+)", re.I),
    re.compile(r"decomposed into\s+(\d+)\s+per-wave", re.I),
    re.compile(r"merged into\s+([a-z0-9-]+)", re.I),
]

_FILE_MISSING = re.compile(r"plan file (is )?missing from disk", re.I)
_STALE_NO_EDITS = re.compile(r"stale since\s+([0-9-]+)", re.I)


def _strip_short_slug(slug: str) -> str:
    """Drop trailing 6-hex id from slug for human readability."""
    return re.sub(r"-[0-9a-f]{6,}$", "", slug)


def make_summary(slug: str, summary_text: str) -> str:
    """Return a ≤ 14-word AI Summary. Heuristic, deterministic."""
    text = summary_text.strip()
    short = _strip_short_slug(slug)

    # Successor-named pattern
    for pat in _SUCCESSOR_PATTERNS:
        m = pat.search(text)
        if m:
            target = m.group(1)
            if pat.pattern.startswith("decomposed"):
                count = target
                return f"Aggregator retired; decomposed into {count} per-wave child plans."
            target_short = _strip_short_slug(target)
            return f"Retired; superseded by {target_short}."

    # Plan file missing
    if _FILE_MISSING.search(text):
        return f"Stale orphan: plan file deleted from disk; Notion row was lagging."

    # Stale by inactivity
    m = _STALE_NO_EDITS.search(text)
    if m:
        return f"Retired stale (no edits since {m.group(1)}); recreate fresh if scoped up."

    # Generic fallback — pull first 12 words of summary
    words = re.findall(r"\S+", text)
    head = " ".join(words[:12])
    return f"Retired: {head}"[:120]


def main() -> int:
    data = json.loads(DUMP.read_text(encoding="utf-8"))
    rows = data["results"]
    out: list[dict] = []
    for r in rows:
        props = r["properties"]
        title = props["Slug"]["title"]
        slug = title[0]["plain_text"] if title else "(no-slug)"
        summary = "".join(c["plain_text"] for c in props["Summary"]["rich_text"])
        ai = make_summary(slug, summary)
        out.append({"page_id": r["id"], "slug": slug, "ai_summary": ai,
                    "word_count": len(ai.split())})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print preview table
    over = [r for r in out if r["word_count"] > 14]
    print(f"Generated {len(out)} AI Summary candidates -> {OUT}")
    print(f"  over 14 words: {len(over)} (will still post; advisory soft-cap)")
    print()
    for r in out[:8]:
        print(f"  [{r['word_count']:2}w] {r['slug']}")
        print(f"         {r['ai_summary']}")
    print(f"  ... and {len(out) - 8} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
