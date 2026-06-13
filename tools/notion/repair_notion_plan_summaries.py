#!/usr/bin/env python3
"""Repair all Plans DB rows that have garbage Summary / AI Summary content.

Garbage detection:
- AI Summary contains '---' OR newlines OR is longer than 100 chars
- Summary starts with 'plan_id:', '**Tier**:', 'Status: Draft', or '---'

For each garbage row: read the on-disk plan file, re-extract clean summaries
using the fixed extractors, and PATCH the Notion page.

Usage:
    python tools/notion/repair_notion_plan_summaries.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
)

PLANS_DIR = REPO_ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
TIMEOUT = 30.0
_WORD_CAP_AI = 12


def _token() -> str:
    t = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY", "")
    if not t:
        sys.exit("ERROR: set NOTION_TOKEN or NOTION_API_KEY")
    return t


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_token()}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }


def _req(method: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def _query_all_pages() -> list[dict]:
    url = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
    pages: list[dict] = []
    cursor = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        result = _req("POST", url, body)
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
        time.sleep(0.3)
    return pages


def _extract_summary(md_text: str, max_chars: int = 200) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("---") or s.startswith("**Slug**") or s.startswith("**Status**"):
            continue
        if re.match(r"^(plan_id|plan_type|Status|Owner|Scope|ADG snapshot|Created):", s):
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"^\*\*.*?\*\*:?\s*", "", s)
        if not s:
            continue
        if len(s) > max_chars:
            s = s[: max_chars - 1] + "\u2026"
        return s
    return "(legacy plan, summary not extracted)"


def _extract_ai_summary(md_text: str) -> str:
    m = re.search(r"^##\s+AI\s+Summary\s*$", md_text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        for line in md_text[m.end():].splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                break
            s = re.sub(r"^[-*]\s+", "", s)
            if s:
                words = s.split()
                return " ".join(words[:_WORD_CAP_AI]) + ("\u2026" if len(words) > _WORD_CAP_AI else "")
    m2 = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
    if m2:
        words = m2.group(1).strip().split()
        return " ".join(words[:_WORD_CAP_AI]) + ("\u2026" if len(words) > _WORD_CAP_AI else "")
    return "Legacy plan; see Plan File Path for detail."


def _is_garbage(text: str) -> bool:
    if not text:
        return False
    return (
        "---" in text
        or "\n" in text
        or len(text) > 100
        or text.startswith("plan_id:")
        or text.startswith("**Tier**")
        or text.startswith("Status: Draft")
        or text.startswith("- ")
        or text.startswith("* ")
    )


def _rich_text_val(prop: dict) -> str:
    chunks = prop.get("rich_text", [])
    return "".join(c.get("plain_text", "") for c in chunks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Fetching all Plans DB rows…")
    pages = _query_all_pages()
    print(f"  {len(pages)} rows found")

    garbage_rows = []
    for page in pages:
        props = page.get("properties", {})
        ai_val = _rich_text_val(props.get("AI Summary ", {}))
        sum_val = _rich_text_val(props.get("Summary", {}))
        slug_chunks = props.get("Slug", {}).get("title", [])
        slug = "".join(c.get("plain_text", "") for c in slug_chunks)
        file_path_val = _rich_text_val(props.get("Plan File Path", {}))

        if _is_garbage(ai_val) or _is_garbage(sum_val):
            garbage_rows.append({
                "page_id": page["id"],
                "slug": slug,
                "file_path": file_path_val,
                "ai_current": ai_val[:80],
                "sum_current": sum_val[:80],
            })

    print(f"\n{len(garbage_rows)} garbage rows detected:\n")
    for r in garbage_rows:
        print(f"  [{r['slug']}]")
        print(f"    AI : {r['ai_current']!r}")
        print(f"    Sum: {r['sum_current']!r}")

    if not garbage_rows:
        print("Nothing to fix.")
        return

    patched = 0
    skipped = 0
    for r in garbage_rows:
        slug = r["slug"]
        file_path = r["file_path"] or f"docs/archive/windsurf/legacy-tree/plans/{slug}.md"
        plan_file = REPO_ROOT / file_path.lstrip("/")
        if not plan_file.exists():
            plan_file = PLANS_DIR / f"{slug}.md"
        if not plan_file.exists():
            print(f"  SKIP {slug} — plan file not found")
            skipped += 1
            continue

        md = plan_file.read_text(encoding="utf-8", errors="replace")
        new_ai = _extract_ai_summary(md)
        new_sum = _extract_summary(md)

        print(f"\n  PATCH {slug}")
        print(f"    AI  → {new_ai!r}")
        print(f"    Sum → {new_sum!r}")

        if args.dry_run:
            continue

        patch_url = f"{NOTION_BASE}/pages/{r['page_id']}"
        payload = {
            "properties": {
                "Summary": {"rich_text": [{"text": {"content": new_sum}}]},
                "AI Summary ": {"rich_text": [{"text": {"content": new_ai}}]},
            }
        }
        try:
            _req("PATCH", patch_url, payload)
            patched += 1
            time.sleep(0.35)
        except urllib.error.HTTPError as e:
            print(f"    ERROR {e.code}: {e.read().decode()[:200]}")
            skipped += 1

    print(f"\nDone. patched={patched} skipped={skipped} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
