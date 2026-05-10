"""
_plan_registration_helpers.py — Idempotent Plans-DB POST surface.

SSOT for: dedup-on-create logic for the Notion Plans database. ALL
Python callers that POST a new Plans row MUST route through
``register_plan_idempotent()``.

RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause B: 41 separate Notion writers
existed without coordinated dedup, leading to phantom duplicate rows for
11 slugs. This module is the new chokepoint.

Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P2).

Public surface
--------------

    find_active_plan_pages(slug, token, *, timeout=15.0)
        Return list of non-archived Plans rows matching ``slug``.
        ``[]`` when no match. Raises ``NotionAPIError`` on transport failure.

    register_plan_idempotent(slug, properties, token, *, dry_run=False)
        Idempotent POST. Decisions:
          - 0 active rows  -> POST a new row, return (page_id, "created")
          - 1 active row   -> return (page_id, "existed") — no write
          - 2+ active rows -> return ("", "duplicate_blocked") + log
        Never overwrites an existing row's properties (use a separate PATCH
        helper for that).

Pure-ish: only does HTTP via stdlib ``urllib``; no MCP, no shelling out.
Specific exception types only. Never raises on operator-recoverable
conditions (missing token, network blip) — returns the appropriate
sentinel + caller logs.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Late import keeps this module importable from any cwd.
sys.path.insert(0, str(REPO_ROOT / ".windsurf" / "scripts"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
    PLANS_DB_ID,
    query_url,
)

# ---------------------------------------------------------------------------
# Telemetry (W3.P2 hook point — every Plans-DB write lands here)
# ---------------------------------------------------------------------------

LOG_PATH = REPO_ROOT / "artifacts" / "windsurf" / "plans_db_writes.jsonl"

# HTTP knobs (mirrors wave_lifecycle_writer.py).
DEFAULT_TIMEOUT_S = 15.0

# Telemetry log rotation threshold (DS-4).
LOG_ROTATION_BYTES = 10 * 1024 * 1024  # 10 MB

# Cache path — mirrors _plan_registration.CACHE_PATH (DS-2).
_CACHE_PATH = REPO_ROOT / ".windsurf" / "state" / "plan_registration_cache.json"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class NotionAPIError(RuntimeError):
    """Raised when a Notion HTTP call fails in a non-recoverable way."""


@dataclass(frozen=True)
class RegistrationResult:
    page_id: str       # "" when blocked or failed
    action: str        # "created" | "existed" | "duplicate_blocked" | "no_token" | "api_error"
    detail: str        # human-readable message
    duplicates: tuple[str, ...] = ()  # page_ids when action == "duplicate_blocked"


# ---------------------------------------------------------------------------
# Logging — best-effort; never raises
# ---------------------------------------------------------------------------


def _rotate_if_large(path: Path, max_bytes: int = LOG_ROTATION_BYTES) -> None:
    """Rotate ``path`` to ``path.1`` when it exceeds ``max_bytes``.

    Never raises — rotation failure is silently swallowed to keep telemetry
    writes non-blocking.  DS-4 (notion-plans-db-hygiene-deferred-scope-d4f7c1).
    """
    try:
        if path.exists() and path.stat().st_size >= max_bytes:
            rotated = path.with_suffix(path.suffix + ".1")
            # Overwrite any previous rotation (keep only 1 backup).
            path.replace(rotated)
    except OSError:
        pass


def _log(event: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **event,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _rotate_if_large(LOG_PATH)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def log_plans_db_write(
    *,
    event: str,
    slug: str = "",
    page_id: str = "",
    writer: str = "unknown",
    status_before: str | None = None,
    status_after: str | None = None,
    ok: bool = True,
    detail: str = "",
    **extra: Any,
) -> None:
    """Public telemetry helper — every Plans-DB writer SHOULD call this.

    Args:
        event: Short event name (e.g. "patch_status", "archive_dup", "register_created").
        slug: Plan slug being written.
        page_id: Notion page id.
        writer: Caller identifier (e.g. ``"triage_plans_duplicates.py"``).
        status_before: Previous Status select value (when known).
        status_after: New Status select value (when applicable).
        ok: Whether the write succeeded.
        detail: Free-form message (HTTP error string, reason code, etc.).
        **extra: Additional fields merged into the row.

    Writes to ``artifacts/windsurf/plans_db_writes.jsonl``. Never raises.

    RCA NOTION_PLANS_STATUS_RCA_2026-05-10 §8 (telemetry mandate).
    """
    row: dict[str, Any] = {
        "event": event,
        "writer": writer,
        "slug": slug,
        "page_id": page_id,
        "ok": ok,
    }
    if status_before is not None:
        row["status_before"] = status_before
    if status_after is not None:
        row["status_after"] = status_after
    if detail:
        row["detail"] = detail
    row.update(extra)
    _log(row)


# ---------------------------------------------------------------------------
# HTTP primitives
# ---------------------------------------------------------------------------


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def _post_json(
    url: str,
    body: dict[str, Any],
    token: str,
    *,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", "replace")[:300]
        raise NotionAPIError(f"http_{exc.code}:{body_text}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise NotionAPIError(f"net:{exc!r}") from exc
    except json.JSONDecodeError as exc:
        raise NotionAPIError(f"json:{exc!r}") from exc


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------


def find_active_plan_pages(
    slug: str,
    token: str,
    *,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> list[dict[str, Any]]:
    """Return non-archived Plans rows whose Slug title equals ``slug``.

    Excludes ``in_trash=True`` rows. Returns ``[]`` when no match.
    Raises ``NotionAPIError`` on transport failure.
    """
    if not slug:
        return []
    body = {
        "filter": {"property": "Slug", "title": {"equals": slug}},
        "page_size": 10,
    }
    payload = _post_json(query_url(PLANS_DATA_SOURCE_ID), body, token, timeout=timeout)
    results = payload.get("results") or []
    # Notion's ``in_trash`` flag (legacy: ``archived``) — exclude both shapes.
    return [
        r for r in results
        if not r.get("in_trash", False) and not r.get("archived", False)
    ]


def _update_cache_entry(
    slug: str,
    page_id: str,
    status: str,
    cache_path: Path = _CACHE_PATH,
) -> None:
    """Patch the local plan registration cache with a newly created row.

    Uses atomic tmp→replace to avoid partial writes under concurrent access.
    Never raises — cache write failures are silently swallowed.

    DS-2 (notion-plans-db-hygiene-deferred-scope-d4f7c1): cache-on-write
    discipline ensures the dedup guard and the dup-surface hook see the new
    row immediately, without waiting for the next full cache refresh cycle.
    """
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if cache_path.exists():
            try:
                data: dict[str, Any] = json.loads(
                    cache_path.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                data = {}
        else:
            data = {}

        if not isinstance(data, dict):
            data = {}
        if "plans" not in data or not isinstance(data["plans"], dict):
            data["plans"] = {}
        if "fetched_at" not in data:
            from datetime import datetime, timezone
            data["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            data["fetched_at_epoch"] = datetime.now(timezone.utc).timestamp()

        data["plans"][slug] = {
            "page_id": page_id,
            "status": status,
        }

        tmp = cache_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(cache_path)
    except OSError:
        pass


def register_plan_idempotent(
    slug: str,
    properties: dict[str, Any],
    token: str | None = None,
    *,
    dry_run: bool = False,
    timeout: float = DEFAULT_TIMEOUT_S,
    writer: str = "unknown",
) -> RegistrationResult:
    """Idempotently register a Plans row.

    Args:
        slug: Plan slug (e.g. ``my-plan-abc123``). Used for the dedup query.
        properties: Notion ``properties`` payload for the new row.
            Should include ``Slug`` (title) and ``Status`` (select). Caller
            owns the full schema — this helper does NOT enforce field shape.
        token: NOTION_TOKEN; auto-resolved from env when None.
        dry_run: When True, never POST; report what would happen.
        timeout: HTTP timeout in seconds.
        writer: Caller identifier for telemetry (e.g. ``"register_ondisk_plans_batch.py"``).

    Returns:
        RegistrationResult with action ∈ ``{"created", "existed",
        "duplicate_blocked", "no_token", "api_error", "dry_run"}``.

    Never raises. Never patches an existing row (caller's responsibility).
    """
    token = token or os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token:
        result = RegistrationResult(
            page_id="", action="no_token",
            detail="NOTION_TOKEN/NOTION_API_KEY not set",
        )
        _log({"event": "register_no_token", "slug": slug, "writer": writer})
        return result

    # Step 1: dedup query.
    try:
        existing = find_active_plan_pages(slug, token, timeout=timeout)
    except NotionAPIError as exc:
        _log({
            "event": "register_query_failed", "slug": slug,
            "writer": writer, "error": str(exc),
        })
        return RegistrationResult(page_id="", action="api_error", detail=str(exc))

    if len(existing) >= 2:
        page_ids = tuple(p.get("id", "") for p in existing if p.get("id"))
        _log({
            "event": "register_duplicate_blocked",
            "slug": slug,
            "writer": writer,
            "page_ids": list(page_ids),
        })
        return RegistrationResult(
            page_id="",
            action="duplicate_blocked",
            detail=(
                f"{len(existing)} active Plans rows already exist for slug={slug!r} "
                f"(page_ids={list(page_ids)}); refusing to create another. "
                f"Resolve duplicates before retrying."
            ),
            duplicates=page_ids,
        )

    if len(existing) == 1:
        page_id = existing[0].get("id", "")
        _log({
            "event": "register_existed",
            "slug": slug,
            "writer": writer,
            "page_id": page_id,
        })
        return RegistrationResult(
            page_id=page_id,
            action="existed",
            detail=f"Plans row already exists for slug={slug!r}; no write performed.",
        )

    # Step 2: no row exists. POST a new one.
    if dry_run:
        _log({"event": "register_dry_run", "slug": slug, "writer": writer})
        return RegistrationResult(
            page_id="", action="dry_run",
            detail=f"dry_run: would POST new row for slug={slug!r}",
        )

    body = {
        "parent": {"type": "database_id", "database_id": PLANS_DB_ID},
        "properties": properties,
    }
    try:
        payload = _post_json(f"{NOTION_BASE}/pages", body, token, timeout=timeout)
    except NotionAPIError as exc:
        _log({
            "event": "register_post_failed",
            "slug": slug, "writer": writer, "error": str(exc),
        })
        return RegistrationResult(page_id="", action="api_error", detail=str(exc))

    page_id = payload.get("id", "")
    _log({
        "event": "register_created",
        "slug": slug,
        "writer": writer,
        "page_id": page_id,
    })
    # DS-2: update cache immediately on successful POST so dedup guards
    # see the new row without waiting for the next full refresh cycle.
    _created_status = (
        (properties.get("Status") or {})
        .get("select", {})
        .get("name", "Not Started")
    )
    _update_cache_entry(slug, page_id, _created_status)
    return RegistrationResult(
        page_id=page_id,
        action="created",
        detail=f"Created new Plans row for slug={slug!r}",
    )


__all__ = [
    "NotionAPIError",
    "RegistrationResult",
    "find_active_plan_pages",
    "register_plan_idempotent",
    "log_plans_db_write",
    "LOG_PATH",
    "LOG_ROTATION_BYTES",
    "_rotate_if_large",
    "_update_cache_entry",
    "_CACHE_PATH",
]
