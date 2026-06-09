#!/usr/bin/env python3
"""
check_plan_registration_freshness.py — Pre-commit gate (T7u) + cache refresher.

Three responsibilities:
    1. Fetch the Notion Plans DB snapshot and cache it at
       ``.claude/state/plan_registration_cache.json`` (TTL 1h).
    2. On pre-commit, fail when a newly-staged ``plans/<slug>-<6hex>.md``
       has no matching Notion Plans row (and the slug is not flagged as
       registered in the queue).
    3. (W4 plan-ssot-notion-pipeline-d2f7a1) Content-drift detection:
       compare the on-disk plan's sha256 digest to the stored digest in the
       queue row; flag plans whose content has drifted from the registered
       snapshot without a Notion re-sync.

CLI::

    python ops_scripts/ci/check_plan_registration_freshness.py
        # Pre-commit mode: checks staged plan files only.

    python ops_scripts/ci/check_plan_registration_freshness.py --refresh
        # Force-refresh the cache from Notion, regardless of staleness.

    python ops_scripts/ci/check_plan_registration_freshness.py --all
        # Full-repo drift scan (registration + content-digest drift).

    python ops_scripts/ci/check_plan_registration_freshness.py --digest-drift
        # Content-digest drift scan only (no registration check).

Modes:
    Advisory (default):  prints violations and exits 0.
    Fail-closed:         PLAN_REGISTRATION_FAIL_CLOSED=1 → exit 1 on violation.
    Content-drift close: PLAN_CONTENT_DRIFT_FAIL_CLOSED=1 → exit 1 on digest mismatch.
    Skip:                NOTION_API_KEY/NOTION_TOKEN unset AND no fresh cache → SKIP + exit 0.

Bypass: PLAN_REGISTRATION_BYPASS=1.

Constitutional tie-in: §36.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_plan_registration.py"

_PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
_NOTION_VERSION = "2025-09-03"
_QUERY_URL = f"https://api.notion.com/v1/data_sources/{_PLANS_DATA_SOURCE_ID}/query"


def _load_helper():
    if not HELPER_PATH.exists():
        raise RuntimeError(f"helper missing: {HELPER_PATH}")
    mod_name = "_plan_registration"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load _plan_registration helper")
    mod = importlib.util.module_from_spec(spec)
    # Register before exec — @dataclass introspects sys.modules[cls.__module__].
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        raise
    return mod


# ---------------------------------------------------------------------------
# Notion fetch
# ---------------------------------------------------------------------------


def _env_token() -> str | None:
    for key in ("NOTION_API_KEY", "NOTION_TOKEN"):
        v = os.environ.get(key)
        if v:
            return v
    return None


def _iter_notion_plans(token: str) -> Iterable[dict[str, Any]]:
    start_cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"page_size": 100}
        if start_cursor is not None:
            payload["start_cursor"] = start_cursor
        req = urllib.request.Request(
            _QUERY_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": _NOTION_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Notion API HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Notion API URL error: {exc.reason}") from exc
        for row in body.get("results", []):
            yield row
        if not body.get("has_more"):
            return
        start_cursor = body.get("next_cursor")
        if not start_cursor:
            return


def _extract_plan_row(row: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    props = row.get("properties") or {}
    title_prop = props.get("Slug") or {}
    title = title_prop.get("title") or []
    if not isinstance(title, list) or not title:
        return None
    slug = str((title[0] or {}).get("plain_text") or "").strip()
    if not slug:
        return None
    status_prop = props.get("Status") or {}
    status = str(((status_prop.get("select") or {}).get("name") or "")).strip()
    exists_prop = props.get("Exists On Disk") or {}
    exists = bool(exists_prop.get("checkbox"))
    ai_prop = props.get("AI Summary ") or props.get("AI Summary") or {}
    ai_rt = ai_prop.get("rich_text") or []
    ai_text = "".join(
        str((chunk or {}).get("plain_text") or "") for chunk in ai_rt if isinstance(chunk, dict)
    ).strip()
    return slug, {
        "status": status,
        "page_id": row.get("id"),
        "exists_on_disk": exists,
        "has_ai_summary": bool(ai_text),
    }


def _refresh_cache(helper) -> tuple[int, str | None]:
    """Fetch Notion and write cache. Returns (count, error)."""
    token = _env_token()
    if not token:
        return 0, "no_token"
    try:
        plans: dict[str, dict[str, Any]] = {}
        for row in _iter_notion_plans(token):
            extracted = _extract_plan_row(row)
            if extracted is None:
                continue
            slug, entry = extracted
            plans[slug] = entry
    except RuntimeError as exc:
        return 0, str(exc)
    helper.write_cache(plans)
    return len(plans), None


# ---------------------------------------------------------------------------
# W4 — content-drift detection
# ---------------------------------------------------------------------------


def content_drift_report(helper) -> list[dict[str, str]]:
    """Compare on-disk plan content_digest to the value stored in the queue row.

    For each on-disk plan that has a queue row with a non-None ``content_digest``,
    compute the current file's sha256 and compare.  Plans with no queue row, or
    queue rows with a None digest (legacy marker-based capture), are silently skipped
    — there is nothing to compare against.

    Returns a list of drift records::

        [
          {
            "slug": "my-plan-abc123",
            "stored_digest": "abcd1234...",   # digest in queue row
            "current_digest": "efgh5678...",  # digest of the current file
            "path": "plans/my-plan-abc123.md",
          },
          ...
        ]

    An empty list means no content-drift was detected among plans with stored digests.
    """
    import hashlib as _hashlib
    rows = helper._read_queue()
    slug_to_row: dict[str, dict] = {r["slug"]: r for r in rows if r.get("slug")}
    drifted: list[dict[str, str]] = []
    for slug in helper.list_on_disk_plans():
        row = slug_to_row.get(slug)
        if row is None:
            continue
        stored = (row.get("content_digest") or "").strip()
        if not stored:
            continue  # no digest recorded — skip (legacy or marker-only capture)
        # Locate the plan file (canonical plans/ or legacy .claude/plans/).
        file_path = helper.plan_file_path(slug)
        plan_file = REPO_ROOT / file_path.replace("/", os.sep)
        if not plan_file.is_file():
            continue
        try:
            content = plan_file.read_text(encoding="utf-8")
        except OSError:
            continue
        current = _hashlib.sha256(content.encode("utf-8")).hexdigest()
        if current != stored:
            drifted.append({
                "slug": slug,
                "stored_digest": stored,
                "current_digest": current,
                "path": file_path,
            })
    return drifted


# ---------------------------------------------------------------------------
# Pre-commit file enumeration
# ---------------------------------------------------------------------------


def _staged_new_plans() -> list[str]:
    """Return slugs of newly-added `.claude/plans/*.md` files in the index."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
            cwd=REPO_ROOT,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []
    slugs: list[str] = []
    for line in result.stdout.splitlines():
        p = line.strip()
        # Forward-only relocation (c1a17d): canonical plans/ + legacy .claude/plans/.
        if not (p.startswith("plans/") or p.startswith(".claude/plans/")) or not p.endswith(".md"):
            continue
        name = Path(p).name
        import re as _re
        m = _re.match(r"^(?P<slug>[a-z0-9][a-z0-9-]*-[0-9a-f]{6})\.md$", name)
        if m:
            slugs.append(m.group("slug"))
    return slugs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _fail_closed() -> bool:
    return os.environ.get("PLAN_REGISTRATION_FAIL_CLOSED", "").strip() in {"1", "true", "TRUE", "yes"}


