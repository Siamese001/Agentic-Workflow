#!/usr/bin/env python3
"""
check_plan_registration_freshness.py — Pre-commit gate (T7u) + cache refresher.

Two responsibilities:
    1. Fetch the Notion Plans DB snapshot and cache it at
       ``.claude/state/plan_registration_cache.json`` (TTL 1h).
    2. On pre-commit, fail when a newly-staged ``plans/<slug>-<6hex>.md``
       or legacy ``.claude/plans/<slug>-<6hex>.md``
       has no matching Notion Plans row (and the slug is not flagged as
       registered in the queue).

CLI::

    python ops_scripts/ci/check_plan_registration_freshness.py
        # Pre-commit mode: checks staged plan files only.

    python ops_scripts/ci/check_plan_registration_freshness.py --refresh
        # Force-refresh the cache from Notion, regardless of staleness.

    python ops_scripts/ci/check_plan_registration_freshness.py --all
        # Full-repo drift scan (on-disk vs Notion, both directions).

Modes:
    Fail-closed (DEFAULT): exit 1 on violation — disk plan and Notion row must be in tandem.
    Advisory:            PLAN_REGISTRATION_FAIL_CLOSED=0 (or false/no) → prints violations, exits 0.
    Skip:                NOTION_API_KEY/NOTION_TOKEN unset AND no fresh cache → SKIP + exit 0.

Bypass: PLAN_REGISTRATION_BYPASS=1.

Constitutional tie-in: §36.
"""

from __future__ import annotations

import argparse
import hashlib
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

sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance" / "scripts"))
from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION as _NOTION_VERSION,
    NOTION_BASE as _NOTION_BASE,
    PLANS_DATA_SOURCE_ID as _PLANS_DATA_SOURCE_ID,
)

_QUERY_URL = f"{_NOTION_BASE}/data_sources/{_PLANS_DATA_SOURCE_ID}/query"


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
# Content-drift detection (W4)
# ---------------------------------------------------------------------------


def content_drift_report(pr: Any) -> list[dict[str, str]]:
    """Return plans whose on-disk content digest differs from the digest recorded
    in the registration queue (i.e. the plan file was edited after registration).

    Each drift row: ``{slug, stored_digest, current_digest, path}``. Rows with a
    null/missing stored digest (legacy marker capture), no ``path``, or no on-disk
    file are skipped silently.
    """
    drift: list[dict[str, str]] = []
    for row in pr._read_queue():
        stored = row.get("content_digest")
        path = row.get("path")
        if not stored or not path:
            continue
        plan_file = REPO_ROOT / path
        if not plan_file.is_file():
            continue
        current = hashlib.sha256(plan_file.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        if current != stored:
            drift.append(
                {
                    "slug": str(row.get("slug") or ""),
                    "stored_digest": str(stored),
                    "current_digest": current,
                    "path": str(path),
                }
            )
    return drift


def _content_drift_fail_closed() -> bool:
    return os.environ.get("PLAN_CONTENT_DRIFT_FAIL_CLOSED", "").strip().lower() in {"1", "true", "yes"}


def _run_digest_drift() -> int:
    """``--digest-drift`` mode: report content drift. Advisory (exit 0) by default;
    fail-closed (exit 1) under ``PLAN_CONTENT_DRIFT_FAIL_CLOSED``."""
    try:
        helper = _load_helper()
    except RuntimeError as exc:
        print(f"[check_plan_registration_freshness] ERROR — {exc}", file=sys.stderr)
        return 1 if _content_drift_fail_closed() else 0
    drift = content_drift_report(helper)
    if not drift:
        print("[check_plan_registration_freshness] OK — no plan content drift.")
        return 0
    for row in drift:
        print(
            f"[check_plan_registration_freshness] CONTENT_DRIFT — {row['slug']} "
            f"({row['path']}): stored={row['stored_digest'][:12]} "
            f"current={row['current_digest'][:12]}",
            file=sys.stderr,
        )
    return 1 if _content_drift_fail_closed() else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _fail_closed() -> bool:
    # Tandem enforcement: fail-closed by DEFAULT (a disk plan must have a Notion row, and
    # vice-versa). Opt out to advisory with PLAN_REGISTRATION_FAIL_CLOSED=0 (or false/no).
    return os.environ.get("PLAN_REGISTRATION_FAIL_CLOSED", "").strip().lower() not in {"0", "false", "no"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true",
                        help="Force refresh of the local cache from Notion")
    parser.add_argument("--all", action="store_true",
                        help="Full-repo drift scan instead of staged-only")
    parser.add_argument("--digest-drift", action="store_true",
                        help="Report plans whose on-disk content digest drifted from the registered digest")
    args = parser.parse_args(argv)

    if os.environ.get("PLAN_REGISTRATION_BYPASS") == "1":
        print("[check_plan_registration_freshness] BYPASS active — skipping.", file=sys.stderr)
        return 0

    if args.digest_drift:
        return _run_digest_drift()

    try:
        helper = _load_helper()
    except RuntimeError as exc:
        print(f"[check_plan_registration_freshness] ERROR — {exc}", file=sys.stderr)
        return 1 if _fail_closed() else 0

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

    if not violations:
        print(
            f"[check_plan_registration_freshness] OK — {len(slugs_to_check)} "
            f"{scope} all registered."
        )
        # Drift report when --all
        if args.all:
            drift = helper.drift_report(cache=cache)
            orphans = drift.get("notion_active_not_on_disk", [])
            if orphans:
                print(
                    f"[check_plan_registration_freshness] WARN — "
                    f"{len(orphans)} Notion Live/Draft row(s) without on-disk file:",
                    file=sys.stderr,
                )
                for s in orphans:
                    print(f"  - {s}", file=sys.stderr)
        return 0

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
        "  with Slug, Status (Live|Draft), Exists On Disk=true, Plan File Path,\n"
        "  Summary, AI Summary. See .claude/rules/plan-registration-enforcement.md.\n"
        "Bypass: PLAN_REGISTRATION_BYPASS=1",
        file=sys.stderr,
    )

    if _fail_closed():
        return 1
    print("[check_plan_registration_freshness] advisory mode — exiting 0", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
