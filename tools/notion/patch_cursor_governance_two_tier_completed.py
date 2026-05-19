#!/usr/bin/env python3
"""PATCH Notion Plans row — cursor-governance-two-tier-b4e8f2 → Completed (W0–W5 + W3R)."""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE, PLANS_DATA_SOURCE_ID, query_url  # noqa: E402

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none  # noqa: E402

EXPECTED_SLUG = "cursor-governance-two-tier-b4e8f2"
TIMEOUT = 30.0

SUMMARY = (
    "COMPLETED — Cursor governance two-tier consolidation (Option A). "
    "W0 measurement; W1 4×alwaysApply + AGENTS 9KB; W2 dedupe triples 8→0; "
    "W3 dispatcher + 490 plans archived; W3R graph orphans 507→0; "
    "W4 skill-description gate + mcp-integration index split; W5 closeout on disk. "
    "Follow-up: 10C proof bundles HEAD resync (198 files). "
    "Closeout: docs/reports/cursor/governance_two_tier_closeout.md"
)

AI_SUMMARY = (
    "COMPLETED Option A. Tier-1 18460B / 4 rules. Active plans 10. "
    "Receipts under docs/reports/cursor/. Not runtime RAG. "
    "Out of scope: native-config Windsurf refs; full contract gates if 10C drifts again."
)

MARKERS = """\
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=0 note="Tier-1 measurement + inventory"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=1 note="Option A: 4x alwaysApply; AGENTS ~9KB"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=2 note="Cluster dedupe; duplicate triples 8→0"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=3 note="Dispatcher hook; 490 plans archived"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=3 note="W3R: baseline orphans 507→0"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=4 note="Skill hygiene gate; mcp-integration indexed"
WAVE_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 wave=5 note="Closeout manifest + md"
PLAN_COMPLETE: plan=cursor-governance-two-tier-b4e8f2 note="Two-tier governance Option A closed"
"""


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


def _find_page_id(token: str) -> str | None:
    payload = {
        "filter": {
            "property": "Slug",
            "title": {"equals": EXPECTED_SLUG},
        },
        "page_size": 1,
    }
    body = json.dumps(payload).encode("utf-8")
    hdr = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(query_url(PLANS_DATA_SOURCE_ID), data=body, headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    results = data.get("results") or []
    if not results:
        return None
    return results[0].get("id")


def main() -> int:
    token = get_notion_bearer_token_or_none()
    if not token:
        print("ERROR: NOTION_TOKEN not set", file=sys.stderr)
        return 2

    page_id = _find_page_id(token)
    if not page_id:
        print(f"ERROR: Plans row not found for slug={EXPECTED_SLUG!r}", file=sys.stderr)
        return 1

    hdr = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(f"{NOTION_BASE}/pages/{page_id}", headers=hdr)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        pg = json.loads(resp.read().decode("utf-8"))
    actual = _page_slug(pg.get("properties") or {})
    if actual is not None and actual != EXPECTED_SLUG:
        print(f"ABORT: slug mismatch expected={EXPECTED_SLUG!r} actual={actual!r}", file=sys.stderr)
        return 3

    patch_payload = {
        "properties": {
            "Status": {"select": {"name": "Completed"}},
            "Summary": {"rich_text": [{"text": {"content": SUMMARY[:1990]}}]},
            "AI Summary ": {"rich_text": [{"text": {"content": AI_SUMMARY[:1990]}}]},
            "Exists On Disk": {"checkbox": True},
        }
    }
    preq = urllib.request.Request(
        f"{NOTION_BASE}/pages/{page_id}",
        data=json.dumps(patch_payload).encode("utf-8"),
        headers=hdr,
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(preq, timeout=TIMEOUT) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8", errors="replace")[:800], file=sys.stderr)
        return 1

    print(f"Patched Notion page {page_id} Status=Completed slug={actual or EXPECTED_SLUG}")

    # Append wave logs via lifecycle writer (best-effort)
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "notion" / "wave_lifecycle_writer.py"), "--emit-from-stdin"],
        input=MARKERS,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
    else:
        print(proc.stderr or proc.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
