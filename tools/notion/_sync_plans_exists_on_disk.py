"""Reconcile Notion Plans 'Exists On Disk' checkbox against actual filesystem.

For every row in the Plans data source, compare the boolean Notion field
'Exists On Disk' to the existence of the file at 'Plan File Path'. PATCH
mismatches in either direction:
  - Notion=true, file gone   -> set false
  - Notion=false, file there -> set true

Direct REST, single subprocess. Idempotent.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"  # Plans
_NOTION_VERSION = "2025-09-03"


def _token() -> str | None:
    return os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")


def _query_all(token: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"https://api.notion.com/v1/data_sources/{_DATA_SOURCE_ID}/query",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": _NOTION_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            page = json.loads(resp.read().decode("utf-8"))
        rows.extend(page["results"])
        if not page.get("has_more"):
            break
        cursor = page.get("next_cursor")
    return rows


def _patch_exists(token: str, page_id: str, exists: bool) -> None:
    payload = {"properties": {"Exists On Disk": {"checkbox": exists}}}
    req = urllib.request.Request(
        f"https://api.notion.com/v1/pages/{page_id}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": _NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def _extract_path(props: dict) -> str:
    rt = props.get("Plan File Path", {}).get("rich_text", [])
    return "".join(c.get("plain_text", "") for c in rt).strip()


def _extract_slug(props: dict) -> str:
    title = props.get("Slug", {}).get("title", [])
    return title[0]["plain_text"] if title else ""


def _resolve_to_disk(plan_path: str, slug: str) -> Path | None:
    """Try several candidate paths and return the first that exists."""
    candidates: list[Path] = []
    if plan_path:
        p = (REPO / plan_path).resolve()
        candidates.append(p)
    # Fallback: glob by slug under .windsurf/plans/
    plans_dir = REPO / ".windsurf" / "plans"
    if slug:
        for match in plans_dir.glob(f"{slug}*.md"):
            candidates.append(match)
    for c in candidates:
        if c.is_file():
            return c
    return None


def main() -> int:
    token = _token()
    if not token:
        print("ERROR: NOTION_API_KEY / NOTION_TOKEN not set")
        return 2

    rows = _query_all(token)
    print(f"Loaded {len(rows)} Plans rows")

    fixed_to_false = []  # Notion said true, file actually gone
    fixed_to_true = []   # Notion said false, file actually present
    ok_match = 0
    missing_path = 0

    for r in rows:
        props = r["properties"]
        slug = _extract_slug(props)
        path = _extract_path(props)
        notion_exists = bool(props.get("Exists On Disk", {}).get("checkbox"))
        page_id = r["id"]
        if not path and not slug:
            missing_path += 1
            continue
        actual = _resolve_to_disk(path, slug)
        actual_exists = actual is not None
        if actual_exists == notion_exists:
            ok_match += 1
            continue
        if notion_exists and not actual_exists:
            fixed_to_false.append((slug, path, page_id))
        else:
            fixed_to_true.append((slug, path, page_id, str(actual) if actual else ""))

    print()
    print(f"Match (no fix needed):           {ok_match}")
    print(f"Need fix true -> false (stale):  {len(fixed_to_false)}")
    print(f"Need fix false -> true (stale):  {len(fixed_to_true)}")
    print(f"Missing path AND slug (skipped): {missing_path}")
    print()

    failed = 0
    for slug, path, page_id in fixed_to_false:
        try:
            _patch_exists(token, page_id, False)
            print(f"  -> false: {slug} (path={path or '(none)'})")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:200]
            print(f"  FAIL  {slug}: HTTP {exc.code} {body}")
            failed += 1
        time.sleep(0.12)

    for slug, path, page_id, actual in fixed_to_true:
        try:
            _patch_exists(token, page_id, True)
            print(f"  -> true:  {slug} (resolved={actual})")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:200]
            print(f"  FAIL  {slug}: HTTP {exc.code} {body}")
            failed += 1
        time.sleep(0.12)

    print()
    print(f"Done: fixed={len(fixed_to_false) + len(fixed_to_true) - failed} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
