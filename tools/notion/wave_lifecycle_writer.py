#!/usr/bin/env python3
"""
wave_lifecycle_writer.py — Direct-HTTP Notion writer for plan/wave lifecycle.

Bypasses the Notion MCP layer entirely (constitutional §25 does not apply —
no MCP tool invocation, no `<invoke name="mcp*_API-*">` tags emitted).

Operations:
  - find_plan_page(slug)        — slug -> page_id via Plans DB query
  - patch_status(slug, status)  — Status field flip with taxonomy validation
  - append_summary(slug, line)  — read-modify-write append to Summary rich_text
  - apply_spec(spec)            — execute a NotionPatchSpec end-to-end
  - emit_from_marker(text)      — parse markers, decide specs, apply

Failure mode: fail-soft. HTTP errors logged + exit 0 (wave execution must
never block on Notion). NOTION_TOKEN missing also exits 0 with a warning.

CLI::

    python tools/notion/wave_lifecycle_writer.py --slug <s> --kind wave_complete --wave 3
    python tools/notion/wave_lifecycle_writer.py --slug <s> --kind plan_complete
    python tools/notion/wave_lifecycle_writer.py --slug <s> --kind wave_start --wave 1
    python tools/notion/wave_lifecycle_writer.py --emit-from-stdin   # read marker text
    python tools/notion/wave_lifecycle_writer.py --slug <s> --kind plan_complete --dry-run

Bypass: WAVE_LIFECYCLE_NOTION_BYPASS=1 (skip writer side-effects, log only).

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W1.P1.2).
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
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"))

from _notion_constants import (  # noqa: E402
    NOTION_API_VERSION,
    NOTION_BASE,
    PLANS_DATA_SOURCE_ID,
    query_url,
)

from tools.notion._wave_lifecycle_helpers import (  # noqa: E402
    CANONICAL_STATUSES,
    NotionPatchSpec,
    PROP_AI_SUMMARY,
    PROP_SLUG,
    PROP_STATUS,
    PROP_SUMMARY,
    SLUG_RE,
    WaveLifecycleMarker,
    coalesce_specs,
    parse_wave_lifecycle_markers,
    patch_for_marker,
)
from tools.notion._plan_registration_helpers import log_plans_db_write  # noqa: E402  DS-1

LOG_PATH = REPO_ROOT / "artifacts" / "governance" / "wave_lifecycle_notion.jsonl"

# Notion REST endpoints
PAGE_URL_FMT = f"{NOTION_BASE}/pages/{{}}"
DS_QUERY_URL = query_url(PLANS_DATA_SOURCE_ID)

# HTTP knobs (mirror tools/notion/apply_plan_derived_status.py).
TIMEOUT_S = 15.0
THROTTLE_S = 0.35

# Property max sizes (Notion REST API limits).
RICH_TEXT_BLOCK_MAX = 2000  # per text block; we split if longer.
SUMMARY_MAX_BLOCKS = 100    # per property; trim oldest log lines if exceeded.


# ---------------------------------------------------------------------------
# Logging (best-effort; never raises)
# ---------------------------------------------------------------------------


def _log(event: dict[str, Any]) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **event,
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Token + headers
# ---------------------------------------------------------------------------


def _token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


# ---------------------------------------------------------------------------
# Plans DB lookup — slug -> (page_id, properties)
# ---------------------------------------------------------------------------


def _post_json(url: str, body: dict[str, Any], token: str) -> tuple[bool, Any, str]:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return True, payload, "ok"
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", "replace")[:300]
        return False, None, f"http_{exc.code}:{body_text}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, None, f"net:{exc!r}"
    except json.JSONDecodeError as exc:
        return False, None, f"json:{exc!r}"


def _patch_json(url: str, body: dict[str, Any], token: str) -> tuple[bool, str]:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="PATCH",
        headers=_headers(token),
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            resp.read()
        return True, "ok"
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", "replace")[:300]
        return False, f"http_{exc.code}:{body_text}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"net:{exc!r}"


def find_plan_page(slug: str, token: str) -> tuple[str | None, dict[str, Any], str]:
    """Look up a Plans DB row by slug.

    Returns ``(page_id, properties, message)``. On failure or no match,
    ``page_id`` is None.
    """
    if not slug or not SLUG_RE.match(slug):
        return None, {}, "invalid_slug"
    body = {
        "filter": {
            "property": "Slug",
            "title": {"equals": slug},
        },
        "page_size": 2,
    }
    ok, payload, msg = _post_json(DS_QUERY_URL, body, token)
    if not ok or payload is None:
        return None, {}, msg
    results = payload.get("results") or []
    if not results:
        return None, {}, "not_found"
    if len(results) > 1:
        # Defensive: prefer the most-recently-edited.
        results.sort(key=lambda r: r.get("last_edited_time") or "", reverse=True)
    page = results[0]
    page_id = page.get("id")
    if not isinstance(page_id, str):
        return None, {}, "missing_page_id"

    # ── Slug cross-check (cardinal safety gate) ──────────────────────────────
    # Notion's filter is exact-match on title, but we verify the returned page's
    # own Slug property matches the queried slug.  This blocks any wrong-plan
    # patch under DB corruption, Notion API drift, or duplicate-slug collisions.
    props = page.get("properties") or {}
    returned_slug = _extract_slug_from_properties(props)
    if returned_slug is not None and returned_slug != slug:
        _log(
            {
                "event": "find_plan_page_slug_mismatch",
                "queried_slug": slug,
                "returned_slug": returned_slug,
                "page_id": page_id,
            }
        )
        return None, {}, f"slug_mismatch:queried={slug!r} returned={returned_slug!r}"

    return page_id, props, "ok"


# ---------------------------------------------------------------------------
# rich_text helpers — read-modify-write append
# ---------------------------------------------------------------------------


def _rich_text_plain(prop_value: dict[str, Any]) -> str:
    """Concatenate plain_text from a rich_text property into a single string."""
    if not isinstance(prop_value, dict):
        return ""
    rt = prop_value.get("rich_text") or []
    parts: list[str] = []
    for blk in rt:
        if isinstance(blk, dict):
            txt = blk.get("plain_text")
            if isinstance(txt, str):
                parts.append(txt)
    return "".join(parts)


def _rich_text_blocks(content: str) -> list[dict[str, Any]]:
    """Split *content* into rich_text blocks of at most ``RICH_TEXT_BLOCK_MAX`` chars."""
    if not content:
        return []
    blocks: list[dict[str, Any]] = []
    for i in range(0, len(content), RICH_TEXT_BLOCK_MAX):
        chunk = content[i : i + RICH_TEXT_BLOCK_MAX]
        blocks.append({"type": "text", "text": {"content": chunk}})
    return blocks


def _trim_summary_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only the last ``SUMMARY_MAX_BLOCKS`` blocks to stay under the API cap."""
    if len(blocks) <= SUMMARY_MAX_BLOCKS:
        return blocks
    return blocks[-SUMMARY_MAX_BLOCKS:]


