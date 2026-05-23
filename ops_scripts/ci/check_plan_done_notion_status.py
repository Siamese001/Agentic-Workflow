#!/usr/bin/env python3
"""
check_plan_done_notion_status.py — NP-DONE CI gate.

Detects plans whose on-disk wave table shows all waves ✅ DONE but whose
Notion Plans DB row does NOT have Status = "Completed".

Root cause closed: plan ``apps-lic-quarantine-u0-coverage-review-d9f4a2``
completed all 11 waves but Notion remained ``Archived`` because
``wave_execution_state.py complete`` was never called and the
``PLAN_COMPLETE:`` hook had no token (fail-open, silent).  RCA documented
in plan ``plan-complete-notion-status-enforcement-a7e2d1`` (W2.P1).

Algorithm
---------
1. Enumerate ``.cursor/plans/*.md`` (skipping ``_archive/`` and
   ``_orphan_review/`` subdirectories).
2. For each plan, parse the Wave Structure table for status cells.
   A plan is "all-waves-done on disk" when:
   - At least one wave row exists, AND
   - Every wave row has status ✅ DONE (or ✅ variants).
3. For each all-done plan, look up its Notion slug in the Plans DB.
4. Report ERROR when Notion status ≠ ``Completed`` (or row not found).

Advisory by default.  Fail-closed: ``NP_PLAN_DONE_STATUS_FAIL_CLOSED=1``.
Bypass:            ``NP_PLAN_DONE_STATUS_BYPASS=1``.
Skips when NOTION_TOKEN / NOTION_API_KEY unset (offline CI safe).

Output: ``artifacts/ci/plan_done_notion_status.json``.

Plan: plan-complete-notion-status-enforcement-a7e2d1 (W2.P1).
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

REPORT_PATH = REPO_ROOT / "artifacts" / "ci" / "plan_done_notion_status.json"
PLANS_DIR = REPO_ROOT / ".cursor" / "plans"
SKIP_SUBDIRS = {"_archive", "_orphan_review"}

# Notion API
try:
    sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts"))
    from _notion_constants import (  # type: ignore[import-not-found]
        NOTION_API_VERSION,
        NOTION_BASE,
        PLANS_DATA_SOURCE_ID,
        query_url,
    )
    DS_QUERY_URL = query_url(PLANS_DATA_SOURCE_ID)
    _NOTION_CONSTANTS_OK = True
except ImportError:
    NOTION_API_VERSION = "2022-06-28"
    NOTION_BASE = "https://api.notion.com/v1"
    DS_QUERY_URL = f"{NOTION_BASE}/databases/6aba34d9-4d0b-4f4c-b956-b2bdea541ca9/query"
    _NOTION_CONSTANTS_OK = False

NOTION_TIMEOUT = 15.0
COMPLETED_STATUS = "Completed"
DONE_CELL_RE = re.compile(r"✅")
TODO_LIKE_CELL_RE = re.compile(r"🔲|🔄|❌|BLOCKED|TODO|IN PROGRESS", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Wave-table parser
# ---------------------------------------------------------------------------

_WAVE_ROW_RE = re.compile(
    r"^\s*\|\s*W\d+",  # row whose first cell starts with W<digit>
    re.IGNORECASE,
)
_STATUS_CELL_RE = re.compile(r"\|\s*(✅[^|]*|🔲[^|]*|🔄[^|]*|❌[^|]*)\s*\|")


def _parse_wave_status(content: str) -> tuple[bool, bool]:
    """Return (has_wave_rows, all_done).

    *has_wave_rows* — at least one wave row found in a Wave Structure table.
    *all_done*      — every wave row has a ✅ DONE status cell.
    """
    wave_rows: list[str] = []
    in_wave_table = False
    for line in content.splitlines():
        stripped = line.strip()
        # Detect the Wave Structure table header
        if re.search(r"\|\s*Wave\s*\|", stripped, re.IGNORECASE):
            in_wave_table = True
            continue
        if in_wave_table:
            if not stripped.startswith("|"):
                # Table ended
                in_wave_table = False
                continue
            if _WAVE_ROW_RE.match(stripped):
                wave_rows.append(stripped)

    if not wave_rows:
        return False, False

    for row in wave_rows:
        # Rows like | W1 | ... | ✅ DONE | or | W1 | ... | 🔲 TODO |
        # Extract all status-like cells and check if any non-done cell exists.
        if TODO_LIKE_CELL_RE.search(row):
            return True, False  # at least one non-done row
        if not DONE_CELL_RE.search(row):
            # Row has no recognisable status cell — treat as unknown/not done
            return True, False
    return True, True


# ---------------------------------------------------------------------------
# Notion lookup
# ---------------------------------------------------------------------------


def _token() -> str | None:
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }


def _query_notion_status(slug: str, token: str) -> str | None:
    """Return the Notion Status string for *slug*, or None on any failure."""
    body = json.dumps(
        {"filter": {"property": "Slug", "title": {"equals": slug}}, "page_size": 2}
    ).encode("utf-8")
    req = urllib.request.Request(
        DS_QUERY_URL, data=body, method="POST", headers=_headers(token)
    )
    try:
        with urllib.request.urlopen(req, timeout=NOTION_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError):
        return None

    results = payload.get("results") or []
    if not results:
        return None
    props = results[0].get("properties") or {}
    status_prop = props.get("Status") or {}
    sel = status_prop.get("select") or {}
    name = sel.get("name")
    return name if isinstance(name, str) else None


# ---------------------------------------------------------------------------
# Slug extractor
# ---------------------------------------------------------------------------

_FRONTMATTER_SLUG_RE = re.compile(r"^plan_id:\s*(\S+)", re.MULTILINE)
_FILENAME_SLUG_RE = re.compile(r"^(.+)-[0-9a-f]{6}$")


def _extract_slug(plan_file: Path) -> str | None:
    """Derive slug from frontmatter ``plan_id:`` or from the filename."""
    try:
        content = plan_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = _FRONTMATTER_SLUG_RE.search(content[:500])
    if m:
        return m.group(1).strip()
    stem = plan_file.stem
    if _FILENAME_SLUG_RE.match(stem):
        return stem
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run(
    *,
    fail_closed: bool = False,
    dry_run: bool = False,
) -> int:
    """Run the gate. Returns exit code (0 = pass, 1 = violations + fail_closed)."""
    bypass = os.environ.get("NP_PLAN_DONE_STATUS_BYPASS") == "1"
    if bypass:
        print("[NP-DONE] BYPASS active — skipping", file=sys.stderr)
        _write_report({"status": "bypass", "violations": []})
        return 0

    token = _token()
    if not token:
        print(
            "[NP-DONE] SKIP — NOTION_TOKEN / NOTION_API_KEY not set (offline CI)",
            file=sys.stderr,
        )
        _write_report({"status": "skipped_no_token", "violations": []})
        return 0

    if not PLANS_DIR.is_dir():
        print(f"[NP-DONE] WARN: plans dir not found: {PLANS_DIR}", file=sys.stderr)
        _write_report({"status": "skipped_no_plans_dir", "violations": []})
        return 0

    violations: list[dict[str, Any]] = []
    checked = 0

    for plan_file in sorted(PLANS_DIR.glob("*.md")):
        # Skip files in excluded subdirectories (shouldn't happen with glob("*.md")
        # at root, but guard anyway).
        if any(part in SKIP_SUBDIRS for part in plan_file.parts):
            continue

        slug = _extract_slug(plan_file)
        if not slug:
            continue

        try:
            content = plan_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        has_wave_rows, all_done = _parse_wave_status(content)
        if not has_wave_rows or not all_done:
            continue

        # Plan appears complete on disk — verify Notion.
        checked += 1
        if dry_run:
            print(f"[NP-DONE] DRY-RUN: would check {slug}", file=sys.stderr)
            continue

        notion_status = _query_notion_status(slug, token)
        if notion_status == COMPLETED_STATUS:
            continue

        violation = {
            "slug": slug,
            "plan_file": str(plan_file.relative_to(REPO_ROOT)),
            "notion_status": notion_status,
            "expected": COMPLETED_STATUS,
            "severity": "ERROR",
        }
        violations.append(violation)
        print(
            f"[NP-DONE] ERROR: {slug} — all waves ✅ on disk but Notion status="
            f"{notion_status!r} (expected 'Completed')",
            file=sys.stderr,
        )

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plans_checked": checked,
        "violations": violations,
        "status": "violations_found" if violations else "ok",
    }
    _write_report(report)

    if violations:
        print(
            f"[NP-DONE] {len(violations)} violation(s) found — "
            f"{'FAIL (fail-closed)' if fail_closed else 'advisory (set NP_PLAN_DONE_STATUS_FAIL_CLOSED=1 to block)'}",
            file=sys.stderr,
        )
    else:
        print(
            f"[NP-DONE] OK — {checked} all-done plan(s) checked, 0 violations",
            file=sys.stderr,
        )

    if violations and fail_closed:
        return 1
    return 0


def _write_report(data: dict[str, Any]) -> None:
    try:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError:
        pass


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Exit 1 on violations (default: advisory/exit 0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List all-done plans without calling Notion API",
    )
    args = parser.parse_args()

    fail_closed = args.fail_closed or (
        os.environ.get("NP_PLAN_DONE_STATUS_FAIL_CLOSED") == "1"
    )
    return run(fail_closed=fail_closed, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
