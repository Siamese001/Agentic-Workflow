#!/usr/bin/env python3
"""
snapshot_renderer.py — W4 of notion-backlog-schema-refactor-7c3d9e.

Renders a compact "Backlog Snapshot" page on Notion that Cascade can retrieve
with ONE API call instead of paginating 220 rows. The page contains:
  - Band distribution counts (P0..P5, UNSCORED)
  - Top 25 open items by Impact Score (P1 + P2 only)
  - Stale-item warnings (P-Band null rows)

The page lives alongside Wave/Phase Convergence and Plans under parent page
33f27693-f55c-8134-9041-d34b6dc11425.

Usage:
    # First time — create the page and print its ID for reuse:
    python tools/notion/snapshot_renderer.py --create-page

    # Every subsequent regenerate:
    python tools/notion/snapshot_renderer.py --regenerate

The page ID is persisted to tools/notion/.snapshot_page_id.

Idempotent regenerate: deletes all children under the page, appends a single
code-block-and-toggle-free markdown rendering. Target size ≤5 KB.

No hardcoded secrets. NOTION_TOKEN resolved from env or .env.
Subprocess-free. Uses only urllib.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
BACKLOG_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
PARENT_PAGE_ID = "33f27693-f55c-8134-9041-d34b6dc11425"

REPO_ROOT = Path(__file__).resolve().parents[2]
PAGE_ID_FILE = REPO_ROOT / "tools" / "notion" / ".snapshot_page_id"
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "notion_snapshot_audit.jsonl"

TOP_N = 25


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN")
    if tok:
        return tok
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 2:
                time.sleep(int(err.headers.get("Retry-After", "2")))
                continue
            body_txt = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {body_txt}") from err
        except urllib.error.URLError as err:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error: {err}") from err
    raise RuntimeError(f"Exhausted retries: {method} {url}")


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_backlog_rows(tok: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST", f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}/query", tok, body)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return rows


def _pband(row: dict) -> str:
    sel = row["properties"].get("P-Band", {}).get("select")
    return sel["name"] if sel else "UNSCORED"


def _impact(row: dict) -> float | None:
    return row["properties"].get("Impact Score", {}).get("number")


def _layer(row: dict) -> str:
    sel = row["properties"].get("Layer", {}).get("select")
    return sel["name"] if sel else "-"


def _surface(row: dict) -> str:
    sel = row["properties"].get("Surface", {}).get("select")
    return sel["name"] if sel else "-"


def _status(row: dict) -> str:
    sel = row["properties"].get("Status", {}).get("select")
    return sel["name"] if sel else "-"


def _title(row: dict) -> str:
    t = row["properties"].get("Phase Title", {}).get("title", [])
    return "".join(x.get("plain_text", "") for x in t)


def _plan_file(row: dict) -> str:
    rt = row["properties"].get("Plan File", {}).get("rich_text", [])
    return "".join(x.get("plain_text", "") for x in rt)


def build_markdown(rows: list[dict]) -> str:
    """Compose the snapshot markdown body. Kept deliberately compact."""
    open_rows = [r for r in rows if _status(r) not in ("Done", "Complete", "Descoped")]
    bands: collections.Counter[str] = collections.Counter(_pband(r) for r in open_rows)
    all_bands: collections.Counter[str] = collections.Counter(_pband(r) for r in rows)

    # Top-N by impact, P1+P2 only, open only
    scored = [r for r in open_rows if _pband(r) in ("P1", "P2") and _impact(r) is not None]
    scored.sort(key=lambda r: _impact(r) or 0.0, reverse=True)
    top = scored[:TOP_N]

    stale = [r for r in open_rows if _pband(r) == "UNSCORED" and _status(r) == "Todo"]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Source:** Wave/Phase Convergence (`{BACKLOG_DS_ID[:8]}...`)")
    lines.append(
        f"**Total rows:** {len(rows)} | **Open:** {len(open_rows)} | **Stale (UNSCORED Todo):** {len(stale)}"
    )
    lines.append("")
    lines.append("## Band distribution (open only)")
    for b in ("P0", "P1", "P2", "P3", "P4", "P5", "UNSCORED"):
        lines.append(f"- **{b}**: {bands.get(b, 0)} open / {all_bands.get(b, 0)} total")
    lines.append("")
    lines.append(f"## Top {TOP_N} open P1+P2 by impact")
    lines.append("")
    lines.append("| # | Band | Impact | Layer | Surface | Phase |")
    lines.append("|---|------|--------|-------|---------|-------|")
    for i, r in enumerate(top, 1):
        title = _title(r)[:70].replace("|", "/")
        lines.append(f"| {i} | {_pband(r)} | {_impact(r):.1f} | {_layer(r)} | {_surface(r)} | {title} |")
    lines.append("")
    lines.append("## Maintenance")
    lines.append(f"- {len(stale)} open rows are UNSCORED (no `[Pn]` prefix; scorer needed)")
    lines.append("- Regenerate via `python tools/notion/snapshot_renderer.py --regenerate`")
    return "\n".join(lines)


def _paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _heading(text: str, level: int = 2) -> dict:
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _code_block(text: str) -> dict:
    # Notion blocks cap text at ~2000 chars; split if needed
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": "markdown",
            "rich_text": [{"type": "text", "text": {"content": text[:1999]}}],
        },
    }


def render_blocks(md: str) -> list[dict]:
    """Return Notion block objects. Uses a single markdown code block to
    preserve the compact table layout and keep parser complexity low."""
    # Split into ~1900-char chunks if large (Notion 2000-char per rich_text)
    chunks: list[str] = []
    remaining = md
    while remaining:
        chunks.append(remaining[:1900])
        remaining = remaining[1900:]
    blocks: list[dict] = [_heading("Backlog Snapshot", 1)]
    for chunk in chunks:
        blocks.append(_code_block(chunk))
    return blocks


def create_snapshot_page(tok: str) -> str:
    body = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "properties": {"title": [{"type": "text", "text": {"content": "Backlog Snapshot"}}]},
        "children": [_paragraph("Snapshot page — regenerated by tools/notion/snapshot_renderer.py")],
    }
    resp = _http("POST", f"{NOTION_API}/pages", tok, body)
    return resp["id"]


def clear_page_children(tok: str, page_id: str) -> None:
    # Delete all existing children
    cursor: str | None = None
    while True:
        url = f"{NOTION_API}/blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        resp = _http("GET", url, tok)
        for blk in resp.get("results", []):
            _http("DELETE", f"{NOTION_API}/blocks/{blk['id']}", tok)
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")


def append_children(tok: str, page_id: str, blocks: list[dict]) -> None:
    # Notion caps appends at 100 children per call
    for i in range(0, len(blocks), 100):
        _http("PATCH", f"{NOTION_API}/blocks/{page_id}/children", tok, {"children": blocks[i : i + 100]})


def regenerate(tok: str, page_id: str) -> dict:
    t0 = time.time()
    rows = fetch_backlog_rows(tok)
    md = build_markdown(rows)
    blocks = render_blocks(md)
    clear_page_children(tok, page_id)
    append_children(tok, page_id, blocks)
    elapsed = time.time() - t0
    return {
        "page_id": page_id,
        "rows": len(rows),
        "md_chars": len(md),
        "blocks": len(blocks),
        "elapsed_s": round(elapsed, 2),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create-page", action="store_true")
    group.add_argument("--regenerate", action="store_true")
    args = parser.parse_args(argv)
    tok = _token()

    if args.create_page:
        if PAGE_ID_FILE.exists():
            page_id = PAGE_ID_FILE.read_text(encoding="utf-8").strip()
            print(f"Snapshot page already exists: {page_id}")
            print("Use --regenerate to refresh content.")
            return 0
        page_id = create_snapshot_page(tok)
        PAGE_ID_FILE.write_text(page_id, encoding="utf-8")
        print(f"Created Backlog Snapshot page: {page_id}")
        _audit({"op": "create_page", "page_id": page_id, "ts": datetime.now(timezone.utc).isoformat()})
        print("Running initial regenerate...")
        result = regenerate(tok, page_id)
        print(f"Regenerated: {result}")
        _audit({"op": "regenerate", **result, "ts": datetime.now(timezone.utc).isoformat()})
        return 0

    # --regenerate
    if not PAGE_ID_FILE.exists():
        print("No snapshot page yet. Run with --create-page first.", file=sys.stderr)
        return 2
    page_id = PAGE_ID_FILE.read_text(encoding="utf-8").strip()
    result = regenerate(tok, page_id)
    print(f"Regenerated: {result}")
    _audit({"op": "regenerate", **result, "ts": datetime.now(timezone.utc).isoformat()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
