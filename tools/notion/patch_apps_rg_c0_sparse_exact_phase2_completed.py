#!/usr/bin/env python3
"""One-shot: PATCH Notion Plans row — apps-rg-c0-sparse-exact-phase2-d2f8a1 → Completed.

Run from repo root with NOTION_TOKEN (or NOTION_API_KEY) set.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402

PAGE_ID = "36127693-f55c-81c0-b56f-d455590ee9be"
EXPECTED_SLUG = "apps-rg-c0-sparse-exact-phase2-d2f8a1"
TIMEOUT = 30.0

SUMMARY = (
    "Phase 2 sparse/exact C0 lane: core seam (c0_sparse_exact_seam, bm25_store "
    "profile-driven index), apps_rg c0_binding merge + 5-tuple retrieval, "
    "section_retrieval_profile toggles, contract tests. W5 (sparse CI gate) "
    "deferred optional."
)

# Plans DB: ≤12 words, one sentence — richer detail lives in Summary (notion-plans-taxonomy).
AI_SUMMARY = (
    "Ships apps_rg C0 sparse lane behind generic core seam plus profile toggles."
)


def _page_slug(props: dict) -> str | None:
    slug_prop = props.get("Slug") or {}
    parts: list[str] = []
    for blk in slug_prop.get("title") or []:
        if isinstance(blk, dict):
            t = blk.get("plain_text") or (blk.get("text") or {}).get("content", "")
            if isinstance(t, str):
                parts.append(t)
    out = "".join(parts).strip()
    return out if out else None


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN (or NOTION_API_KEY) not set", file=sys.stderr)
        return 2

    hdr = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        f"{NOTION_BASE}/pages/{PAGE_ID}",
        headers=hdr,
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            pg = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8", errors="replace")[:500], file=sys.stderr)
        return 1

    actual = _page_slug(pg.get("properties") or {})
    if actual is not None and actual != EXPECTED_SLUG:
        print(
            f"ABORT: slug mismatch expected={EXPECTED_SLUG!r} actual={actual!r}",
            file=sys.stderr,
        )
        return 3

    payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:1990]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:1990]}}]},
        }
    }
    body = json.dumps(payload).encode("utf-8")
    preq = urllib.request.Request(
        f"{NOTION_BASE}/pages/{PAGE_ID}",
        data=body,
        headers=hdr,
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(preq, timeout=TIMEOUT) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8", errors="replace")[:500], file=sys.stderr)
        return 1

    slug_note = actual if actual else "(no Slug on page)"
    print(f"Patched Notion page {PAGE_ID} Status=Completed (slug check: {slug_note})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