def _build_summary_property(existing: str, append_line: str) -> dict[str, Any]:
    sep = "\n" if existing and not existing.endswith("\n") else ""
    new_text = f"{existing}{sep}{append_line}"
    blocks = _trim_summary_blocks(_rich_text_blocks(new_text))
    return {PROP_SUMMARY: {"rich_text": blocks}}


# ---------------------------------------------------------------------------
# High-level operations
# ---------------------------------------------------------------------------


def apply_spec(
    spec: NotionPatchSpec,
    *,
    dry_run: bool = False,
    token: str | None = None,
) -> tuple[bool, str]:
    """Execute a NotionPatchSpec against the Plans DB.

    Returns (ok, message). Fail-soft: any HTTP error returns ``ok=False``
    plus the reason; the caller is responsible for logging. The writer's
    own log captures the same.
    """
    if spec.is_noop:
        _log({"event": "apply_spec_noop", "slug": spec.slug, "reason": spec.reason})
        return True, "noop"

    if dry_run:
        _log(
            {
                "event": "apply_spec_dry_run",
                "slug": spec.slug,
                "properties": list(spec.properties.keys()),
                "summary_append": spec.summary_append,
                "reason": spec.reason,
            }
        )
        return True, "dry_run"

    if token is None:
        token = _token()
    if not token:
        _log({"event": "apply_spec_no_token", "slug": spec.slug, "reason": spec.reason})
        return False, "no_notion_token"

    if os.environ.get("WAVE_LIFECYCLE_NOTION_BYPASS") == "1":
        _log(
            {
                "event": "apply_spec_bypass",
                "slug": spec.slug,
                "properties": list(spec.properties.keys()),
                "summary_append": spec.summary_append,
            }
        )
        return True, "bypass"

    page_id, properties, msg = find_plan_page(spec.slug, token)
    if page_id is None:
        _log({"event": "apply_spec_lookup_failed", "slug": spec.slug, "msg": msg})
        return False, f"lookup_failed:{msg}"

    # Build the merged properties payload.
    payload_props: dict[str, Any] = dict(spec.properties)

    if spec.summary_append:
        existing_text = _rich_text_plain(properties.get(PROP_SUMMARY, {}))
        payload_props.update(_build_summary_property(existing_text, spec.summary_append))

    if not payload_props:
        _log({"event": "apply_spec_empty_payload", "slug": spec.slug})
        return True, "empty_payload"

    ok, msg = _patch_json(
        PAGE_URL_FMT.format(page_id),
        {"properties": payload_props},
        token,
    )
    _log(
        {
            "event": "apply_spec_patch",
            "slug": spec.slug,
            "page_id": page_id,
            "properties": list(payload_props.keys()),
            "ok": ok,
            "msg": msg,
            "reason": spec.reason,
        }
    )
    if ok:
        # DS-1: unified Plans-DB write telemetry
        log_plans_db_write(
            event="patch_status",
            slug=spec.slug,
            writer="wave_lifecycle_writer",
            detail=f"props={list(payload_props.keys())} reason={spec.reason}",
        )
    return ok, msg


