#!/usr/bin/env python3
"""W4 P4.1 — Post-linkage accuracy re-audit.

For each Backlog row that has a resolved Plan relation:
  * Fetch the linked Plans DB page.
  * Read Plan-derived field values (Layer, Status, Plan File Path).
  * Compare against the current Backlog row values.
  * Classify each field as:
      - "match"          — Backlog value == Plan-derived value
      - "backlog_empty"  — Backlog cell is empty; Plan has data
      - "plan_empty"     — Plan cell is empty; Backlog has data
      - "both_empty"     — both empty
      - "conflict"       — both non-empty but differ

Outputs:
  artifacts/notion/backlog_plan_derived_delta.json  (machine-readable)
  Prints a markdown summary table to stdout.

Requires NOTION_TOKEN or NOTION_API_KEY.

Flags:
  --limit N    Inspect at most N linked rows (debug).
  --json-only  Suppress markdown summary; only write JSON.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    WAVE_PHASE_DATA_SOURCE_ID,
)

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

BACKLOG_QUERY_URL = f"{NOTION_BASE}/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query"
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{}}"
OUT_JSON = REPO_ROOT / "artifacts" / "notion" / "backlog_plan_derived_delta.json"
TIMEOUT = 30.0
THROTTLE_S = 0.35

# Backlog field → Plans DB property name (best-effort; some Plans rows may lack these)
FIELD_MAP: dict[str, str] = {
    "Layer": "Layer",
    "Status": "Status",
    "Plan File": "Plan File Path",
}

# Scorer default sentinel values (written by backfill_backlog_scores.py / W3)
SCORER_DEFAULTS: dict[str, str] = {
    "Layer": "L_MIXED",
    "Surface": "None",
    "Status": "Draft",
    "Wave ID": "W1",
    "Phase ID": "1.1",
}


# ──────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────────────────────────────────────

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


def _post(url: str, body: dict, token: str) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=_headers(token),
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_page(page_id: str, token: str) -> dict | None:
    try:
        req = urllib.request.Request(
            PAGE_URL_FMT.format(page_id),
            headers=_headers(token),
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def _query_all(token: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = _post(BACKLOG_QUERY_URL, body, token)
        rows.extend(data.get("results") or [])
        if not data.get("has_more"):
            return rows
        cursor = data.get("next_cursor")


# ──────────────────────────────────────────────────────────────────────────────
# Property extractors
# ──────────────────────────────────────────────────────────────────────────────

def _prop(row: dict, name: str) -> dict | None:
    return (row.get("properties") or {}).get(name)


def _select_name(prop: dict | None) -> str | None:
    if not prop or prop.get("type") != "select":
        return None
    v = prop.get("select")
    return (v or {}).get("name") if v else None


def _rich_text_value(prop: dict | None) -> str | None:
    if not prop:
        return None
    t = prop.get("type")
    if t == "rich_text":
        parts = prop.get("rich_text") or []
    elif t == "title":
        parts = prop.get("title") or []
    else:
        return None
    val = "".join((r.get("plain_text") or "") for r in parts).strip()
    return val or None


def _relation_ids(prop: dict | None) -> list[str]:
    if not prop or prop.get("type") != "relation":
        return []
    return [r["id"] for r in (prop.get("relation") or []) if r.get("id")]


def _extract_value(props: dict, name: str) -> str | None:
    """Extract a human-readable value from a page's properties dict."""
    prop = props.get(name)
    if prop is None:
        return None
    t = prop.get("type")
    if t == "select":
        return _select_name(prop)
    if t in {"rich_text", "title"}:
        return _rich_text_value(prop)
    if t == "number":
        v = prop.get("number")
        return str(v) if v is not None else None
    if t == "relation":
        ids = _relation_ids(prop)
        return ",".join(ids) if ids else None
    return None


def _classify(backlog_val: str | None, plan_val: str | None, field: str) -> str:
    if backlog_val is None and plan_val is None:
        return "both_empty"
    if backlog_val is None:
        return "backlog_empty"
    if plan_val is None:
        return "plan_empty"
    if backlog_val == plan_val:
        return "match"
    return "conflict"


