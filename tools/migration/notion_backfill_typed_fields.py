#!/usr/bin/env python3
"""
notion_backfill_typed_fields.py — W2 of notion-backlog-schema-refactor-7c3d9e.

Parses legacy Wave/Phase Convergence rows and populates the W1-added typed
fields: P-Band, Impact Score, Fan-In, Coverage Gap %, Layer, Surface, Last Scored.

Idempotent: skips rows where P-Band is already set. Safe to re-run.

Parsing contract:
    Phase Title: "[Pn] <rest>"                          -> P-Band = Pn
    Blocking Items: "Layer=<L>, fan_in=<N>, surface=<S>,
                     coverage_gap_pct=<F>. Priority impact score: <F>."
                                                         -> Layer, Fan-In, Surface,
                                                            Coverage Gap %, Impact Score

Rows without [Pn] prefix -> P-Band = UNSCORED.
Rows without the structured Blocking Items pattern -> typed fields left empty.

Usage:
    python tools/migration/notion_backfill_typed_fields.py --dry-run
    python tools/migration/notion_backfill_typed_fields.py --execute

Artifacts:
    artifacts/cursor/notion_backfill_audit.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import urllib.error

DATA_SOURCE_ID = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"
AUDIT_LOG = Path("artifacts/cursor/notion_backfill_audit.jsonl")

BAND_RE = re.compile(r"^\s*\[(P[0-5])\]")
METRICS_RE = re.compile(
    r"Layer=(L\w+)\s*,\s*fan_in=(\d+)\s*,\s*surface=(\w+)\s*,\s*"
    r"coverage_gap_pct=(\d+(?:\.\d+)?)\.?\s+Priority impact score:\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

VALID_LAYERS = {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_OPS", "L_TOOLS", "L_SHARED"}
VALID_SURFACES = {"Security", "Write", "Execution", "State", "Observability", "None"}


def _load_token() -> str:
    token = os.environ.get("NOTION_TOKEN")
    if token:
        return token
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("NOTION_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_TOKEN not set (env or .env)")


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _http(method: str, url: str, token: str, body: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(token))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < 2:
                retry_after = int(err.headers.get("Retry-After", "2"))
                time.sleep(retry_after)
                continue
            body_text = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {err.code} {method} {url}: {body_text}") from err
        except urllib.error.URLError as err:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            raise RuntimeError(f"URL error {method} {url}: {err}") from err
    raise RuntimeError(f"Exhausted retries for {method} {url}")


def _rt(prop: dict) -> str:
    if not prop:
        return ""
    return "".join(x.get("plain_text", "") for x in prop.get("rich_text", []))


def _title(prop: dict) -> str:
    if not prop:
        return ""
    return "".join(x.get("plain_text", "") for x in prop.get("title", []))


def fetch_all_rows(token: str) -> list[dict]:
    """Paginate the entire Wave/Phase Convergence data source."""
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = _http("POST", f"{NOTION_API}/data_sources/{DATA_SOURCE_ID}/query", token, body)
        rows.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return rows


def parse_row(row: dict) -> dict:
    """Extract typed values from a legacy row. Empty dict keys = not parseable."""
    props = row["properties"]
    title = _title(props.get("Phase Title"))
    blocking = _rt(props.get("Blocking Items"))

    parsed: dict = {}
    # Band from [Pn] prefix
    m = BAND_RE.match(title)
    parsed["band"] = m.group(1) if m else "UNSCORED"

    # Metrics from blocking items prose
    mm = METRICS_RE.search(blocking)
    if mm:
        layer, fan_in, surface, gap, impact = mm.groups()
        layer = layer.upper()
        # Normalize surface case (blocking-items uses mixed case)
        surface_norm = next(
            (s for s in VALID_SURFACES if s.lower() == surface.lower()),
            None,
        )
        if layer in VALID_LAYERS and surface_norm is not None:
            parsed["layer"] = layer
            parsed["surface"] = surface_norm
            parsed["fan_in"] = int(fan_in)
            parsed["coverage_gap_pct"] = float(gap)
            parsed["impact_score"] = float(impact)
    return parsed


def already_backfilled(row: dict) -> bool:
    """Idempotency: skip if P-Band is already set (by prior backfill or hook)."""
    pband = row["properties"].get("P-Band")
    if pband and pband.get("select"):
        return True
    return False


def build_patch_properties(parsed: dict) -> dict:
    """Convert parsed dict to Notion property-update payload."""
    payload: dict = {
        "P-Band": {"select": {"name": parsed["band"]}},
        "Last Scored": {"date": {"start": datetime.now(timezone.utc).date().isoformat()}},
    }
    if "impact_score" in parsed:
        payload["Impact Score"] = {"number": round(parsed["impact_score"], 2)}
    if "fan_in" in parsed:
        payload["Fan-In"] = {"number": parsed["fan_in"]}
    if "coverage_gap_pct" in parsed:
        # Notion percent format expects 0..1
        payload["Coverage Gap %"] = {"number": parsed["coverage_gap_pct"] / 100.0}
    if "layer" in parsed:
        payload["Layer"] = {"select": {"name": parsed["layer"]}}
    if "surface" in parsed:
        payload["Surface"] = {"select": {"name": parsed["surface"]}}
    return payload


def patch_page(page_id: str, properties: dict, token: str) -> dict:
    return _http("PATCH", f"{NOTION_API}/pages/{page_id}", token, {"properties": properties})


def audit_log(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Parse + report, no writes")
    group.add_argument("--execute", action="store_true", help="Parse + write typed fields via API-patch-page")
    args = parser.parse_args(argv)

    token = _load_token()
    rows = fetch_all_rows(token)
    print(f"Fetched {len(rows)} rows from Wave/Phase Convergence.")

    total = len(rows)
    skipped = 0
    scored = 0
    band_only = 0
    errors = 0

    run_ts = datetime.now(timezone.utc).isoformat()

    for idx, row in enumerate(rows, 1):
        page_id = row["id"]
        title = _title(row["properties"].get("Phase Title"))[:60]

        if already_backfilled(row):
            skipped += 1
            continue

        parsed = parse_row(row)
        has_metrics = "impact_score" in parsed
        entry = {
            "ts": run_ts,
            "page_id": page_id,
            "title": title,
            "parsed": parsed,
            "mode": "execute" if args.execute else "dry_run",
        }

        if has_metrics:
            scored += 1
        else:
            band_only += 1

        if args.execute:
            try:
                props = build_patch_properties(parsed)
                patch_page(page_id, props, token)
                entry["status"] = "ok"
                # Gentle rate-limit cushion
                if idx % 3 == 0:
                    time.sleep(0.35)
            except (RuntimeError, ValueError, KeyError) as exc:
                errors += 1
                entry["status"] = "error"
                entry["error"] = str(exc)
        else:
            entry["status"] = "dry_run"

        audit_log(entry)
        bar_pct = idx * 100 // total
        if idx % 10 == 0 or idx == total:
            print(
                f"  [{idx:>3}/{total}] {bar_pct:>3}% "
                f"scored={scored} band_only={band_only} "
                f"skipped={skipped} errors={errors}"
            )

    print()
    print(f"=== Backfill {'EXECUTE' if args.execute else 'DRY-RUN'} complete ===")
    print(f"Total rows:   {total}")
    print(f"Already done: {skipped}  (had P-Band set)")
    print(f"Fully scored: {scored}   (band + metrics)")
    print(f"Band only:    {band_only}")
    print(f"Errors:       {errors}")
    print(f"Audit log:    {AUDIT_LOG}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
