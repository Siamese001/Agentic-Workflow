#!/usr/bin/env python3
"""
_plan_registration.py — Plan→Notion registration helper (SSOT pure logic).

Shared by:
  - post_cursor_agent_plan_registration_capture.py (PLAN_CREATED marker capture)
  - pre_user_prompt_plan_registration_surface.py (proactive surface)
  - tools/cursor/wave_execution_state.py (wave-start block)
  - ops_scripts/ci/check_plan_registration_freshness.py (pre-commit gate)
  - ops_scripts/calibration/plan_registration_weekly_report.py (weekly drift)

State files:
  - .cursor/state/plan_registration_queue.jsonl
        Append-only log of PLAN_CREATED markers awaiting Notion registration.
        One row per slug; re-enqueue is idempotent.
  - .cursor/state/plan_registration_cache.json
        Snapshot of the Notion Plans DB keyed by slug. TTL 1h. Populated by
        the pre-commit gate / weekly report; consumed by the wave-start
        block when network is unavailable.

Row shape (queue)::

    {
      "slug": "my-plan-abc123",
      "path": ".claude/plans/my-plan-abc123.md",
      "declared_status": "Not Started",
      "captured_at": "2026-05-03T11:00:00Z",
      "registered": false,
      "registered_at": null
    }

Cache shape::

    {
      "fetched_at": "2026-05-03T11:00:00Z",
      "fetched_at_epoch": 1745236800.0,
      "plans": {
        "slug-a-aaaaaa": {
          "status": "In Progress",
          "page_id": "...",
          "exists_on_disk": true,
          "has_ai_summary": true
        },
        ...
      }
    }

Pure: no subprocess, no Notion API calls, no env reads. Specific
exceptions only. Constitutional tie-in: §36 (new).
"""

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".cursor" / "state"
QUEUE_PATH = STATE_DIR / "plan_registration_queue.jsonl"
CACHE_PATH = STATE_DIR / "plan_registration_cache.json"
PLANS_DIR = REPO_ROOT / ".claude" / "plans"

# Slug pattern: lowercase-slug-with-dashes-<6hex>
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*-[0-9a-f]{6}$")
# Plan filename shape
PLAN_FILE_RE = re.compile(r"^(?P<slug>[a-z0-9][a-z0-9-]*-[0-9a-f]{6})\.md$")

# Cache TTL (seconds). Cache considered fresh when fetched within this window.
CACHE_TTL_SECONDS = 3600  # 1 hour


@dataclass(frozen=True)
class RegistrationStatus:
    """Result of a registration check against the cache."""

    slug: str
    registered: bool
    status: str | None         # Notion Status field (In Progress/Not Started/Lower Priority/Waiting/Completed/Retired/Archived)
    source: str                # "cache" | "cache_stale" | "cache_missing" | "queue"
    reason: str | None         # Human-readable detail when registered=False


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_epoch() -> float:
    return time.time()


# ---------------------------------------------------------------------------
# On-disk plan enumeration
# ---------------------------------------------------------------------------


def list_on_disk_plans() -> list[str]:
    """Return sorted list of plan slugs present under .claude/plans/*.md."""
    if not PLANS_DIR.exists():
        return []
    slugs: list[str] = []
    try:
        for p in PLANS_DIR.iterdir():
            if not p.is_file() or p.suffix != ".md":
                continue
            m = PLAN_FILE_RE.match(p.name)
            if m:
                slugs.append(m.group("slug"))
    except OSError:
        return []
    return sorted(slugs)


def plan_file_path(slug: str) -> str:
    """Return repo-relative path for a slug. Does not check existence."""
    return f".claude/plans/{slug}.md"


# ---------------------------------------------------------------------------
# Queue (JSONL append-only)
# ---------------------------------------------------------------------------


def _read_queue() -> list[dict[str, Any]]:
    """Read all queue rows. Skips malformed lines. Missing file → []."""
    if not QUEUE_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with QUEUE_PATH.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict) and "slug" in row:
                    rows.append(row)
    except OSError:
        return []
    return rows


def _write_queue(rows: list[dict[str, Any]]) -> None:
    """Atomically rewrite queue from a full row list."""
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = QUEUE_PATH.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(QUEUE_PATH)


