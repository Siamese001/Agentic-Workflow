#!/usr/bin/env python3
"""check_notion_schema_preflight.py — NP11 Notion Schema Pre-flight Gate (advisory).

Validates that Notion write operations target existing properties before
API calls are made. Prevents 400 errors from renamed/deleted properties.

Constitutional: §25 (MCP serialization), §36 (plan registration)
Sibling: check_notion_plans_status_canonical.py (NP2)

Exit codes:
  0 = all checks passed or advisory mode
  1 = fail-closed mode with violations (NOTION_SCHEMA_PREFLIGHT_FAIL_CLOSED=1)
  2 = internal error (import failure, etc.)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".cursor" / "scripts" / "_legacy_windsurf"))

from tools.notion._notion_property_validator import (
    PLANS_DB_REQUIRED_PROPERTIES,
    validate_properties,
    fetch_and_cache_properties,
    clear_cache,
)
from _notion_plans_status_check import PLANS_DATA_SOURCE_ID, PLANS_DB_ID

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ci"
REPORT_PATH = ARTIFACTS_DIR / "notion_schema_preflight.json"

# Database ID -> expected properties mapping
DB_SCHEMA_REGISTRY: dict[str, set[str]] = {
    PLANS_DB_ID: PLANS_DB_REQUIRED_PROPERTIES,
    PLANS_DATA_SOURCE_ID: PLANS_DB_REQUIRED_PROPERTIES,
    # Normalized forms (no dashes, lowercase)
    PLANS_DB_ID.lower().replace("-", ""): PLANS_DB_REQUIRED_PROPERTIES,
    PLANS_DATA_SOURCE_ID.lower().replace("-", ""): PLANS_DB_REQUIRED_PROPERTIES,
}

BYPASS_ENV_VAR = "NOTION_SCHEMA_PREFLIGHT_BYPASS"
FAIL_CLOSED_ENV_VAR = "NOTION_SCHEMA_PREFLIGHT_FAIL_CLOSED"


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def check_write_payload(
    payload: dict[str, Any],
    db_schema: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    """Check a Notion write payload for property violations.
    
    Args:
        payload: Notion API payload (post-page or patch-page)
        db_schema: Optional override of DB_SCHEMA_REGISTRY
    
    Returns:
        List of violation dicts
    """
    violations: list[dict[str, Any]] = []
    schema = db_schema or DB_SCHEMA_REGISTRY
    
    # Extract database ID from payload
    db_id: str | None = None
    parent = payload.get("parent", {})
    if parent.get("type") == "database_id":
        db_id = parent.get("database_id", "")
    elif parent.get("type") == "data_source_id":
        db_id = parent.get("data_source_id", "")
    
    # Also check page_id for patch operations
    if not db_id and "page_id" in payload:
        # For patch-page, we'd need to resolve page -> database
        # This requires a Notion API call; skip for now
        pass
    
    if not db_id:
        return violations  # Cannot validate without DB context
    
    # Normalize DB ID for lookup
    db_id_norm = db_id.lower().replace("-", "")
    expected_props = schema.get(db_id_norm) or schema.get(db_id.lower())
    
    if not expected_props:
        return violations  # Unknown database, no schema to validate against
    
    # Extract properties being written
    properties = payload.get("properties", {})
    written_props = set(properties.keys())
    
    # Check for missing/renamed properties
    missing = written_props - expected_props
    for prop in missing:
        # Check if it's a known renamed property (e.g., "AI Summary" vs "AI Summary ")
        suggestion = None
        for expected in expected_props:
            if prop.rstrip() == expected.rstrip() or prop.lower() == expected.lower():
                suggestion = expected
                break
        
        violations.append({
            "type": "unknown_property",
            "database_id": db_id,
            "property": prop,
            "suggestion": suggestion,
            "message": (
                f"Property '{prop}' not in known schema for DB {db_id[:8]}..."
                + (f". Did you mean '{suggestion}'?" if suggestion else "")
            ),
        })
    
    return violations


def check_payloads_in_response(response_text: str) -> list[dict[str, Any]]:
    """Scan response text for Notion API payloads and validate them.
    
    This is used by post-cursor-agent audits to check what Cursor Agent wrote.
    """
    violations: list[dict[str, Any]] = []
    
    # Look for JSON blocks in API-post-page / API-patch-page calls
    # This is a heuristic pattern match
    import re
    
    # Match API-post-page or API-patch-page with JSON payload
    pattern = r'API-(?:post|patch)-page[^{]*(\{[^}]+\})'
    for match in re.finditer(pattern, response_text, re.DOTALL):
        try:
            # Try to extract JSON - this is approximate
            json_str = match.group(1)
            # Handle nested braces by counting
            brace_count = 0
            end_pos = 0
            for i, char in enumerate(json_str):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            if end_pos > 0:
                payload = json.loads(json_str[:end_pos])
                vios = check_write_payload(payload)
                violations.extend(vios)
        except (json.JSONDecodeError, IndexError):
            continue  # Skip malformed JSON
    
    return violations


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the schema preflight check.
    
    Modes:
      --check-payload <json>: Validate a single payload
      --scan-file <path>:     Scan a file for payloads
      --report:               Emit JSON report
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NP11 Notion Schema Pre-flight Gate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check-payload",
        metavar="JSON",
        help="Validate a single JSON payload string",
    )
    parser.add_argument(
        "--scan-file",
        metavar="PATH",
        help="Scan a file for Notion API payloads",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Emit JSON report to artifacts/ci/notion_schema_preflight.json",
    )
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Exit 1 on any violation (override env var)",
    )
    
    args = parser.parse_args()
    
    # Check bypass
    if os.environ.get(BYPASS_ENV_VAR):
        print(f"NP11: {BYPASS_ENV_VAR}=1 — bypassing schema preflight check")
        return 0
    
    fail_closed = (
        args.fail_closed
        or os.environ.get(FAIL_CLOSED_ENV_VAR, "").lower() in ("1", "true", "yes")
    )
    
    all_violations: list[dict[str, Any]] = []
    
    # Mode: single payload check
    if args.check_payload:
        try:
            payload = json.loads(args.check_payload)
            vios = check_write_payload(payload)
            all_violations.extend(vios)
        except json.JSONDecodeError as e:
            print(f"NP11 ERROR: Invalid JSON payload: {e}")
            return 2
    
    # Mode: scan file
    if args.scan_file:
        file_path = Path(args.scan_file)
        if not file_path.exists():
            print(f"NP11 ERROR: File not found: {file_path}")
            return 2
        
        try:
            content = file_path.read_text(encoding="utf-8")
            vios = check_payloads_in_response(content)
            all_violations.extend(vios)
        except Exception as e:
            print(f"NP11 ERROR: Failed to read file: {e}")
            return 2
    
    # Default mode: no-op with status
    if not args.check_payload and not args.scan_file:
        # Advisory check - just report schema registry status
        print("NP11: Schema preflight gate active")
        print(f"  - Registered DB schemas: {len(DB_SCHEMA_REGISTRY) // 2} unique databases")
        print(f"  - Plans DB properties tracked: {len(PLANS_DB_REQUIRED_PROPERTIES)}")
        print(f"  - Fail-closed mode: {fail_closed}")
    
    # Emit report if requested
    if args.report or all_violations:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        report = {
            "gate": "NP11",
            "name": "notion_schema_preflight",
            "timestamp": str(Path(__file__).stat().st_mtime),
            "fail_closed": fail_closed,
            "bypass": os.environ.get(BYPASS_ENV_VAR, "") != "",
            "violations": all_violations,
            "violation_count": len(all_violations),
            "status": "FAIL" if all_violations else "PASS",
        }
        
        try:
            with open(REPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"NP11: Report written to {REPORT_PATH}")
        except Exception as e:
            print(f"NP11 WARNING: Failed to write report: {e}")
    
    # Print violations
    for v in all_violations:
        print(f"NP11 VIOLATION: {v['type']} — {v['message']}")
    
    if all_violations and fail_closed:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
