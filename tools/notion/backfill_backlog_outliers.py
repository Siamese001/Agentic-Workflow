#!/usr/bin/env python3
"""W3 — Backlog Items outlier spot-fix.

Three sub-probes (run all three unless --probe is specified):

  probe1 — Phase ID / Status / Wave ID (up to ~22 rows)
    For rows missing Phase ID, Status, or Wave ID:
      * If the row's `Plan File` slug matches a known on-disk plan
        (slug extracted from filename <slug>-<6hex>.md), recover from plan slug
        where possible (currently: no extra data in slug → not applicable).
      * Write safe defaults: Phase ID=1.1, Status=Draft, Wave ID=W1.
      * Record `Evidence` note: "W3 default applied — no plan-derived value".

  probe2 — Plan File (up to 3 rows)
    For rows missing `Plan File` but having a `Plan` relation:
      * Walk back to Plans DB via the relation; read `Plan File Path`.
      * Write that value into Backlog row's `Plan File`.

  probe3 — Layer / Surface edge cases (up to 16 rows)
    For rows that have a non-null `Layer` or `Surface` property but whose
    select value returned None via _select_name (structurally broken cell,
    mid-migration multi_select→select survivor):
      * Write `L_MIXED` for Layer / `None` for Surface unconditionally.
      * Log the 16 page IDs to artifacts/cursor/w3_layer_surface_fixes.jsonl.

Idempotent per field: only writes if the target field is currently empty
(or structurally broken for probe3).
Fail-open per row.
Requires NOTION_TOKEN or NOTION_API_KEY.

Flags:
  --dry-run       Compute but do not PATCH.
  --probe N       Run only probe N (1, 2, or 3).
  --limit N       Process at most N eligible rows per probe (debug).
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
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
    WAVE_PHASE_DATA_SOURCE_ID,
)

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

BACKLOG_QUERY_URL = f"{NOTION_BASE}/data_sources/{WAVE_PHASE_DATA_SOURCE_ID}/query"
PLANS_QUERY_URL = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{}}"
LAYER_SURFACE_LOG = REPO_ROOT / "artifacts" / "windsurf" / "w3_layer_surface_fixes.jsonl"
TIMEOUT = 30.0
THROTTLE_S = 0.35

_PLANS_SLUG_RE = re.compile(r"^(.+)-[0-9a-f]{6}$")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
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


def _get(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers=_headers(token))
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _patch_page(page_id: str, properties: dict, token: str) -> tuple[bool, str]:
    req = urllib.request.Request(
        PAGE_URL_FMT.format(page_id),
        data=json.dumps({"properties": properties}).encode("utf-8"),
        method="PATCH",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            resp.read()
        return True, "ok"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:300]
        return False, f"http_{exc.code}:{body}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"net:{exc!r}"


def _query_all(url: str, token: str) -> list[dict]:
    rows: list[dict] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = _post(url, body, token)
        rows.extend(data.get("results") or [])
        if not data.get("has_more"):
            return rows
        cursor = data.get("next_cursor")


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
    return "".join((r.get("plain_text") or "") for r in parts).strip() or None


def _number_value(prop: dict | None) -> float | None:
    if not prop or prop.get("type") != "number":
        return None
    return prop.get("number")


def _relation_ids(prop: dict | None) -> list[str]:
    if not prop or prop.get("type") != "relation":
        return []
    return [r["id"] for r in (prop.get("relation") or []) if r.get("id")]


def _select_is_structurally_broken(prop: dict | None) -> bool:
    """Return True if the cell is non-null but _select_name returns None."""
    if prop is None:
        return False
    t = prop.get("type")
    raw = prop.get(t)
    if raw is None:
        return False
    # Cell exists but select name is missing — structurally broken
    return _select_name(prop) is None


# ──────────────────────────────────────────────────────────────────────────────
# Probe 1 — Phase ID / Status / Wave ID defaults
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_PHASE_ID = "1.1"
_DEFAULT_STATUS = "Not Started"
_DEFAULT_WAVE_ID = "W1"
_EVIDENCE_NOTE = "W3 default applied — no plan-derived value"


def _needs_probe1(row: dict) -> bool:
    missing_phase = _rich_text_value(_prop(row, "Phase ID")) is None
    missing_status = _select_name(_prop(row, "Status")) is None
    missing_wave = _rich_text_value(_prop(row, "Wave ID")) is None
    return missing_phase or missing_status or missing_wave


def run_probe1(rows: list[dict], token: str, dry_run: bool, limit: int | None) -> dict:
    eligible = [r for r in rows if _needs_probe1(r)]
    if limit is not None:
        eligible = eligible[:limit]

    ok = fail = skip = 0
    today_iso = date.today().isoformat()
    bar = tqdm(eligible, desc="Probe1 Phase/Status/WaveID", unit="row", colour="cyan")
    for row in bar:
        page_id = row.get("id")
        if not page_id:
            skip += 1
            continue

        props: dict = {}
        if _rich_text_value(_prop(row, "Phase ID")) is None:
            props["Phase ID"] = {
                "rich_text": [{"type": "text", "text": {"content": _DEFAULT_PHASE_ID}}]
            }
        if _select_name(_prop(row, "Status")) is None:
            props["Status"] = {"select": {"name": _DEFAULT_STATUS}}
        if _rich_text_value(_prop(row, "Wave ID")) is None:
            props["Wave ID"] = {
                "rich_text": [{"type": "text", "text": {"content": _DEFAULT_WAVE_ID}}]
            }
        # Append evidence note
        props["Evidence"] = {
            "rich_text": [{"type": "text", "text": {"content": _EVIDENCE_NOTE}}]
        }
        props["Last Updated"] = {"date": {"start": today_iso}}

        if dry_run:
            ok += 1
            continue

        success, err = _patch_page(page_id, props, token)
        if success:
            ok += 1
        else:
            fail += 1
            if hasattr(bar, "write"):
                bar.write(f"FAIL {page_id}: {err}")
            else:
                print(f"FAIL {page_id}: {err}", file=sys.stderr)
        time.sleep(THROTTLE_S)

    return {"eligible": len(eligible), "ok": ok, "fail": fail, "skip": skip}


# ──────────────────────────────────────────────────────────────────────────────
# Probe 2 — Plan File walkback from Plan relation
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_plan_file_path(plan_page_id: str, token: str) -> str | None:
    """Return the Plan File Path property from the Plans DB page."""
    try:
        page = _get(PAGE_URL_FMT.format(plan_page_id), token)
        props = page.get("properties") or {}
        # Try common property name variants
        for candidate in ("Plan File Path", "Plan File", "File Path"):
            prop = props.get(candidate)
            if prop:
                val = _rich_text_value(prop)
                if val:
                    return val
    except Exception:  # noqa: BLE001
        pass
    return None


def _needs_probe2(row: dict) -> bool:
    has_relation = bool(_relation_ids(_prop(row, "Plan")))
    missing_plan_file = _rich_text_value(_prop(row, "Plan File")) is None
    return has_relation and missing_plan_file


def run_probe2(rows: list[dict], token: str, dry_run: bool, limit: int | None) -> dict:
    eligible = [r for r in rows if _needs_probe2(r)]
    if limit is not None:
        eligible = eligible[:limit]

    ok = fail = skip = miss = 0
    today_iso = date.today().isoformat()
    bar = tqdm(eligible, desc="Probe2 PlanFile walkback", unit="row", colour="yellow")
    for row in bar:
        page_id = row.get("id")
        if not page_id:
            skip += 1
            continue

        rel_ids = _relation_ids(_prop(row, "Plan"))
        plan_file_path: str | None = None
        for rel_id in rel_ids:
            plan_file_path = _fetch_plan_file_path(rel_id, token)
            time.sleep(THROTTLE_S)
            if plan_file_path:
                break

        if not plan_file_path:
            miss += 1
            msg = f"MISS {page_id}: no Plan File Path on linked plan(s) {rel_ids}"
            if hasattr(bar, "write"):
                bar.write(msg)
            else:
                print(msg, file=sys.stderr)
            continue

        props: dict = {
            "Plan File": {
                "rich_text": [{"type": "text", "text": {"content": plan_file_path}}]
            },
            "Last Updated": {"date": {"start": today_iso}},
        }

        if dry_run:
            ok += 1
            continue

        success, err = _patch_page(page_id, props, token)
        if success:
            ok += 1
        else:
            fail += 1
            if hasattr(bar, "write"):
                bar.write(f"FAIL {page_id}: {err}")
            else:
                print(f"FAIL {page_id}: {err}", file=sys.stderr)
        time.sleep(THROTTLE_S)

    return {"eligible": len(eligible), "ok": ok, "fail": fail, "skip": skip, "miss": miss}


# ──────────────────────────────────────────────────────────────────────────────
# Probe 3 — Layer / Surface structurally-broken select cells
# ──────────────────────────────────────────────────────────────────────────────

def _needs_probe3(row: dict) -> bool:
    layer_broken = _select_is_structurally_broken(_prop(row, "Layer"))
    surface_broken = _select_is_structurally_broken(_prop(row, "Surface"))
    # Also include rows where both are simply empty (belt-and-suspenders)
    layer_empty = _select_name(_prop(row, "Layer")) is None
    surface_empty = _select_name(_prop(row, "Surface")) is None
    return layer_broken or surface_broken or layer_empty or surface_empty


def run_probe3(rows: list[dict], token: str, dry_run: bool, limit: int | None) -> dict:
    eligible = [r for r in rows if _needs_probe3(r)]
    if limit is not None:
        eligible = eligible[:limit]

    ok = fail = skip = 0
    today_iso = date.today().isoformat()
    log_rows: list[dict] = []

    bar = tqdm(eligible, desc="Probe3 Layer/Surface fix", unit="row", colour="magenta")
    for row in bar:
        page_id = row.get("id")
        if not page_id:
            skip += 1
            continue

        props: dict = {}
        layer_prop = _prop(row, "Layer")
        surface_prop = _prop(row, "Surface")

        # Only write if actually broken/empty (do NOT overwrite valid values)
        if _select_name(layer_prop) is None:
            props["Layer"] = {"select": {"name": "L_MIXED"}}
        if _select_name(surface_prop) is None:
            props["Surface"] = {"select": {"name": "None"}}

        if not props:
            skip += 1
            continue

        props["Last Updated"] = {"date": {"start": today_iso}}

        log_rows.append({
            "page_id": page_id,
            "layer_was": (layer_prop or {}).get("select") if layer_prop else None,
            "surface_was": (surface_prop or {}).get("select") if surface_prop else None,
            "wrote": list(props.keys()),
        })

        if dry_run:
            ok += 1
            continue

        success, err = _patch_page(page_id, props, token)
        if success:
            ok += 1
        else:
            fail += 1
            if hasattr(bar, "write"):
                bar.write(f"FAIL {page_id}: {err}")
            else:
                print(f"FAIL {page_id}: {err}", file=sys.stderr)
        time.sleep(THROTTLE_S)

    # Write log even in dry-run so the IDs are available for post-hoc inspection
    if log_rows:
        LAYER_SURFACE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with LAYER_SURFACE_LOG.open("a", encoding="utf-8") as fh:
            for entry in log_rows:
                fh.write(json.dumps(entry) + "\n")
        print(f"Logged {len(log_rows)} rows → {LAYER_SURFACE_LOG}", file=sys.stderr)

    return {"eligible": len(eligible), "ok": ok, "fail": fail, "skip": skip}


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--probe",
        type=int,
        choices=[1, 2, 3],
        default=None,
        help="Run only this probe (default: all three)",
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    token = _token()

    print("Querying Backlog Items…", file=sys.stderr)
    rows = _query_all(BACKLOG_QUERY_URL, token)
    print(f"Total rows: {len(rows)}", file=sys.stderr)

    probes = [args.probe] if args.probe else [1, 2, 3]
    summary: dict[int, dict] = {}

    if 1 in probes:
        print("\n── Probe 1: Phase ID / Status / Wave ID ──", file=sys.stderr)
        summary[1] = run_probe1(rows, token, args.dry_run, args.limit)
        print(f"  result: {summary[1]}", file=sys.stderr)

    if 2 in probes:
        print("\n── Probe 2: Plan File walkback ──", file=sys.stderr)
        summary[2] = run_probe2(rows, token, args.dry_run, args.limit)
        print(f"  result: {summary[2]}", file=sys.stderr)

    if 3 in probes:
        print("\n── Probe 3: Layer / Surface edge cases ──", file=sys.stderr)
        summary[3] = run_probe3(rows, token, args.dry_run, args.limit)
        print(f"  result: {summary[3]}", file=sys.stderr)

    total_fail = sum(v.get("fail", 0) for v in summary.values())
    print(
        f"\nDone. dry_run={args.dry_run}  total_fail={total_fail}",
        file=sys.stderr,
    )
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
