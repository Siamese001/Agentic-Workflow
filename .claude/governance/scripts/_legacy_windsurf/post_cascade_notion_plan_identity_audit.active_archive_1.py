#!/usr/bin/env python3
"""post_cascade_notion_plan_identity_audit.py — Post-cascade audit for plan identity verification.

Scans Cascade response text for mcp7_API-patch-page calls targeting the Plans DB,
extracts intended plan slug from context and targeted page_id from the API call,
queries Notion DB to verify the match, and logs any mismatches.

This is a post-cascade audit (not a pre-hook) because pre_mcp_tool_use hooks
cannot see tool arguments per pre_mcp_gate.py:1042-1051.

Contract
--------
    audit_response(response_text: str, context_text: str) -> list[IdentityViolation]
        response_text  — The full Cascade response text containing API calls
        context_text   — Prior context (plan slugs, file paths, etc.)

    Returns list of IdentityViolation objects for any detected mismatches.

Logging
-------
    All violations append to: artifacts/windsurf/plan_identity_violations.jsonl
    Summary written to: artifacts/windsurf/plan_identity_audit_summary.json

Bypass
------
    NOTION_PLAN_IDENTITY_AUDIT_BYPASS=1 — skip audit entirely

Integration
-----------
    Registered in .windsurf/hooks.json under post_cascade_response.
    Triggered after every Cascade response.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Import the verification logic from the pre-write gate module
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pre_notion_plan_write_gate import (
    verify_plan_identity,
    extract_slug_from_context,
    PLANS_DATA_SOURCE_ID,
    _get_notion_token,
)


@dataclass(frozen=True)
class IdentityViolation:
    timestamp: str
    intended_slug: str
    targeted_page_id: str
    actual_slug: Optional[str]
    actual_page_id: Optional[str]
    message: str
    context_excerpt: str


def _normalize_id(raw: str) -> str:
    """Normalize Notion ID: lowercase, strip dashes for comparison."""
    return raw.strip().lower().replace("-", "")


def _is_plans_db_target(payload_str: str) -> bool:
    """Check if the payload targets the Plans DB."""
    # Look for Plans DB IDs in various forms
    plans_ids = {
        "ac53d31b-3068-4039-9ebe-856c12caab32",  # data_source_id
        "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9",  # database_id
    }
    # Also check un-dashed forms
    normalized = _normalize_id(payload_str)
    for pid in plans_ids:
        if _normalize_id(pid) in normalized or pid in payload_str:
            return True
    return False


def extract_page_id_from_payload(payload_str: str) -> Optional[str]:
    """Extract page_id from an mcp7_API-patch-page payload."""
    # Pattern: "page_id": "35b27693-f55c-8189-8827-c3dec80f05fa"
    match = re.search(r'"page_id"\s*:\s*"([a-f0-9-]{36})"', payload_str)
    if match:
        return match.group(1)
    
    # Pattern: page_id="35b27693-f55c-8189-8827-c3dec80f05fa"
    match = re.search(r'page_id=\"([a-f0-9-]{36})\"', payload_str)
    if match:
        return match.group(1)
    
    return None


def extract_notion_api_calls(response_text: str) -> list[dict]:
    """Extract all mcp7_API-patch-page calls from response text.
    
    Returns list of dicts with:
        - tool_name: str
        - page_id: str
        - payload: str (full match)
        - targets_plans: bool
    """
    calls = []
    
    # Pattern to find mcp7_API-patch-page invocations
    # Matches both <invoke name="..."> and JSON-like payloads
    patterns = [
        # XML-style invoke tags
        r'<invoke\s+name="mcp7_API-patch-page"[^>]*>(.*?)</invoke>',
        # JSON-style function calls
        r'mcp7_API-patch-page\s*\(\s*(.*?)\s*\)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, response_text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            payload = match.group(0)
            page_id = extract_page_id_from_payload(payload)
            
            if page_id:
                targets_plans = _is_plans_db_target(payload)
                calls.append({
                    "tool_name": "mcp7_API-patch-page",
                    "page_id": page_id,
                    "payload": payload[:500],  # Truncated for logging
                    "targets_plans": targets_plans,
                })
    
    return calls


def audit_response(response_text: str, context_text: str = "") -> list[IdentityViolation]:
    """Audit a Cascade response for plan identity mismatches.
    
    Steps:
    1. Extract all mcp7_API-patch-page calls
    2. Filter to those targeting Plans DB
    3. Extract intended slug from context
    4. Verify each call's page_id matches the slug
    5. Return list of violations
    """
    violations = []
    
    # Check bypass
    if os.environ.get("NOTION_PLAN_IDENTITY_AUDIT_BYPASS", "") == "1":
        return violations
    
    # Extract Notion API calls
    calls = extract_notion_api_calls(response_text)
    
    # Filter to Plans DB targets only
    plan_calls = [c for c in calls if c.get("targets_plans", False)]
    
    if not plan_calls:
        return violations
    
    # Extract intended slug from context
    intended_slug = extract_slug_from_context(context_text)
    
    # If no slug found in context, we can't verify — log as uncertain
    if not intended_slug:
        for call in plan_calls:
            violations.append(IdentityViolation(
                timestamp=datetime.now(timezone.utc).isoformat(),
                intended_slug="UNKNOWN",
                targeted_page_id=call["page_id"],
                actual_slug=None,
                actual_page_id=None,
                message="Could not determine intended plan slug from context",
                context_excerpt=context_text[:200] if context_text else "",
            ))
        return violations
    
    # Verify each call
    for call in plan_calls:
        result = verify_plan_identity(intended_slug, call["page_id"])
        
        if not result.ok:
            violations.append(IdentityViolation(
                timestamp=datetime.now(timezone.utc).isoformat(),
                intended_slug=intended_slug,
                targeted_page_id=call["page_id"],
                actual_slug=result.actual_slug,
                actual_page_id=result.actual_page_id,
                message=result.message,
                context_excerpt=context_text[:200] if context_text else "",
            ))
    
    return violations


def _log_violations(violations: list[IdentityViolation]) -> None:
    """Append violations to audit log."""
    if not violations:
        return
    
    log_dir = Path("artifacts/windsurf")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "plan_identity_violations.jsonl"
    
    with open(log_file, "a", encoding="utf-8") as f:
        for v in violations:
            f.write(json.dumps(asdict(v), default=str) + "\n")


def _write_summary(violations: list[IdentityViolation], total_calls: int) -> None:
    """Write audit summary."""
    summary_dir = Path("artifacts/windsurf")
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_file = summary_dir / "plan_identity_audit_summary.json"
    
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_violations": len(violations),
        "total_calls_audited": total_calls,
        "violations": [asdict(v) for v in violations],
    }
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)


def main() -> int:
    """Main entry point for hook execution.
    
    Reads response text from stdin or environment variable.
    """
    # Get response text
    response_text = os.environ.get("CASCADE_RESPONSE_TEXT", "")
    context_text = os.environ.get("CASCADE_CONTEXT_TEXT", "")
    
    if not response_text and not sys.stdin.isatty():
        response_text = sys.stdin.read()
    
    if not response_text:
        # Nothing to audit
        return 0
    
    # Run audit
    violations = audit_response(response_text, context_text)
    
    # Log results
    _log_violations(violations)
    
    # Extract total calls for summary
    calls = extract_notion_api_calls(response_text)
    plan_calls = [c for c in calls if c.get("targets_plans", False)]
    _write_summary(violations, len(plan_calls))
    
    # Output summary to stderr if violations found
    if violations:
        sys.stderr.write(f"[PLAN_IDENTITY_AUDIT] {len(violations)} violation(s) detected\n")
        for v in violations:
            sys.stderr.write(f"  - {v.intended_slug} → {v.targeted_page_id[:8]}...: {v.message[:80]}\n")
        return 1  # Non-zero exit to flag attention (but not block)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