def enqueue_plan(slug: str, path: str, declared_status: str = "Not Started") -> bool:
    """
    Idempotently enqueue a PLAN_CREATED capture.

    Returns True if a new row was appended, False if the slug was already
    queued (regardless of its registered flag).
    """
    if not slug or not SLUG_RE.match(slug):
        raise ValueError(f"invalid slug: {slug!r}")
    rows = _read_queue()
    if any(r.get("slug") == slug for r in rows):
        return False
    rows.append({
        "slug": slug,
        "path": path,
        "declared_status": declared_status,
        "captured_at": _now_iso(),
        "registered": False,
        "registered_at": None,
    })
    _write_queue(rows)
    return True


def mark_registered(slug: str) -> bool:
    """Flip registered=True for a queued slug. Returns True if a row was updated."""
    rows = _read_queue()
    changed = False
    for r in rows:
        if r.get("slug") == slug and not r.get("registered"):
            r["registered"] = True
            r["registered_at"] = _now_iso()
            changed = True
    if changed:
        _write_queue(rows)
    return changed


def pending_registrations() -> list[dict[str, Any]]:
    """Return queue rows where registered=False."""
    return [r for r in _read_queue() if not r.get("registered")]


# ---------------------------------------------------------------------------
# Cache (JSON with TTL)
# ---------------------------------------------------------------------------


def read_cache() -> dict[str, Any] | None:
    """Return cache dict, or None when missing / malformed."""
    if not CACHE_PATH.exists():
        return None
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or "plans" not in data:
        return None
    return data


def cache_is_fresh(cache: dict[str, Any] | None, ttl_seconds: int = CACHE_TTL_SECONDS) -> bool:
    """True iff cache was fetched within ttl_seconds."""
    if not cache:
        return False
    fetched = cache.get("fetched_at_epoch")
    if not isinstance(fetched, (int, float)):
        return False
    return (_now_epoch() - float(fetched)) <= ttl_seconds