def _is_scorer_default(field: str, value: str | None) -> bool:
    default = SCORER_DEFAULTS.get(field)
    return default is not None and value == default


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    token = _token()

    print("Querying Backlog Items…", file=sys.stderr)
    rows = _query_all(token)
    print(f"Total rows: {len(rows)}", file=sys.stderr)

    linked = [r for r in rows if _relation_ids(_prop(r, "Plan"))]
    print(f"Rows with Plan relation: {len(linked)}", file=sys.stderr)

    if args.limit is not None:
        linked = linked[: args.limit]
        print(f"Limited to: {len(linked)}", file=sys.stderr)

    # Per-field counters for summary
    counters: dict[str, dict[str, int]] = {
        f: {"match": 0, "backlog_empty": 0, "plan_empty": 0, "both_empty": 0, "conflict": 0, "scorer_default_overridable": 0}
        for f in FIELD_MAP
    }

    delta_rows: list[dict] = []

    bar = tqdm(linked, desc="Comparing fields", unit="row", colour="blue")
    for row in bar:
        page_id = row.get("id", "")
        title_prop = _prop(row, "Phase Title")
        title = _rich_text_value(title_prop) or _extract_value(row.get("properties", {}), "Phase Title") or page_id[:8]

        rel_ids = _relation_ids(_prop(row, "Plan"))
        plan_props: dict = {}
        for rel_id in rel_ids:
            plan_page = _get_page(rel_id, token)
            time.sleep(THROTTLE_S)
            if plan_page:
                plan_props = plan_page.get("properties") or {}
                break  # use first linked plan

        row_delta: dict = {
            "page_id": page_id,
            "title": title,
            "plan_id": rel_ids[0] if rel_ids else None,
            "fields": {},
        }

        for backlog_field, plan_field in FIELD_MAP.items():
            backlog_val = _extract_value(row.get("properties", {}), backlog_field)
            plan_val = _extract_value(plan_props, plan_field) if plan_props else None

            classification = _classify(backlog_val, plan_val, backlog_field)
            is_default = _is_scorer_default(backlog_field, backlog_val)

            counters[backlog_field][classification] += 1
            if classification == "conflict" and is_default:
                counters[backlog_field]["scorer_default_overridable"] += 1

            row_delta["fields"][backlog_field] = {
                "backlog_value": backlog_val,
                "plan_value": plan_val,
                "classification": classification,
                "backlog_is_scorer_default": is_default,
            }

        delta_rows.append(row_delta)

    # ── Write JSON output ──────────────────────────────────────────────────────
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "total_linked": len(linked),
        "field_summary": counters,
        "rows": delta_rows,
    }
    with OUT_JSON.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\nWrote {OUT_JSON}", file=sys.stderr)

    # ── Markdown summary ───────────────────────────────────────────────────────
    if not args.json_only:
        print(f"\n## W4 P4.1 — Backlog ↔ Plan derived-field delta (n={len(linked)} linked rows)\n")
        print(f"{'Field':<14} {'Match':>7} {'Backlog∅':>9} {'Plan∅':>7} {'Both∅':>7} {'Conflict':>9} {'Default→Override':>18}")
        print("-" * 76)
        for field, c in counters.items():
            print(
                f"{field:<14} {c['match']:>7} {c['backlog_empty']:>9} "
                f"{c['plan_empty']:>7} {c['both_empty']:>7} {c['conflict']:>9} "
                f"{c['scorer_default_overridable']:>18}"
            )
        print()

        # Highlight actionable conflicts
        actionable = [
            (f, c["conflict"], c["scorer_default_overridable"])
            for f, c in counters.items()
            if c["conflict"] > 0 or c["backlog_empty"] > 0
        ]
        if actionable:
            print("### Actionable rows (conflict or backlog_empty)")
            for field, conflicts, overridable in actionable:
                print(f"  - **{field}**: {conflicts} conflict(s), {overridable} are scorer-defaults (overridable); {counters[field]['backlog_empty']} backlog-empty")
        else:
            print("✅ No conflicts or backlog-empty cells found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