def patch_status(slug: str, status: str, *, dry_run: bool = False) -> tuple[bool, str]:
    """Convenience wrapper: flip Status to ``status`` (taxonomy-validated)."""
    if status not in CANONICAL_STATUSES:
        return False, f"invalid_status:{status}"
    spec = NotionPatchSpec(
        slug=slug,
        properties={PROP_STATUS: {"select": {"name": status}}},
        summary_append=None,
        reason=f"explicit_status_patch:{status}",
    )
    return apply_spec(spec, dry_run=dry_run)


def append_summary(slug: str, line: str, *, dry_run: bool = False) -> tuple[bool, str]:
    """Convenience wrapper: append a single line to Summary (read-modify-write)."""
    spec = NotionPatchSpec(
        slug=slug,
        properties={},
        summary_append=line,
        reason="explicit_summary_append",
    )
    return apply_spec(spec, dry_run=dry_run)


def emit_from_markers(
    text: str,
    *,
    dry_run: bool = False,
    token: str | None = None,
) -> list[tuple[str, bool, str]]:
    """Parse all wave-lifecycle markers from *text* and apply them in order.

    Returns one (slug, ok, msg) row per coalesced spec applied.
    Markers for the same slug are coalesced into a single PATCH.
    """
    markers: list[WaveLifecycleMarker] = parse_wave_lifecycle_markers(text)
    if not markers:
        return []

    if token is None:
        token = _token()

    # W1.P2 (plan-complete-notion-status-enforcement-a7e2d1): warn loudly when
    # token is absent so the silent-skip failure mode is observable.
    if not token:
        print(
            "[wave_lifecycle_writer] WARN: NOTION_TOKEN not set — "
            "wave lifecycle markers parsed but Notion PATCH will be skipped",
            file=sys.stderr,
        )
        _log({"event": "emit_from_markers_no_token_warn", "marker_count": len(markers)})

    # Look up current status per slug ONCE for the whole batch.
    current_status_by_slug: dict[str, str | None] = {}
    if token and not dry_run:
        for slug in {m.slug for m in markers}:
            page_id, props, _msg = find_plan_page(slug, token)
            current_status_by_slug[slug] = _extract_status(props) if page_id else None

    specs = [
        patch_for_marker(m, current_status_by_slug.get(m.slug))
        for m in markers
    ]
    coalesced = coalesce_specs(specs)

    rows: list[tuple[str, bool, str]] = []
    for slug, spec in coalesced.items():
        ok, msg = apply_spec(spec, dry_run=dry_run, token=token)
        rows.append((slug, ok, msg))
        time.sleep(THROTTLE_S)
    return rows


