#!/usr/bin/env python3
"""
post_cursor_agent_plan_creation_audit.py — Post-creation audit with auto-correction.

Scans Cursor Agent responses for successful plan creation, validates status is correct,
and auto-corrects wrong status immediately.

Defense in depth for holistic-plan-status-discipline-d4e8a1 (W2).

Functions:
1. Detect plan creation via API-post-page responses
2. Validate created plan has correct status
3. Auto-correct wrong status via API-patch-page
4. Log all corrections to audit trail
5. Alert on manual-intervention-required cases

Integration:
- Registered in .cursor/hooks.json under post_cursor_agent_response
- Runs after every Cursor Agent response
- Fail-soft: audit errors don't block, they log
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Notion API constants
_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_API_VERSION = "2025-09-03"
_NOTION_TIMEOUT_S = 30

# Valid statuses at creation time
VALID_CREATION_STATUSES = frozenset({"Not Started", "Completed"})
FORBIDDEN_AT_CREATION = {"In Progress", "Waiting", "Lower Priority", "Retired", "Archived"}

# Audit log path
_AUDIT_LOG_PATH = Path("artifacts/cursor/plan_creation_corrections.jsonl")
_ALERT_LOG_PATH = Path("artifacts/cursor/plan_creation_alerts.jsonl")


@dataclass
class CorrectionEvent:
    """Record of a status correction."""
    timestamp: str
    slug: str
    page_id: str
    wrong_status: str
    corrected_status: str
    correction_ok: bool
    error: str | None = None
    method: str = "auto_patch"


@dataclass
class AlertEvent:
    """Record of an alert requiring manual intervention."""
    timestamp: str
    slug: str
    page_id: str | None
    alert_type: str
    message: str
    recommended_action: str


def _notion_token() -> str | None:
    """Get Notion token from environment."""
    return os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")


def _ensure_log_dirs():
    """Ensure audit log directories exist."""
    _AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _log_correction(event: CorrectionEvent):
    """Append correction to audit log."""
    _ensure_log_dirs()
    with _AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), default=str) + "\n")


def _log_alert(event: AlertEvent):
    """Append alert to alert log."""
    _ensure_log_dirs()
    with _ALERT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), default=str) + "\n")


def _extract_plan_creation_from_response(response_text: str) -> list[dict[str, Any]]:
    """
    Extract successful plan creation events from Cursor Agent response.
    
    Looks for:
    - API-post-page responses with success
    - Plans DB data_source_id
    - Returns list of {slug, page_id, status, created}
    """
    creations = []
    
    # Pattern to find successful API-post-page responses
    # Matches both the invoke tag and any success indicators
    invoke_pattern = re.compile(
        r'<invoke[^>]*name="(?:mcp\d+_)?API-post-page"[^>]*>(.*?)</invoke>',
        re.DOTALL,
    )
    
    plans_data_source = "ac53d31b-3068-4039-9ebe-856c12caab32"
    
    for match in invoke_pattern.finditer(response_text):
        block = match.group(1)
        
        # Check if targeting Plans DB
        if plans_data_source not in block:
            continue
        
        # Try to extract the response/result if present
        # Look for JSON result with id (indicating success)
        result_match = re.search(
            r'"id"\s*:\s*"([a-f0-9-]+)"',
            block,
        )
        
        if result_match:
            page_id = result_match.group(1)
            
            # Extract slug from properties
            slug_match = re.search(
                r'"Slug"[^}]*"content"\s*:\s*"([^"]+)"',
                block,
            )
            slug = slug_match.group(1) if slug_match else "unknown"
            
            # Extract status
            status_match = re.search(
                r'"Status"[^}]*"name"\s*:\s*"([^"]+)"',
                block,
            )
            status = status_match.group(1) if status_match else "unknown"
            
            creations.append({
                "slug": slug,
                "page_id": page_id,
                "status": status,
                "source": "response_block",
            })
    
    # Also check for PLAN_CREATED markers with verification
    marker_pattern = re.compile(
        r'PLAN_CREATED:\s*plan=([a-z0-9-]+)',
    )
    for match in marker_pattern.finditer(response_text):
        slug = match.group(1)
        # Check if we already captured this from response block
        if not any(c["slug"] == slug for c in creations):
            creations.append({
                "slug": slug,
                "page_id": None,  # Will need lookup
                "status": "marker_only",
                "source": "marker",
            })
    
    return creations


def _validate_created_status(status: str) -> tuple[bool, str, str]:
    """
    Validate status of newly created plan.
    
    Returns (is_valid, recommended_status, reason)
    """
    if status in VALID_CREATION_STATUSES:
        return True, status, "Valid creation status"
    
    if status in FORBIDDEN_AT_CREATION:
        return False, "Not Started", f"Status '{status}' forbidden at creation"
    
    # Unknown status
    return False, "Not Started", f"Unknown status '{status}'"


def _patch_plan_status(page_id: str, new_status: str) -> tuple[bool, str | None]:
    """
    Auto-correct plan status via Notion API.
    
    Returns (success, error_message)
    """
    token = _notion_token()
    if not token:
        return False, "No NOTION_TOKEN available for correction"
    
    if os.environ.get("PLAN_CREATION_AUTO_CORRECT_BYPASS") == "1":
        return False, "PLAN_CREATION_AUTO_CORRECT_BYPASS=1"
    
    url = f"{_NOTION_BASE}/pages/{page_id}"
    
    payload = {
        "properties": {
            "Status": {
                "select": {"name": new_status}
            }
        }
    }
    
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
            method="PATCH",
        )
        
        with urllib.request.urlopen(req, timeout=_NOTION_TIMEOUT_S) as resp:
            if resp.status == 200:
                return True, None
            return False, f"HTTP {resp.status}"
            
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def _process_creation(
    creation: dict[str, Any],
    response_text: str,
) -> CorrectionEvent | AlertEvent | None:
    """
    Process a single plan creation event.
    
    Returns CorrectionEvent if corrected, AlertEvent if needs manual intervention,
    or None if valid.
    """
    slug = creation["slug"]
    page_id = creation.get("page_id")
    status = creation["status"]
    
    # If we only have marker but no page_id, we can't auto-correct
    if not page_id and creation.get("source") == "marker":
        return AlertEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            slug=slug,
            page_id=None,
            alert_type="marker_without_page_id",
            message=f"PLAN_CREATED marker for {slug} but no page_id in response",
            recommended_action="Verify plan was created; check Notion DB manually",
        )
    
    # Validate status
    is_valid, recommended, reason = _validate_created_status(status)
    
    if is_valid:
        print(
            f"[post-creation-audit] VALID: {slug} status={status}",
            file=sys.stderr,
        )
        return None
    
    # Status is wrong — attempt auto-correction
    print(
        f"[post-creation-audit] INVALID: {slug} status={status} "
        f"recommending={recommended} (reason: {reason})",
        file=sys.stderr,
    )
    
    if page_id:
        success, error = _patch_plan_status(page_id, recommended)
        
        event = CorrectionEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            slug=slug,
            page_id=page_id,
            wrong_status=status,
            corrected_status=recommended,
            correction_ok=success,
            error=error,
        )
        
        if success:
            print(
                f"[post-creation-audit] CORRECTED: {slug} {status}->{recommended}",
                file=sys.stderr,
            )
        else:
            print(
                f"[post-creation-audit] CORRECTION_FAILED: {slug} error={error}",
                file=sys.stderr,
            )
            # Also log as alert
            _log_alert(AlertEvent(
                timestamp=datetime.utcnow().isoformat() + "Z",
                slug=slug,
                page_id=page_id,
                alert_type="auto_correction_failed",
                message=f"Failed to correct status from {status} to {recommended}: {error}",
                recommended_action="Manually patch status in Notion UI",
            ))
        
        return event
    
    # No page_id, can't correct
    return AlertEvent(
        timestamp=datetime.utcnow().isoformat() + "Z",
        slug=slug,
        page_id=None,
        alert_type="no_page_id_for_correction",
        message=f"Wrong status {status} but no page_id available for correction",
        recommended_action="Manually find and patch plan in Notion UI",
    )


def main() -> int:
    """
    Main entry point for post-cursor-agent hook.
    
    Reads response text from stdin, audits plan creations, applies corrections.
    """
    if os.environ.get("POST_CREATION_AUDIT_BYPASS") == "1":
        print("[post-creation-audit] BYPASS", file=sys.stderr)
        return 0
    
    # Read input (Cursor Agent hook contract - response text via stdin)
    try:
        input_data = sys.stdin.read()
    except Exception:
        input_data = ""
    
    if not input_data:
        return 0
    
    # Extract plan creations from response
    creations = _extract_plan_creation_from_response(input_data)
    
    if not creations:
        # No plan creations detected
        return 0
    
    print(
        f"[post-creation-audit] DETECTED: {len(creations)} plan creation(s)",
        file=sys.stderr,
    )
    
    # Process each creation
    corrections = 0
    alerts = 0
    
    for creation in creations:
        result = _process_creation(creation, input_data)
        
        if isinstance(result, CorrectionEvent):
            _log_correction(result)
            if result.correction_ok:
                corrections += 1
            else:
                alerts += 1
        elif isinstance(result, AlertEvent):
            _log_alert(result)
            alerts += 1
    
    print(
        f"[post-creation-audit] SUMMARY: "
        f"creations={len(creations)} corrections={corrections} alerts={alerts}",
        file=sys.stderr,
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