def write_cache(plans: dict[str, dict[str, Any]]) -> None:
    """Persist a fresh cache snapshot."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": _now_iso(),
        "fetched_at_epoch": _now_epoch(),
        "plans": plans,
    }
    tmp = CACHE_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CACHE_PATH)


# ---------------------------------------------------------------------------
# Core check — used by wave-start block and pre-commit gate
# ---------------------------------------------------------------------------


# Statuses that satisfy "registered" for the purpose of wave execution.
# Retired/Archived mean the plan is not actively tracked; a wave-start on
# such a plan should still block to force the operator to flip status first.
# Canonical per notion-plans-taxonomy.md §Status Criteria and Transition Rules.
ACTIVE_STATUSES: frozenset[str] = frozenset({"In Progress", "Not Started", "Lower Priority", "Waiting", "Completed"})


def check_registration(slug: str, cache: dict[str, Any] | None = None) -> RegistrationStatus:
    """
    Decide whether ``slug`` is registered, using the cache as source of truth.

    If cache is fresh:
      - plan present with status in ACTIVE_STATUSES → registered=True
      - plan present with Retired/Archived → registered=False, reason names the status
      - plan absent → registered=False, reason="not_in_notion_plans_db"
    If cache is stale/missing:
      - fall back to queue: if slug is queued and registered=True → registered=True
      - else registered=False, source="cache_missing"|"cache_stale"

    The wave-start block uses source to decide whether to fail-open
    (cache missing AND no Notion token available) or fail-closed.
    """
    if not slug or not SLUG_RE.match(slug):
        return RegistrationStatus(
            slug=slug, registered=False, status=None,
            source="cache_missing", reason="invalid_slug",
        )

    if cache is None:
        cache = read_cache()

    if cache_is_fresh(cache):
        plans = (cache or {}).get("plans", {})
        entry = plans.get(slug) if isinstance(plans, dict) else None
        if entry is None:
            # Cross-check queue — an in-flight registration counts as pending,
            # not as "never heard of". The queue flag flips after a successful
            # API-post-page, which is what we want to surface accurately.
            queue_rows = _read_queue()
            queued = next((r for r in queue_rows if r.get("slug") == slug), None)
            if queued and queued.get("registered"):
                return RegistrationStatus(
                    slug=slug, registered=True, status=None,
                    source="queue", reason="marked_registered_in_queue_awaiting_cache_refresh",
                )
            return RegistrationStatus(
                slug=slug, registered=False, status=None,
                source="cache", reason="not_in_notion_plans_db",
            )
        status = str(entry.get("status") or "")
        if status in ACTIVE_STATUSES:
            return RegistrationStatus(
                slug=slug, registered=True, status=status,
                source="cache", reason=None,
            )
        return RegistrationStatus(
            slug=slug, registered=False, status=status,
            source="cache", reason=f"status_is_{status or 'unknown'}",
        )

    # Cache stale or missing — fall back to queue.
    queue_rows = _read_queue()
    queued = next((r for r in queue_rows if r.get("slug") == slug), None)
    source = "cache_stale" if cache else "cache_missing"
    if queued and queued.get("registered"):
        return RegistrationStatus(
            slug=slug, registered=True, status=None,
            source="queue", reason="marked_registered_in_queue_cache_unavailable",
        )
    return RegistrationStatus(
        slug=slug, registered=False, status=None,
        source=source, reason="cache_unavailable_and_not_in_queue",
    )


# ---------------------------------------------------------------------------
# Drift detection — used by weekly report + pre-commit gate
# ---------------------------------------------------------------------------


def drift_report(cache: dict[str, Any] | None = None) -> dict[str, list[str]]:
    """
    Compare on-disk plans vs cached Notion snapshot.

    Returns::

        {
          "on_disk_not_in_notion": [slug, ...],      # missing registrations
          "notion_active_not_on_disk": [slug, ...],  # orphan In Progress/Not Started/Deferred rows
        }

    Callers decide whether staleness of cache itself is a blocker.
    """
    if cache is None:
        cache = read_cache()
    on_disk = set(list_on_disk_plans())
    notion_plans: dict[str, dict[str, Any]] = {}
    if isinstance(cache, dict):
        maybe = cache.get("plans")
        if isinstance(maybe, dict):
            notion_plans = maybe
    notion_active = {
        slug for slug, entry in notion_plans.items()
        if isinstance(entry, dict)
        and str(entry.get("status") or "") in ACTIVE_STATUSES
    }
    return {
        "on_disk_not_in_notion": sorted(on_disk - set(notion_plans.keys())),
        "notion_active_not_on_disk": sorted(notion_active - on_disk),
    }


# ---------------------------------------------------------------------------
# Utility: parse PLAN_CREATED markers (shared by post-hook + tests)
# ---------------------------------------------------------------------------


_PLAN_CREATED_RE = re.compile(
    r"^\s*PLAN_CREATED\s*:\s*(?P<body>.+?)\s*$",
    re.MULTILINE,
)
_PLAN_CREATED_KV_RE = re.compile(
    r"\b(?P<key>slug|path|status)="
    r"(?P<val>.*?)"
    r"(?=\s+(?:slug|path|status)=|\s*$)",
    re.DOTALL,
)


def parse_plan_created_markers(text: str) -> list[dict[str, str]]:
    """Parse all PLAN_CREATED markers from Cursor Agent response text.

    Returns a list of dicts with keys ``slug``, ``path``, ``status``.
    Rows missing ``slug`` are dropped; ``path`` and ``status`` default to
    derived / "Not Started" respectively. Never raises.
    """
    if not text:
        return []
    out: list[dict[str, str]] = []
    for m in _PLAN_CREATED_RE.finditer(text):
        body = m.group("body")
        fields: dict[str, str] = {}
        for kv in _PLAN_CREATED_KV_RE.finditer(body):
            fields[kv.group("key")] = kv.group("val").strip()
        slug = fields.get("slug", "").strip()
        if not slug or not SLUG_RE.match(slug):
            continue
        out.append({
            "slug": slug,
            "path": fields.get("path", plan_file_path(slug)).strip(),
            "status": fields.get("status", "Not Started").strip() or "Not Started",
        })
    return out


# ---------------------------------------------------------------------------
# Convenience for callers
# ---------------------------------------------------------------------------


def iter_unregistered_on_disk(cache: dict[str, Any] | None = None) -> Iterable[str]:
    """Yield slugs present on disk but not registered per the cache."""
    if cache is None:
        cache = read_cache()
    for slug in list_on_disk_plans():
        res = check_registration(slug, cache=cache)
        if not res.registered:
            yield slug
