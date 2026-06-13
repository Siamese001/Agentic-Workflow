#!/usr/bin/env python3
"""pre_notion_plan_write_gate.py — Pre-write gate for Notion plan identity verification.

Blocks Notion API writes when the targeted page ID does not match the
intended plan slug. Prevents silent mis-targeting of plan status updates.

Contract
--------
    verify_plan_identity(intended_slug: str, notion_page_id: str) -> VerificationResult
        intended_slug    — The plan slug we intend to update (e.g., "l6-alignment-deferred-scope-c5e8a7")
        notion_page_id   — The Notion page ID being targeted in the API call

    Returns VerificationResult with:
        ok      — bool, True if slug matches page_id
        message — str, diagnostic message (error if not ok)
        actual  — str|None, the slug found for the given page_id (if query succeeded)

The helper queries the Notion Plans DB to resolve slug → page_id and
compares with the targeted page_id.

Bypass
------
    NOTION_PLAN_IDENTITY_BYPASS=1  — logs warning, proceeds anyway
    NOTION_PLAN_IDENTITY_FAIL_CLOSED=1  — exit 2 on mismatch (default is warn)

Logging
-------
    All verification attempts append to:
        artifacts/governance/plan_identity_verifications.jsonl

Example usage in pre-hook:
    result = verify_plan_identity("my-plan-slug", "35b27693...")
    if not result.ok:
        sys.stderr.write(f"PLAN_IDENTITY_MISMATCH: {result.message}\n")
        sys.exit(2)
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# SSOT — Plans DB identifiers
# ---------------------------------------------------------------------------

PLANS_DATA_SOURCE_ID: str = "ac53d31b-3068-4039-9ebe-856c12caab32"
NOTION_API_BASE: str = "https://api.notion.com/v1"

# Cache for slug → page_id lookups (session-level)
_slug_page_cache: dict[str, Optional[str]] = {}


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    message: str
    intended_slug: str
    targeted_page_id: str
    actual_slug: Optional[str] = None
    actual_page_id: Optional[str] = None


def _get_notion_token() -> Optional[str]:
    """Retrieve Notion API token from environment."""
    return os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")


def _normalize_id(raw: str) -> str:
    """Normalize Notion ID: lowercase, strip dashes for comparison."""
    return raw.strip().lower().replace("-", "")


def _ids_match(id1: str, id2: str) -> bool:
    """Compare two Notion IDs (tolerant of formatting differences)."""
    return _normalize_id(id1) == _normalize_id(id2)


def _log_verification(result: VerificationResult) -> None:
    """Append verification result to audit log."""
    log_dir = Path("artifacts/governance")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "plan_identity_verifications.jsonl"
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **asdict(result),
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def _query_notion_plans_db(slug: str) -> Optional[dict]:
    """Query Notion Plans DB for a plan by slug. Returns page object or None.
    
    Uses direct Notion REST API (not MCP) to avoid serialization constraints.
    """
    token = _get_notion_token()
    if not token:
        return None  # Cannot query without auth
    
    # Check cache first
    cache_key = slug.lower().strip()
    if cache_key in _slug_page_cache:
        cached = _slug_page_cache[cache_key]
        if cached is None:
            return None
        return {"id": cached, "properties": {"Slug": {"title": [{"text": {"content": slug}}]}}}
    
    try:
        url = f"{NOTION_API_BASE}/data_sources/{PLANS_DATA_SOURCE_ID}/query"
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        }
        
        # Query by slug (exact match on title property)
        payload = {
            "filter": {
                "property": "Slug",
                "title": {
                    "equals": slug
                }
            }
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(  # noqa: S310 - fixed Notion HTTPS API base
            url, data=body, headers=headers, method="POST"
        )
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
        results = data.get("results", [])
        
        if not results:
            _slug_page_cache[cache_key] = None
            return None
        
        # Return first match (slug should be unique)
        page = results[0]
        page_id = page.get("id", "")
        _slug_page_cache[cache_key] = page_id
        return page
        
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        message = f"HTTP {e.code}: {body or e.reason}"
        return {"id": f"ERROR:{message}", "error": message}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        # Query failed — cannot verify. In fail-closed mode this blocks.
        return {"id": f"ERROR:{e}", "error": str(e)}


def verify_plan_identity(
    intended_slug: str,
    targeted_page_id: str,
) -> VerificationResult:
    """Verify that targeted_page_id corresponds to intended_slug.
    
    Queries Notion Plans DB to find the canonical page for the slug,
    compares with targeted_page_id.
    """
    if not intended_slug or not targeted_page_id:
        return VerificationResult(
            ok=False,
            message="Missing intended_slug or targeted_page_id",
            intended_slug=intended_slug or "",
            targeted_page_id=targeted_page_id or "",
        )
    
    # Query Notion for the slug
    page = _query_notion_plans_db(intended_slug)
    
    if page is None:
        # Slug not found in DB — could be a new plan or query failure
        return VerificationResult(
            ok=True,  # Allow new plans to be created
            message=f"Slug '{intended_slug}' not found in Plans DB — assuming new plan",
            intended_slug=intended_slug,
            targeted_page_id=targeted_page_id,
        )
    
    if "error" in page:
        # Query failed
        error_msg = page.get("error", "unknown error")
        return VerificationResult(
            ok=False,
            message=f"Failed to query Plans DB: {error_msg}",
            intended_slug=intended_slug,
            targeted_page_id=targeted_page_id,
        )
    
    actual_page_id = page.get("id", "")
    actual_slug = ""
    
    # Extract slug from page properties
    props = page.get("properties", {})
    slug_prop = props.get("Slug", {})
    title_arr = slug_prop.get("title", [])
    if title_arr:
        actual_slug = title_arr[0].get("text", {}).get("content", "")
    
    # Compare page IDs
    if _ids_match(actual_page_id, targeted_page_id):
        return VerificationResult(
            ok=True,
            message="Plan identity verified: slug matches targeted page ID",
            intended_slug=intended_slug,
            targeted_page_id=targeted_page_id,
            actual_slug=actual_slug,
            actual_page_id=actual_page_id,
        )
    else:
        return VerificationResult(
            ok=False,
            message=(
                f"PLAN_IDENTITY_MISMATCH: Intended slug '{intended_slug}' "
                f"resolves to page '{actual_page_id[:8]}...' but targeted "
                f"page is '{targeted_page_id[:8]}...'. "
                f"Actual slug for targeted page: '{actual_slug or 'unknown'}'"
            ),
            intended_slug=intended_slug,
            targeted_page_id=targeted_page_id,
            actual_slug=actual_slug,
            actual_page_id=actual_page_id,
        )


def extract_slug_from_context(context: str) -> Optional[str]:
    """Extract plan slug from Cursor Agent context text.
    
    Looks for:
    - PLAN_CREATED markers: slug=xxx
    - plan file paths: .claude/plans/xxx-xxx.md
    - prose references: "plan xxx"
    """
    if not context:
        return None
    
    # Pattern 1: PLAN_CREATED marker
    match = re.search(r'PLAN_CREATED:.*?slug=([a-z0-9-]+)', context, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 2: Plan file path
    match = re.search(r'(?:plans|\.claude/plans)/([a-z0-9-]+-[a-f0-9]{6,})\.md', context)
    if match:
        return match.group(1)
    
    # Pattern 3: Slug in quotes or backticks
    match = re.search(r'[`"\']([a-z0-9-]+-[a-f0-9]{6,})[`"\']', context)
    if match:
        return match.group(1)
    
    return None


def run_gate(intended_slug: str, targeted_page_id: str) -> int:
    """Run the verification gate. Returns exit code (0 = pass, 2 = block).
    
    Honors bypass and fail-closed environment variables.
    """
    bypass = os.environ.get("NOTION_PLAN_IDENTITY_BYPASS", "") == "1"
    # Tandem enforcement: fail-closed by DEFAULT; opt out with NOTION_PLAN_IDENTITY_FAIL_CLOSED=0.
    fail_closed = os.environ.get("NOTION_PLAN_IDENTITY_FAIL_CLOSED", "").strip().lower() not in {"0", "false", "no"}
    
    result = verify_plan_identity(intended_slug, targeted_page_id)
    _log_verification(result)
    
    if result.ok:
        return 0
    
    # Mismatch detected
    if bypass:
        sys.stderr.write(f"WARNING: {result.message} (NOTION_PLAN_IDENTITY_BYPASS=1, proceeding)\n")
        return 0
    
    sys.stderr.write(f"ERROR: {result.message}\n")
    
    if fail_closed:
        sys.stderr.write("ERROR: NOTION_PLAN_IDENTITY_FAIL_CLOSED=1, blocking operation\n")
        return 2
    else:
        # Advisory only when explicitly opted out (NOTION_PLAN_IDENTITY_FAIL_CLOSED=0)
        sys.stderr.write("WARNING: Advisory mode (NOTION_PLAN_IDENTITY_FAIL_CLOSED=0) — mismatch allowed\n")
        return 0


def cli_main() -> int:
    """Command-line entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Pre-write gate for Notion plan identity verification"
    )
    parser.add_argument(
        "--intended-slug",
        required=True,
        help="The plan slug we intend to update",
    )
    parser.add_argument(
        "--notion-page-id",
        required=True,
        help="The Notion page ID being targeted",
    )
    parser.add_argument(
        "--test-mismatch",
        action="store_true",
        help="Test mode: simulate a mismatch scenario",
    )
    
    args = parser.parse_args()
    
    if args.test_mismatch:
        result = VerificationResult(
            ok=False,
            message="PLAN_IDENTITY_MISMATCH: simulated mismatch for test mode",
            intended_slug=args.intended_slug,
            targeted_page_id=args.notion_page_id,
            actual_page_id="WRONG-PAGE-ID",
        )
        _log_verification(result)
        sys.stderr.write(f"TEST-MISMATCH-DETECTED: {result.message}\n")
        return 2
    
    return run_gate(args.intended_slug, args.notion_page_id)


if __name__ == "__main__":
    sys.exit(cli_main())
