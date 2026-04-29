#!/usr/bin/env python3
"""
batch_rescore_notion.py — Drain UNSCORED rows in Wave/Phase Convergence.

Two distinct UNSCORED root causes are handled:

  1. Title-format drift — row has `P-Band` Notion select correctly set, but
     the Phase Title lacks the canonical `[Pn]` prefix that the snapshot
     renderer uses to classify rows. Pure cosmetic patch — patches the
     title only.

  2. Genuine unscored — both `P-Band` and the title prefix are missing. If
     Layer + Surface + Fan-In + Coverage Gap % are all populated, runs the
     deferred-scope scorer and patches both `P-Band` and the title prefix.
     Otherwise the row is emitted to a manual-triage CSV.

Dry-run by default. Pass --apply to actually patch Notion rows.

No hardcoded secrets. NOTION_TOKEN resolved from env or .env (same path as
tools/notion/snapshot_renderer.py).

Usage:
    python tools/priority/batch_rescore_notion.py             # dry-run
    python tools/priority/batch_rescore_notion.py --apply     # patch Notion
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ruff: noqa: E402  -- repo-root sys.path insertion required before tools.* imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.priority.deferred_scope_scorer import score_deferred_scope  # noqa: E402

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
BACKLOG_DS_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"

TRIAGE_CSV = REPO_ROOT / "docs" / "reports" / "maintenance" / "unscored_manual_triage.csv"
AUDIT_LOG = REPO_ROOT / "artifacts" / "windsurf" / "notion_batch_rescore_audit.jsonl"

PBAND_RE = re.compile(r"^\s*\[(P[0-5]|NEXT·P[0-5]|INDEX|RECOVERY|EVIDENCE)\b")


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
                result: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
                return result
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


def fetch_open_todos(tok: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {
            "page_size": 100,
            "filter": {"property": "Status", "select": {"equals": "Todo"}},
        }
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST", f"{NOTION_API}/data_sources/{BACKLOG_DS_ID}/query", tok, body)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return rows


def _title(row: dict) -> str:
    parts = row["properties"].get("Phase Title", {}).get("title", [])
    return "".join(p.get("plain_text", "") for p in parts).strip()


def _pband(row: dict) -> str | None:
    sel = row["properties"].get("P-Band", {}).get("select")
    return sel["name"] if sel else None


def _layer(row: dict) -> str | None:
    sel = row["properties"].get("Layer", {}).get("select")
    return sel["name"] if sel else None


def _surface(row: dict) -> str | None:
    sel = row["properties"].get("Surface", {}).get("select")
    return sel["name"] if sel else None


def _num(row: dict, prop: str) -> float | None:
    val = row["properties"].get(prop, {}).get("number")
    return float(val) if val is not None else None


def _has_band_prefix(title: str) -> bool:
    return bool(PBAND_RE.match(title))


def _patch_row(tok: str, page_id: str, props: dict, dry_run: bool) -> None:
    if dry_run:
        return
    _http("PATCH", f"{NOTION_API}/pages/{page_id}", tok, {"properties": props})


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch rescore UNSCORED Notion rows")
    parser.add_argument("--apply", action="store_true", help="Actually patch Notion (default: dry-run)")
    args = parser.parse_args()

    dry_run = not args.apply

    tok = _token()
    rows = fetch_open_todos(tok)

    fix1_cosmetic: list[tuple[str, str, str]] = []  # (page_id, old_title, new_title)
    fix2_scored: list[tuple[str, str, str, str]] = []  # (page_id, old_title, new_title, band)
    fix3_triage: list[dict] = []
    skipped: int = 0

    for row in rows:
        title = _title(row)
        if not title or _has_band_prefix(title):
            skipped += 1
            continue

        page_id = row["id"]
        existing_band = _pband(row)

        if existing_band and existing_band != "UNSCORED":
            # Fix-1: title-format drift only
            new_title = f"[{existing_band}] {title}"
            fix1_cosmetic.append((page_id, title, new_title))
            continue

        # Genuinely unscored — try to score
        layer = _layer(row)
        surface = _surface(row)
        fan_in = _num(row, "Fan-In")
        cov_gap = _num(row, "Coverage Gap %")

        if layer and surface and fan_in is not None and cov_gap is not None:
            try:
                result = score_deferred_scope(
                    layer=layer,
                    fan_in=int(fan_in),
                    surface=surface,
                    coverage_gap_pct=float(cov_gap),
                )
                band: str = str(result.band)
                new_title = f"[{band}] {title}"
                fix2_scored.append((page_id, title, new_title, band))
            except (ValueError, KeyError) as exc:
                fix3_triage.append({
                    "page_id": page_id,
                    "title": title,
                    "layer": layer,
                    "surface": surface,
                    "fan_in": fan_in,
                    "coverage_gap_pct": cov_gap,
                    "reason": f"scorer_error: {exc}",
                })
        else:
            missing = [
                k for k, v in {
                    "layer": layer, "surface": surface,
                    "fan_in": fan_in, "coverage_gap_pct": cov_gap,
                }.items() if v is None
            ]
            fix3_triage.append({
                "page_id": page_id,
                "title": title,
                "layer": layer,
                "surface": surface,
                "fan_in": fan_in,
                "coverage_gap_pct": cov_gap,
                "reason": f"missing_fields: {','.join(missing)}",
            })

    # Apply patches
    for page_id, _old, new_title in fix1_cosmetic:
        props = {"Phase Title": {"title": [{"text": {"content": new_title}}]}}
        _patch_row(tok, page_id, props, dry_run)

    for page_id, _old, new_title, band in fix2_scored:
        scored_props: dict[str, Any] = {
            "Phase Title": {"title": [{"text": {"content": new_title}}]},
            "P-Band": {"select": {"name": band}},
        }
        _patch_row(tok, page_id, scored_props, dry_run)

    # Manual-triage CSV
    if fix3_triage:
        TRIAGE_CSV.parent.mkdir(parents=True, exist_ok=True)
        with TRIAGE_CSV.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["page_id", "title", "layer", "surface", "fan_in", "coverage_gap_pct", "reason"],
            )
            writer.writeheader()
            writer.writerows(fix3_triage)

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run" if dry_run else "apply",
        "rows_inspected": len(rows),
        "skipped_already_scored": skipped,
        "fix1_cosmetic_patches": len(fix1_cosmetic),
        "fix2_scored_and_patched": len(fix2_scored),
        "fix3_manual_triage": len(fix3_triage),
        "triage_csv": str(TRIAGE_CSV.relative_to(REPO_ROOT)) if fix3_triage else None,
    }
    _audit(summary)

    print(json.dumps(summary, indent=2))
    print()
    print(f"  Mode:                  {summary['mode']}")
    print(f"  Inspected rows:        {summary['rows_inspected']}")
    print(f"  Already scored:        {summary['skipped_already_scored']}")
    print(f"  Fix-1 (cosmetic):      {summary['fix1_cosmetic_patches']}")
    print(f"  Fix-2 (scored+patch):  {summary['fix2_scored_and_patched']}")
    print(f"  Fix-3 (manual triage): {summary['fix3_manual_triage']}")
    if fix3_triage:
        print(f"  Triage CSV:            {summary['triage_csv']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
