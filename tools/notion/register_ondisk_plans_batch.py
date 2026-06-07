#!/usr/bin/env python3
"""W1 extension — batch-register on-disk plan files into the Plans DB.

Reads `artifacts/cursor/backlog_plan_linkage_misses.jsonl`, extracts unique
slugs whose on-disk plan file exists at `docs/archive/windsurf/legacy-tree/plans/<slug>.md`, and posts
one Plans DB row per slug with Slug (title) / Status=Not Started / Exists On Disk=true /
Plan File Path / Summary / AI Summary.

Idempotent: queries Plans DB by Slug-equals before posting; skips existing.
Fail-open per row.

Flags:
  --dry-run    Compute but do not POST.
  --limit N    Process at most N slugs (debug).
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
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    NOTION_POST_URL,
    PLANS_DATA_SOURCE_ID,
    PLANS_DB_ID,
)

# RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B: shared dedup helper.
from tools.notion._plan_registration_helpers import (  # noqa: E402
    register_plan_idempotent,
)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

MISS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "backlog_plan_linkage_misses.jsonl"
PLANS_DIR = REPO_ROOT / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
PLANS_QUERY_URL = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
RESULT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "register_ondisk_plans_results.jsonl"
TIMEOUT = 30.0
THROTTLE_S = 0.35


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not tok:
        print("ERROR: set NOTION_TOKEN or NOTION_API_KEY", file=sys.stderr)
        sys.exit(1)
    return tok


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


# Dedup logic moved to tools/notion/_plan_registration_helpers.py
# (RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B). All Plans-DB POSTs
# now route through register_plan_idempotent for shared dedup + telemetry.


def _extract_summary(md_text: str, max_chars: int = 200) -> str:
    """First non-header, non-blank line of content, capped to max_chars."""
    for line in md_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("---") or s.startswith("**Slug**") or s.startswith("**Status**"):
            continue
        # Strip leading bullet/bold markers for a clean sentence
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"^\*\*.*?\*\*:?\s*", "", s)
        if not s:
            continue
        if len(s) > max_chars:
            s = s[: max_chars - 1] + "\u2026"
        return s
    return "(legacy plan, summary not extracted)"


_WORD_CAP_AI = 12


def _extract_ai_summary(md_text: str) -> str:
    """First line of `## AI Summary` section, hard-capped at _WORD_CAP_AI words."""
    m = re.search(r"^##\s+AI\s+Summary\s*$", md_text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        for line in md_text[m.end():].splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                break
            # Strip leading bullet marker
            s = re.sub(r"^[-*]\s+", "", s)
            if s:
                words = s.split()
                return " ".join(words[:_WORD_CAP_AI]) + ("\u2026" if len(words) > _WORD_CAP_AI else "")
    # Fallback: slug-derived terse description
    m2 = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
    if m2:
        words = m2.group(1).strip().split()
        return " ".join(words[:_WORD_CAP_AI]) + ("\u2026" if len(words) > _WORD_CAP_AI else "")
    return "Legacy plan; see Plan File Path for detail."


def _build_payload(slug: str, plan_path: Path) -> dict:
    md = plan_path.read_text(encoding="utf-8", errors="replace")
    summary = _extract_summary(md)
    ai_summary = _extract_ai_summary(md)
    return {
        "parent": {"type": "database_id", "database_id": PLANS_DB_ID},
        "properties": {
            "Slug": {"title": [{"text": {"content": slug}}]},
            "Status": {"select": {"name": "Not Started"}},
            "Exists On Disk": {"checkbox": True},
            "Plan File Path": {"rich_text": [{"text": {"content": f"docs/archive/windsurf/legacy-tree/plans/{slug}.md"}}]},
            "Summary": {"rich_text": [{"text": {"content": summary}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": ai_summary}}]},
        },
    }


# _post() removed; use register_plan_idempotent() instead.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    token = _token()

    if not MISS_LOG.exists():
        print(f"ERROR: miss log not found: {MISS_LOG}", file=sys.stderr)
        return 1

    slugs: set[str] = set()
    for line in MISS_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            slugs.add(rec.get("slug", ""))
        except json.JSONDecodeError:
            continue

    on_disk = []
    for slug in sorted(slugs):
        if not slug:
            continue
        path = PLANS_DIR / f"{slug}.md"
        if path.exists():
            on_disk.append((slug, path))

    print(f"Unique slugs in miss log:        {len(slugs)}", file=sys.stderr)
    print(f"Slugs with on-disk plan file:    {len(on_disk)}", file=sys.stderr)

    if args.limit is not None:
        on_disk = on_disk[: args.limit]
        print(f"Limited to:                      {len(on_disk)}", file=sys.stderr)

    today_iso = date.today().isoformat()
    posted = 0
    skipped_existing = 0
    failed = 0

    if not args.dry_run:
        RESULT_LOG.parent.mkdir(parents=True, exist_ok=True)

    bar = tqdm(on_disk, desc="Registering", unit="plan", colour="magenta")
    for slug, path in bar:
        payload = _build_payload(slug, path)
        result = register_plan_idempotent(
            slug,
            payload["properties"],
            token=token,
            dry_run=args.dry_run,
            writer="register_ondisk_plans_batch.py",
        )

        rec = {
            "ts": today_iso,
            "slug": slug,
            "plan_path": str(path.relative_to(REPO_ROOT)),
            "action": result.action,
            "page_id": result.page_id,
            "detail": result.detail,
        }
        with RESULT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")

        if result.action == "created":
            posted += 1
        elif result.action == "existed":
            skipped_existing += 1
            tqdm.write(f"SKIP {slug}: already registered (page_id={result.page_id})")
        elif result.action == "dry_run":
            posted += 1
        elif result.action == "duplicate_blocked":
            failed += 1
            tqdm.write(f"BLOCKED {slug}: {result.detail}")
        else:  # api_error / no_token
            failed += 1
            tqdm.write(f"FAIL {slug}: {result.action} {result.detail}")
        time.sleep(THROTTLE_S)

    print(
        f"\nDone. posted={posted} skipped_existing={skipped_existing} "
        f"failed={failed} (dry_run={args.dry_run})",
        file=sys.stderr,
    )
    if not args.dry_run:
        print(f"Results: {RESULT_LOG}", file=sys.stderr)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