def _drift_fail_closed() -> bool:
    return os.environ.get("PLAN_CONTENT_DRIFT_FAIL_CLOSED", "").strip() in {"1", "true", "TRUE", "yes"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true",
                        help="Force refresh of the local cache from Notion")
    parser.add_argument("--all", action="store_true",
                        help="Full-repo drift scan (registration + digest drift)")
    parser.add_argument("--digest-drift", action="store_true",
                        help="Content-digest drift scan only (W4)")
    args = parser.parse_args(argv)

    if os.environ.get("PLAN_REGISTRATION_BYPASS") == "1":
        print("[check_plan_registration_freshness] BYPASS active — skipping.", file=sys.stderr)
        return 0

    try:
        helper = _load_helper()
    except RuntimeError as exc:
        print(f"[check_plan_registration_freshness] ERROR — {exc}", file=sys.stderr)
        return 1 if _fail_closed() else 0

    # --digest-drift mode: content-drift scan only, no registration check.
    if args.digest_drift and not args.all:
        drifted = content_drift_report(helper)
        if not drifted:
            print("[check_plan_registration_freshness] OK — no content-digest drift detected.")
            return 0
        print(
            f"[check_plan_registration_freshness] CONTENT_DRIFT — "
            f"{len(drifted)} plan(s) have diverged from their registered digest:",
            file=sys.stderr,
        )
        for item in drifted:
            print(
                f"  - {item['slug']}  stored={item['stored_digest'][:12]}..."
                f"  current={item['current_digest'][:12]}..."
                f"  path={item['path']}",
                file=sys.stderr,
            )
        print(
            "\nFix: plan was edited after registration without an AI Summary patch.\n"
            "  Re-save the plan to trigger the W3 re-sync hook, or run:\n"
            "    python tools/notion/plan_creation_helper.py --patch-digest <slug>\n"
            "Bypass: PLAN_REGISTRATION_BYPASS=1",
            file=sys.stderr,
        )
        if _drift_fail_closed():
            return 1
        print("[check_plan_registration_freshness] content-drift advisory — exiting 0", file=sys.stderr)
        return 0

    cache = helper.read_cache()
    need_refresh = args.refresh or not helper.cache_is_fresh(cache)
    if need_refresh:
        count, err = _refresh_cache(helper)
        if err:
            # Cache unavailable. For pre-commit: fall back to existing cache
            # if present (even if stale), else SKIP (advisory).
            if err == "no_token" and cache is None:
                print(
                    "[check_plan_registration_freshness] SKIP — "
                    "NOTION_API_KEY unset and no local cache."
                )
                return 0
            if err == "no_token":
                print(
                    "[check_plan_registration_freshness] WARN — NOTION_API_KEY unset; "
                    "using stale cache.",
                    file=sys.stderr,
                )
            else:
                print(
                    f"[check_plan_registration_freshness] WARN — refresh failed ({err}); "
                    f"continuing with existing cache.",
                    file=sys.stderr,
                )
        else:
            print(
                f"[check_plan_registration_freshness] cache refreshed "
                f"({count} Plans rows)"
            )
            cache = helper.read_cache()

    # Choose scope.
    if args.all:
        slugs_to_check = helper.list_on_disk_plans()
        scope = "all on-disk plans"
    else:
        slugs_to_check = _staged_new_plans()
        if not slugs_to_check:
            print("[check_plan_registration_freshness] OK — no staged plan files.")
            return 0
        scope = "staged plan files"

    violations: list[tuple[str, str, str | None]] = []
    for slug in slugs_to_check:
        res = helper.check_registration(slug, cache=cache)
        if not res.registered:
            violations.append((slug, res.source, res.reason))

    exit_code = 0
    if not violations:
        print(
            f"[check_plan_registration_freshness] OK — {len(slugs_to_check)} "
            f"{scope} all registered."
        )
    else:
        print(
            f"[check_plan_registration_freshness] VIOLATION — {len(violations)} of "
            f"{len(slugs_to_check)} {scope} lack a Notion Plans DB row:",
            file=sys.stderr,
        )
        for slug, source, reason in violations:
            print(f"  - {slug}  (source={source}, reason={reason})", file=sys.stderr)

        print(
            "\nFix: API-post-page into Plans DB (data source "
            f"{_PLANS_DATA_SOURCE_ID})\n"
            "  with Slug, Status (Not Started), Exists On Disk=true, Plan File Path,\n"
            "  Summary, AI Summary. See .claude/rules/plan-registration-enforcement.md.\n"
            "Bypass: PLAN_REGISTRATION_BYPASS=1",
            file=sys.stderr,
        )
        if _fail_closed():
            exit_code = 1
        else:
            print("[check_plan_registration_freshness] advisory mode — continuing", file=sys.stderr)

    # W4 content-drift check when --all (appended; does NOT override registration exit_code).
    if args.all or args.digest_drift:
        drifted = content_drift_report(helper)
        if drifted:
            print(
                f"[check_plan_registration_freshness] CONTENT_DRIFT — "
                f"{len(drifted)} plan(s) have content diverged from registered digest:",
                file=sys.stderr,
            )
            for item in drifted:
                print(
                    f"  - {item['slug']}  stored={item['stored_digest'][:12]}..."
                    f"  current={item['current_digest'][:12]}..."
                    f"  path={item['path']}",
                    file=sys.stderr,
                )
            if _drift_fail_closed() and exit_code == 0:
                exit_code = 1
        else:
            print(
                f"[check_plan_registration_freshness] OK (digest-drift) — "
                f"no content-digest drift detected among plans with stored digests."
            )

    # Notion orphan report when --all.
    if args.all:
        drift = helper.drift_report(cache=cache)
        orphans = drift.get("notion_active_not_on_disk", [])
        if orphans:
            print(
                f"[check_plan_registration_freshness] WARN — "
                f"{len(orphans)} Notion active row(s) without on-disk file:",
                file=sys.stderr,
            )
            for s in orphans:
                print(f"  - {s}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
