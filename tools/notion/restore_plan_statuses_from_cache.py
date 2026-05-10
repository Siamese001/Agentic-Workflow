#!/usr/bin/env python3
"""Plan notion-plans-status-bulk-recovery-c4e2f9 — restore Plans DB Status from cache snapshot.

At ~2026-05-10T10:50 UTC, all 328 rows in the Notion Plans DB were
bulk-overwritten to Status="Not Started". This script reverses that overwrite
by patching each row to the Status recorded in
`.windsurf/state/plan_registration_cache.json` (a 2026-05-10T01:44:17Z snapshot
captured ~9h pre-corruption).

Pattern source: tools/notion/apply_plan_derived_status.py.

Modes:
  --dry-run   Compare cache vs current Notion state, write
              artifacts/notion/plan_status_recovery_diff.json. No PATCHes.
  --execute   Apply PATCHes for every divergent row. Idempotent (re-running
              after success produces 0 eligible rows).
  --verify    Re-query Notion and verify post-recovery distribution matches
              the cache distribution; write
              artifacts/notion/plan_status_recovery_report.json.

  --limit N   Process at most N rows (debug).

Sanctioned non-MCP path per .windsurf/rules/notion-plan-wave-deferral.md —
direct HTTP, no MCP tool invocations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import NOTION_API_VERSION, NOTION_BASE  # noqa: E402

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = lambda it, **kw: it  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLAN_REG_CACHE = REPO_ROOT / ".windsurf" / "state" / "plan_registration_cache.json"
PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
PLANS_DATABASE_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"

DIFF_OUT = REPO_ROOT / "artifacts" / "notion" / "plan_status_recovery_diff.json"
REPORT_OUT = REPO_ROOT / "artifacts" / "notion" / "plan_status_recovery_report.json"

PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{}}"
QUERY_URL = f"{NOTION_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
TIMEOUT = 30.0
THROTTLE_S = 0.35  # ~3 req/s to stay under Notion rate limit

CANONICAL_STATUSES = {
    "In Progress",
    "Not Started",
    "Deferred",
    "Waiting",
    "Completed",
    "Retired",
    "Archived",
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


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


def _query_all_plans(token: str) -> list[dict]:
    """Page through the Plans data source and return all rows.

    Returns list of {page_id, slug, status} dicts.
    """
    out: list[dict] = []
    payload: dict = {"page_size": 100}
    while True:
        req = urllib.request.Request(
            QUERY_URL,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers=_headers(token),
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for page in data.get("results", []):
            page_id = page.get("id")
            props = page.get("properties", {})
            slug_prop = props.get("Slug", {}).get("title", []) or []
            slug = (
                slug_prop[0].get("plain_text", "")
                if slug_prop
                else ""
            )
            status_sel = (props.get("Status", {}) or {}).get("select") or {}
            status = status_sel.get("name", "")
            out.append({"page_id": page_id, "slug": slug, "status": status})

        if not data.get("has_more"):
            break
        payload = {"page_size": 100, "start_cursor": data["next_cursor"]}
        time.sleep(0.1)

    return out


# ---------------------------------------------------------------------------
# Recovery logic
# ---------------------------------------------------------------------------


def _load_cache() -> dict[str, dict]:
    if not PLAN_REG_CACHE.exists():
        print(f"ERROR: {PLAN_REG_CACHE} not found", file=sys.stderr)
        sys.exit(1)
    with PLAN_REG_CACHE.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("plans", {})


def _build_diff(cache: dict[str, dict], live_rows: list[dict]) -> dict:
    """Build per-row diff: cache_status vs live_status.

    Indexed by page_id (cache is keyed by slug → has page_id; live is keyed by page_id).
    """
    # cache_by_page_id
    cache_by_pid: dict[str, dict] = {}
    for slug, info in cache.items():
        pid = info.get("page_id")
        if pid:
            cache_by_pid[pid] = {"slug": slug, **info}

    rows_diff: list[dict] = []
    cache_dist: Counter[str] = Counter()
    live_dist: Counter[str] = Counter()
    target_dist: Counter[str] = Counter()

    seen_pids: set[str] = set()
    for live in live_rows:
        pid = live["page_id"]
        seen_pids.add(pid)
        live_status = live["status"]
        live_dist[live_status] += 1

        cache_entry = cache_by_pid.get(pid)
        if not cache_entry:
            # Live row not in cache snapshot — leave alone.
            rows_diff.append({
                "page_id": pid,
                "slug": live["slug"],
                "live_status": live_status,
                "cache_status": None,
                "action": "skip_not_in_cache",
                "reason": "no cache entry for page_id (post-snapshot row)",
            })
            target_dist[live_status] += 1
            continue

        cache_status = cache_entry.get("status", "")
        cache_dist[cache_status] += 1

        if cache_status not in CANONICAL_STATUSES:
            rows_diff.append({
                "page_id": pid,
                "slug": cache_entry["slug"],
                "live_status": live_status,
                "cache_status": cache_status,
                "action": "skip_non_canonical_cache",
                "reason": f"cache had non-canonical status '{cache_status}' — manual review",
            })
            target_dist[live_status] += 1
            continue

        if live_status == cache_status:
            rows_diff.append({
                "page_id": pid,
                "slug": cache_entry["slug"],
                "live_status": live_status,
                "cache_status": cache_status,
                "action": "skip_already_matches",
                "reason": "live already matches cache",
            })
            target_dist[live_status] += 1
            continue

        rows_diff.append({
            "page_id": pid,
            "slug": cache_entry["slug"],
            "live_status": live_status,
            "cache_status": cache_status,
            "action": "patch",
            "reason": f"restore {live_status} → {cache_status}",
        })
        target_dist[cache_status] += 1

    # Cache rows whose page_ids no longer exist in live.
    for pid, entry in cache_by_pid.items():
        if pid in seen_pids:
            continue
        rows_diff.append({
            "page_id": pid,
            "slug": entry["slug"],
            "live_status": None,
            "cache_status": entry.get("status", ""),
            "action": "skip_missing_live",
            "reason": "page_id present in cache but not in live query (deleted/archived?)",
        })
        cache_dist[entry.get("status", "")] += 1

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "cache_snapshot_path": str(PLAN_REG_CACHE.relative_to(REPO_ROOT)),
        "live_rows_total": len(live_rows),
        "cache_rows_total": len(cache),
        "distributions": {
            "cache": dict(cache_dist),
            "live": dict(live_dist),
            "target": dict(target_dist),
        },
        "patch_count": sum(1 for r in rows_diff if r["action"] == "patch"),
        "skip_already_matches_count": sum(1 for r in rows_diff if r["action"] == "skip_already_matches"),
        "skip_non_canonical_count": sum(1 for r in rows_diff if r["action"] == "skip_non_canonical_cache"),
        "skip_not_in_cache_count": sum(1 for r in rows_diff if r["action"] == "skip_not_in_cache"),
        "skip_missing_live_count": sum(1 for r in rows_diff if r["action"] == "skip_missing_live"),
        "rows": rows_diff,
    }


def _execute_patches(
    diff: dict,
    token: str,
    limit: int | None = None,
    only_from_not_started: bool = False,
) -> dict:
    eligible = [r for r in diff["rows"] if r["action"] == "patch"]
    if only_from_not_started:
        eligible = [r for r in eligible if r["live_status"] == "Not Started"]
    if limit is not None:
        eligible = eligible[:limit]

    ok = fail = 0
    failures: list[dict] = []

    bar = tqdm(eligible, desc="Restoring Status", unit="row", colour="green")
    for row in bar:
        props = {"Status": {"select": {"name": row["cache_status"]}}}
        success, err = _patch_page(row["page_id"], props, token)
        if success:
            ok += 1
        else:
            fail += 1
            failures.append({
                "page_id": row["page_id"],
                "slug": row["slug"],
                "target_status": row["cache_status"],
                "error": err,
            })
            if hasattr(bar, "write"):
                bar.write(f"FAIL {row['page_id']} ({row['slug']}): {err}")
        time.sleep(THROTTLE_S)

    return {
        "executed_at": datetime.now(tz=timezone.utc).isoformat(),
        "attempted": len(eligible),
        "patched_count": ok,
        "fail_count": fail,
        "failures": failures,
    }


def _verify(token: str, cache: dict[str, dict]) -> dict:
    """Re-query live state and compare distributions to cache."""
    live_rows = _query_all_plans(token)
    diff = _build_diff(cache, live_rows)
    cache_dist = diff["distributions"]["cache"]
    live_dist = diff["distributions"]["live"]
    delta = {
        s: live_dist.get(s, 0) - cache_dist.get(s, 0)
        for s in CANONICAL_STATUSES
    }
    matches_distribution = all(abs(v) <= 5 for v in delta.values())
    remaining_patches = diff["patch_count"]
    return {
        "verified_at": datetime.now(tz=timezone.utc).isoformat(),
        "cache_distribution": cache_dist,
        "live_distribution": live_dist,
        "delta_per_status": delta,
        "matches_distribution_within_5": matches_distribution,
        "remaining_patches_needed": remaining_patches,
        "verdict": "GREEN" if matches_distribution and remaining_patches == 0 else "RED",
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="compute diff, no PATCH")
    mode.add_argument("--execute", action="store_true", help="apply PATCHes")
    mode.add_argument("--verify", action="store_true", help="re-query and verify post-recovery distribution")
    parser.add_argument("--limit", type=int, default=None, help="process at most N rows (debug)")
    parser.add_argument(
        "--only-from-not-started",
        action="store_true",
        help="conservative mode: only patch rows whose live status is 'Not Started' "
             "(skip cross-status drift in the cache→corruption window)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    cache = _load_cache()
    print(f"Cache rows: {len(cache)}", file=sys.stderr)

    if args.verify:
        token = _token()
        report = _verify(token, cache)
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nVerify report: {REPORT_OUT}", file=sys.stderr)
        print(f"Verdict: {report['verdict']}", file=sys.stderr)
        print(f"Remaining patches needed: {report['remaining_patches_needed']}", file=sys.stderr)
        return 0 if report["verdict"] == "GREEN" else 1

    token = _token()
    print("Querying live Plans DB ...", file=sys.stderr)
    live_rows = _query_all_plans(token)
    print(f"Live rows: {len(live_rows)}", file=sys.stderr)

    diff = _build_diff(cache, live_rows)
    DIFF_OUT.parent.mkdir(parents=True, exist_ok=True)
    DIFF_OUT.write_text(json.dumps(diff, indent=2), encoding="utf-8")

    print(f"\nDiff written: {DIFF_OUT}", file=sys.stderr)
    print(
        f"  patch_count: {diff['patch_count']}\n"
        f"  skip_already_matches: {diff['skip_already_matches_count']}\n"
        f"  skip_non_canonical: {diff['skip_non_canonical_count']}\n"
        f"  skip_not_in_cache: {diff['skip_not_in_cache_count']}\n"
        f"  skip_missing_live: {diff['skip_missing_live_count']}",
        file=sys.stderr,
    )
    print(f"  cache_distribution: {diff['distributions']['cache']}", file=sys.stderr)
    print(f"  live_distribution: {diff['distributions']['live']}", file=sys.stderr)
    print(f"  target_distribution: {diff['distributions']['target']}", file=sys.stderr)

    if args.dry_run:
        return 0

    if args.execute:
        if diff["patch_count"] == 0:
            print("\nNothing to patch. Exiting.", file=sys.stderr)
            return 0
        result = _execute_patches(
            diff,
            token,
            limit=args.limit,
            only_from_not_started=args.only_from_not_started,
        )
        result["only_from_not_started"] = args.only_from_not_started
        report_path = REPO_ROOT / "artifacts" / "notion" / "plan_status_recovery_execute.json"
        report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(
            f"\nExecute report: {report_path}\n"
            f"  attempted: {result['attempted']}\n"
            f"  patched: {result['patched_count']}\n"
            f"  failed: {result['fail_count']}",
            file=sys.stderr,
        )
        return 0 if result["fail_count"] == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