def _extract_slug_from_properties(properties: dict[str, Any]) -> str | None:
    """Extract the plain-text Slug value from a Notion page properties dict.

    Returns ``None`` when the property is absent or malformed (caller treats
    that as "unknown — skip cross-check" rather than "mismatch").
    """
    slug_prop = properties.get(PROP_SLUG) or {}
    if not isinstance(slug_prop, dict):
        return None
    title_list = slug_prop.get("title") or []
    parts: list[str] = []
    for blk in title_list:
        if isinstance(blk, dict):
            txt = blk.get("plain_text") or (blk.get("text") or {}).get("content", "")
            if isinstance(txt, str):
                parts.append(txt)
    result = "".join(parts).strip()
    return result if result else None


def _extract_status(properties: dict[str, Any]) -> str | None:
    status_prop = properties.get(PROP_STATUS) or {}
    if not isinstance(status_prop, dict):
        return None
    sel = status_prop.get("select")
    if isinstance(sel, dict):
        name = sel.get("name")
        if isinstance(name, str):
            return name
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", help="Plan slug (required unless --emit-from-stdin)")
    parser.add_argument(
        "--kind",
        choices=("wave_start", "wave_complete", "phase_complete", "plan_complete"),
        help="Marker kind to synthesize",
    )
    parser.add_argument("--wave", type=int, help="Wave number (for wave_*)")
    parser.add_argument("--phase", help="Phase id (for phase_complete)")
    parser.add_argument("--reason", help="Optional reason annotation")
    parser.add_argument(
        "--note",
        help=(
            "Optional high-signal one-liner appended to the Summary log line "
            "(e.g. '4 files, +12 tests, scope=summary-signal'). Capped at "
            "~240 chars; whitespace collapsed to a single line."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--emit-from-stdin",
        action="store_true",
        help="Read marker text from stdin and apply all parsed markers",
    )
    args = parser.parse_args(argv)

    if args.emit_from_stdin:
        text = sys.stdin.read()
        rows = emit_from_markers(text, dry_run=args.dry_run)
        if not rows:
            print("[wave_lifecycle_writer] no markers parsed", file=sys.stderr)
            return 0
        any_fail = False
        for slug, ok, msg in rows:
            tag = "OK" if ok else "FAIL"
            print(f"[wave_lifecycle_writer] {tag} slug={slug} msg={msg}", file=sys.stderr)
            any_fail = any_fail or not ok
        return 0 if not any_fail else 1

    if not args.slug or not args.kind:
        parser.error("--slug and --kind are required (or use --emit-from-stdin)")
        return 2

    marker = WaveLifecycleMarker(
        kind=args.kind,
        slug=args.slug,
        wave=args.wave,
        phase=args.phase,
        reason=args.reason,
        note=args.note,
    )

    token = _token() if not args.dry_run else None
    current_status: str | None = None
    if token and not args.dry_run:
        page_id, props, _msg = find_plan_page(args.slug, token)
        if page_id:
            current_status = _extract_status(props)

    spec = patch_for_marker(marker, current_status)
    ok, msg = apply_spec(spec, dry_run=args.dry_run, token=token)
    tag = "OK" if ok else "FAIL"
    print(
        f"[wave_lifecycle_writer] {tag} slug={args.slug} kind={args.kind} "
        f"msg={msg} reason={spec.reason}",
        file=sys.stderr,
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
