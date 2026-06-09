"""plan_creation_helper.py — Canonical helper for Notion Plans DB creation.

SSOT for ALL plan creation in the Notion Plans DB. Enforces:
1. Status MUST be "Not Started" at creation (no exceptions except retrospective)
2. All required fields populated
3. Slug validation (kebab-case-6hex)
4. Fail-closed: any validation error → no API call

Usage:
    from tools.notion.plan_creation_helper import create_plan_in_notion
    
    # Standard new plan
    result = create_plan_in_notion(
        slug="my-plan-abc123",
        summary="Plan summary text",
        ai_summary="- Target: ...\n- Closes: ...",
    )
    
    # Retrospective plan (created and completed same session)
    result = create_plan_in_notion(
        slug="retrospective-plan-def456",
        summary="Retrospective documentation",
        ai_summary="- Target: ...",
        force_status="Completed",  # Only for retrospective
    )

Defense in depth for holistic-plan-status-discipline-d4e8a1 (W1).
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from tools.notion.notion_bearer_token import get_notion_bearer_token_or_none

# Notion API constants
_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_API_VERSION = "2025-09-03"
_NOTION_TIMEOUT_S = 30

# Plans DB data_source_id
_PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"

# Slug pattern: kebab-case with 6-hex suffix
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*-[a-f0-9]{6}$")

# Canonical statuses allowed at creation time
VALID_CREATION_STATUSES = frozenset({"Not Started", "Completed"})


class PlanCreationError(Exception):
    """Validation or API error during plan creation."""
    pass


@dataclass(frozen=True)
class CreationResult:
    """Result of plan creation attempt."""
    ok: bool
    page_id: str | None
    slug: str
    status: str
    error: str | None = None
    correction_applied: bool = False


def _notion_token() -> str | None:
    """Get Notion token from environment (canonical ``NOTION_TOKEN``; alias in notion_bearer_token)."""
    return get_notion_bearer_token_or_none()


def _validate_slug(slug: str) -> None:
    """Validate plan slug format. Raises PlanCreationError if invalid."""
    if not slug:
        raise PlanCreationError("Slug is required")
    if not SLUG_PATTERN.match(slug):
        raise PlanCreationError(
            f"Invalid slug '{slug}'. Expected format: kebab-case-6hex "
            f"(e.g., 'my-plan-abc123')"
        )


def _enforce_not_started_status(
    status: str,
    force_status: Literal["Not Started", "Completed"] | None,
    slug: str,
) -> str:
    """Enforce correct initial status. Returns validated status.
    
    Rules:
    - Default (force_status=None): MUST be "Not Started"
    - force_status="Completed": Only for retrospective plans
    - ANY other status: REJECTED with error
    
    This prevents the "In Progress" at creation bug.
    """
    effective_status = force_status or "Not Started"
    
    # CRITICAL GUARD: Never allow "In Progress" or "Waiting" at creation
    forbidden_at_creation = {"In Progress", "Waiting", "Lower Priority", 
                              "Retired", "Archived"}
    
    if effective_status in forbidden_at_creation:
        raise PlanCreationError(
            f"Status '{effective_status}' is FORBIDDEN at plan creation time.\n"
            f"Plan: {slug}\n"
            f"Allowed: 'Not Started' (default) or 'Completed' (retrospective only)\n"
            f"To flip to '{effective_status}', use wave_execution_state.py start "
            f"or emit WAVE_START marker AFTER creation."
        )
    
    if effective_status not in VALID_CREATION_STATUSES:
        raise PlanCreationError(
            f"Invalid status '{effective_status}'. "
            f"Must be one of: {VALID_CREATION_STATUSES}"
        )
    
    return effective_status


def _build_payload(
    slug: str,
    summary: str,
    ai_summary: str,
    status: str,
    plan_file_path: str,
) -> dict:
    """Build Notion API payload for plan creation."""
    return {
        "parent": {
            "type": "data_source_id",
            "data_source_id": _PLANS_DATA_SOURCE_ID,
        },
        "properties": {
            "Slug": {
                "title": [{"text": {"content": slug}}]
            },
            "Status": {
                "select": {"name": status}
            },
            "Exists On Disk": {
                "checkbox": True
            },
            "Plan File Path": {
                "rich_text": [{"text": {"content": plan_file_path}}]
            },
            "Summary": {
                "rich_text": [{"text": {"content": summary}}]
            },
            "AI Summary ": {
                "rich_text": [{"text": {"content": ai_summary}}]
            },
        },
    }


def _call_notion_api(payload: dict) -> dict:
    """Execute Notion API call. Raises PlanCreationError on failure."""
    token = _notion_token()
    if not token:
        raise PlanCreationError(
            "NOTION_TOKEN environment variable required (NOTION_API_KEY accepted as legacy alias)"
        )
    
    url = f"{_NOTION_BASE}/pages"
    
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": _NOTION_API_VERSION,
            },
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise PlanCreationError(
            f"Notion API HTTP {e.code}: {error_body}"
        )
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise PlanCreationError(f"Notion API connection error: {e}")
    except json.JSONDecodeError as e:
        raise PlanCreationError(f"Invalid JSON response from Notion: {e}")


def create_plan_in_notion(
    slug: str,
    summary: str,
    ai_summary: str,
    plan_file_path: str | None = None,
    force_status: Literal["Not Started", "Completed"] | None = None,
) -> CreationResult:
    """
    Canonical plan creation in Notion Plans DB.
    
    **ENFORCES:** Status MUST be "Not Started" at creation time.
    
    Args:
        slug: Plan slug (kebab-case-6hex, e.g., 'my-plan-abc123')
        summary: Human-readable summary (prose)
        ai_summary: Bullet-style AI summary (high-signal format)
        plan_file_path: Optional override. Default: plans/{slug}.md
        force_status: "Completed" for retrospective plans only. Default "Not Started".
    
    Returns:
        CreationResult with ok, page_id, status, error details
    
    Raises:
        PlanCreationError: On validation or API error (fail-closed)
    
    Examples:
        >>> # Standard new plan
        >>> result = create_plan_in_notion(
        ...     slug="fix-bug-a1b2c3",
        ...     summary="Fix the critical bug in auth flow",
        ...     ai_summary="- Target: auth module\n- Closes: login bug",
        ... )
        >>> assert result.ok
        >>> assert result.status == "Not Started"
        
        >>> # Retrospective plan (documenting completed work)
        >>> result = create_plan_in_notion(
        ...     slug="rca-analysis-d4e5f6",
        ...     summary="RCA documentation for incident",
        ...     ai_summary="- Target: incident analysis",
        ...     force_status="Completed",
        ... )
    """
    # Phase 1.1: Validate inputs
    _validate_slug(slug)
    
    if not summary:
        raise PlanCreationError("Summary is required")
    if not ai_summary:
        raise PlanCreationError("AI Summary is required")
    
    # Phase 1.2: CRITICAL GUARD — enforce correct status
    try:
        validated_status = _enforce_not_started_status(
            status=force_status or "Not Started",
            force_status=force_status,
            slug=slug,
        )
    except PlanCreationError:
        # Log to stderr for visibility, then re-raise
        print(
            f"[plan-creation-helper] STATUS_ENFORCEMENT_FAILED slug={slug}",
            file=sys.stderr,
        )
        raise
    
    # Build default path if not provided.
    # Canonical SSOT is repo-root plans/ (relocated out of .claude/ to avoid the
    # Claude Code .claude/ edit-guard); plan relocate-plans-ssot-outside-claude-c1a17d.
    effective_path = plan_file_path or f"plans/{slug}.md"
    
    # Phase 1.3: Build payload
    payload = _build_payload(
        slug=slug,
        summary=summary,
        ai_summary=ai_summary,
        status=validated_status,
        plan_file_path=effective_path,
    )
    
    # Phase 1.4: Execute API call (fail-closed)
    try:
        response = _call_notion_api(payload)
        page_id = response.get("id")
        
        print(
            f"[plan-creation-helper] CREATED slug={slug} "
            f"status={validated_status} page_id={page_id}",
            file=sys.stderr,
        )
        
        return CreationResult(
            ok=True,
            page_id=page_id,
            slug=slug,
            status=validated_status,
        )
        
    except PlanCreationError:
        print(
            f"[plan-creation-helper] API_FAILED slug={slug}",
            file=sys.stderr,
        )
        raise


def patch_plan_notion_properties(
    page_id: str,
    *,
    ai_summary: str | None = None,
    summary: str | None = None,
    token: str | None = None,
) -> bool:
    """Patch an existing Plans DB page's ``AI Summary`` and/or ``Summary`` properties.

    Used for W3 body-sync: after initial registration and on subsequent plan-file edits
    (detected via content_digest change) so the Notion row stays current.

    Returns True if the patch succeeded, False otherwise (fail-soft; callers should not
    raise on False).  Skips the API call when both ai_summary and summary are None.
    """
    if ai_summary is None and summary is None:
        return False
    resolved_token = token or _notion_token()
    if not resolved_token:
        return False
    if not page_id:
        return False

    props: dict[str, Any] = {}
    if ai_summary is not None:
        props["AI Summary "] = {
            "rich_text": [{"type": "text", "text": {"content": ai_summary[:2000]}}]
        }
    if summary is not None:
        props["Summary"] = {
            "rich_text": [{"type": "text", "text": {"content": summary[:2000]}}]
        }

    url = f"{_NOTION_BASE}/pages/{page_id}"
    body = json.dumps({"properties": props}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {resolved_token}",
            "Content-Type": "application/json",
            "Notion-Version": _NOTION_API_VERSION,
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            resp.read()
        print(
            f"[plan-creation-helper] BODY_SYNC page_id={page_id} "
            f"ai_summary={'set' if ai_summary else 'skip'} "
            f"summary={'set' if summary else 'skip'}",
            file=sys.stderr,
        )
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return False


def main(argv: list[str] | None = None) -> int:
    """CLI for plan creation (scripted/batch use)."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Canonical plan creation helper")
    parser.add_argument("--slug", required=True, help="Plan slug (kebab-case-6hex)")
    parser.add_argument("--summary", required=True, help="Plan summary")
    parser.add_argument("--ai-summary", required=True, help="AI Summary (bullet format)")
    parser.add_argument("--plan-file-path", help="Override plan file path")
    parser.add_argument(
        "--force-status",
        choices=["Not Started", "Completed"],
        help="Force status (default: Not Started; use Completed for retrospective)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON result")
    
    args = parser.parse_args(argv)
    
    try:
        result = create_plan_in_notion(
            slug=args.slug,
            summary=args.summary,
            ai_summary=args.ai_summary,
            plan_file_path=args.plan_file_path,
            force_status=args.force_status,  # type: ignore
        )
        
        if args.json:
            print(json.dumps({
                "ok": result.ok,
                "page_id": result.page_id,
                "slug": result.slug,
                "status": result.status,
                "error": result.error,
            }, indent=2))
        else:
            if result.ok:
                print(f"✅ Created plan {result.slug} with status={result.status}")
            else:
                print(f"❌ Failed: {result.error}")
                
        return 0 if result.ok else 1
        
    except PlanCreationError as e:
        error_msg = str(e)
        if args.json:
            print(json.dumps({
                "ok": False,
                "page_id": None,
                "slug": args.slug,
                "status": args.force_status or "Not Started",
                "error": error_msg,
            }, indent=2))
        else:
            print(f"❌ Plan creation failed: {error_msg}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
