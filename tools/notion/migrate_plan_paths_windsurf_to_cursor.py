#!/usr/bin/env python3
"""Migrate Notion plan file paths from .windsurf/plans to .cursor/plans.

W5.D1 deferred scope for windsurf-gha-cutover-d9f2a7.

Patches:
  - Plans DB ``Plan File Path`` rich_text
  - Wave/Phase Convergence ``Plan File`` rich_text

Only patches when the target ``.cursor/plans/<file>`` exists on disk (or slug glob).

Usage:
    python tools/notion/migrate_plan_paths_windsurf_to_cursor.py --dry-run
    python tools/notion/migrate_plan_paths_windsurf_to_cursor.py --execute
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._governance_paths import CURSOR_PLANS_DIR  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
WAVE_PHASE_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
PLANS_DS_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
AUDIT_LOG = REPO_ROOT / "artifacts" / "cursor" / "migrate_plan_paths_windsurf_to_cursor.jsonl"


def _token() -> str:
    tok = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if tok:
        return tok
    env = REPO_ROOT / ".env"
    if env.is_file():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN=") or line.startswith("NOTION_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set")


def _headers(tok: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {tok}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, tok: str, body: dict | None = None) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(tok))
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _query_ds(ds_id: str, tok: str, filter_: dict | None = None) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict[str, Any] = {"page_size": 100}
        if filter_:
            body["filter"] = filter_
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST", f"{NOTION_API}/data_sources/{ds_id}/query", tok, body)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return rows


def _rt_text(props: dict, name: str) -> str:
    items = props.get(name, {}).get("rich_text", [])
    return "".join(it.get("plain_text", "") for it in items)


def _audit(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _resolve_cursor_plan_path(raw: str) -> str | None:
    """Map Notion plan file reference to .cursor/plans/ path if resolvable on disk."""
    if not raw or not raw.strip():
        return None
    text = raw.strip().replace("\\", "/")
    if ".windsurf/plans/" in text:
        text = text.replace(".windsurf/plans/", ".cursor/plans/")
    elif text.startswith(".cursor/plans/"):
        pass
    elif "/" not in text:
        text = f".cursor/plans/{Path(text).name}"
    else:
        return None

    rel = Path(text)
    if not str(rel).startswith(".cursor/plans/"):
        return None
    full = REPO_ROOT / rel
    if full.is_file():
        return text.replace("\\", "/")

    name = full.name
    base = name[:-3] if name.endswith(".md") else name
    for candidate in CURSOR_PLANS_DIR.glob(f"{base}*.md"):
        if candidate.is_file():
            rel_path = candidate.relative_to(REPO_ROOT).as_posix()
            return rel_path
    # Archive mirror under .cursor/plans/_archive
    for candidate in (REPO_ROOT / ".cursor/plans").rglob(f"{base}*.md"):
        if candidate.is_file():
            return candidate.relative_to(REPO_ROOT).as_posix()
    # Legacy: copy from .windsurf/plans into cursor archive (execute mode only via caller)
    return None


def _ensure_cursor_copy_from_windsurf(filename: str, *, execute: bool) -> str | None:
    """If plan exists only under .windsurf/plans, copy to .cursor/plans/_archive/windsurf_legacy/."""
    name = Path(filename).name
    if not name.endswith(".md"):
        name = f"{name}.md"
    ws = REPO_ROOT / ".windsurf" / "plans" / name
    if not ws.is_file():
        for c in (REPO_ROOT / ".windsurf" / "plans").rglob(f"{Path(name).stem}*.md"):
            if c.is_file():
                ws = c
                break
    if not ws.is_file():
        return None
    dest_dir = REPO_ROOT / ".cursor/plans/_archive/windsurf_legacy"
    dest = dest_dir / ws.name
    rel = dest.relative_to(REPO_ROOT).as_posix()
    if dest.is_file():
        return rel
    if not execute:
        return rel
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(ws.read_text(encoding="utf-8"), encoding="utf-8")
    return rel


def _patch_page(page_id: str, prop_name: str, new_value: str, tok: str, dry_run: bool) -> bool:
    body = {
        "properties": {
            prop_name: {
                "rich_text": [{"type": "text", "text": {"content": new_value[:2000]}}]
            }
        }
    }
    if dry_run:
        return True
    _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, body)
    time.sleep(0.35)
    return True


def migrate_plans_db(tok: str, dry_run: bool, *, execute: bool) -> dict[str, int]:
    rows = _query_ds(
        PLANS_DS_ID,
        tok,
        filter_={
            "or": [
                {"property": "Plan File Path", "rich_text": {"contains": ".windsurf/plans"}},
                {"property": "Plan File Path", "rich_text": {"contains": "windsurf/plans"}},
            ]
        },
    )
    patched = skipped = failed = 0
    for row in rows:
        page_id = row["id"]
        props = row.get("properties", {})
        current = _rt_text(props, "Plan File Path")
        new_path = _resolve_cursor_plan_path(current)
        if not new_path:
            new_path = _ensure_cursor_copy_from_windsurf(current, execute=execute)
        if not new_path or new_path == current:
            skipped += 1
            continue
        try:
            if _patch_page(page_id, "Plan File Path", new_path, tok, dry_run):
                patched += 1
                _audit({"db": "plans", "page_id": page_id, "from": current, "to": new_path})
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, RuntimeError) as exc:
            failed += 1
            _audit({"db": "plans", "page_id": page_id, "error": str(exc)[:300]})
    return {"patched": patched, "skipped": skipped, "failed": failed, "candidates": len(rows)}


def migrate_wave_phase(tok: str, dry_run: bool, *, execute: bool) -> dict[str, int]:
    rows = _query_ds(
        WAVE_PHASE_DS_ID,
        tok,
        filter_={
            "or": [
                {"property": "Plan File", "rich_text": {"contains": "windsurf"}},
                {"property": "Plan File", "rich_text": {"contains": ".md"}},
            ]
        },
    )
    patched = skipped = failed = 0
    for row in rows:
        page_id = row["id"]
        props = row.get("properties", {})
        current = _rt_text(props, "Plan File")
        if not current:
            skipped += 1
            continue
        if ".windsurf/" in current:
            new_val = _resolve_cursor_plan_path(current)
        elif current.endswith(".md"):
            new_val = _resolve_cursor_plan_path(current)
        else:
            skipped += 1
            continue
        if not new_val:
            new_val = _ensure_cursor_copy_from_windsurf(current, execute=execute)
        if not new_val:
            skipped += 1
            continue
        # Wave/Phase stores filename only in many rows
        new_file = Path(new_val).name
        if new_file == current and ".windsurf" not in current:
            skipped += 1
            continue
        try:
            if _patch_page(page_id, "Plan File", new_file, tok, dry_run):
                patched += 1
                _audit({"db": "wave_phase", "page_id": page_id, "from": current, "to": new_file})
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, RuntimeError) as exc:
            failed += 1
            _audit({"db": "wave_phase", "page_id": page_id, "error": str(exc)[:300]})
    return {"patched": patched, "skipped": skipped, "failed": failed, "scanned": len(rows)}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    dry_run = args.dry_run

    tok = _token()
    mode = "DRY-RUN" if dry_run else "EXECUTE"
    print(f"=== migrate_plan_paths_windsurf_to_cursor ({mode}) ===")

    execute = not dry_run
    plans = migrate_plans_db(tok, dry_run, execute=execute)
    wave = migrate_wave_phase(tok, dry_run, execute=execute)

    print(f"Plans DB: {plans}")
    print(f"Wave/Phase: {wave}")
    print(f"Audit: {AUDIT_LOG}")
    return 0 if plans.get("failed", 0) == 0 and wave.get("failed", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
