#!/usr/bin/env python3
"""
unified_plan_creation_auditor.py — Consolidated plan creation validation (W2.P1).

Merges:
- pre_notion_plan_creation_gate.py (pre-flight blocking validation)
- post_agent_plan_creation_audit.py (post-flight advisory audit with auto-correction)

Result: Single unified hook providing defense-in-depth for plan creation.

Behavior preservation:
- Pre-flight: BLOCKS non-canonical plan creation attempts (blocking mode)
- Post-flight: Auto-corrects status violations, logs to audit trail (advisory mode)
- Bypass: NOTION_PLAN_CREATION_GATE_BYPASS=1 (logged but allowed)

Enforcement:
1. Status MUST be "Not Started" or "Completed" (forbidden: In Progress, Waiting, etc.)
2. Slug format: kebab-case-6hex
3. Required fields: Slug, Status, Summary, AI Summary, Exists On Disk
4. Post-creation: Auto-correct wrong status via Notion API PATCH
5. Audit logging: All corrections and alerts logged to artifacts/

W2.P1 Consolidation: Pair 1 — preserves all blocking/advisory behavior exactly.
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

_REPO_ROOT = Path(__file__).resolve().parents[3]

# Validation constants
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*-[a-f0-9]{6}$")
VALID_CREATION_STATUSES = frozenset({"Not Started", "Completed"})
FORBIDDEN_AT_CREATION = {
    "In Progress",
    "Deferred",       # stale → coerces to In Progress
    "Deprioritized",  # stale → coerces to In Progress
    "Active",
    "Live",
    "Draft",
    "Retired",
    "Archived",
}  # SSOT 5-status: "Waiting"/"Lower Priority" removed from the taxonomy

# Audit log paths (repo-root anchored — hook cwd is usually repo root but this stays correct)
_AUDIT_LOG_PATH = _REPO_ROOT / "artifacts" / "governance" / "plan_creation_corrections.jsonl"
_ALERT_LOG_PATH = _REPO_ROOT / "artifacts" / "governance" / "plan_creation_alerts.jsonl"

# Plans DB identifiers — imported from _notion_constants SSOT.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from _notion_constants import PLANS_DATA_SOURCE_ID, PLANS_DB_ID as PLANS_DATABASE_ID  # noqa: E402

PLANS_PARENT_IDS = frozenset({PLANS_DATA_SOURCE_ID, PLANS_DATABASE_ID})

_NOTION_MCP_SERVER_KEY = "notion"


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


# =============================================================================
# PRE-FLIGHT VALIDATION (from pre_notion_plan_creation_gate)
# =============================================================================

def _get_payload_from_stdin() -> dict[str, Any] | None:
    """Parse JSON payload from stdin (Cursor Agent hook contract)."""
    try:
        data = sys.stdin.read()
        if not data:
            return None
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def _extract_plans_creation_payloads(response_text: str) -> list[dict[str, Any]]:
    """Extract API-post-page payloads targeting Plans DB from Cursor Agent response."""
    payloads: list[dict[str, Any]] = []
    
    invoke_pattern = re.compile(
        r'<invoke\s+name="(?:mcp\d+_)?API-post-page">(.*?)</invoke>',
        re.DOTALL,
    )
    
    plans_ids = [PLANS_DATA_SOURCE_ID, PLANS_DATABASE_ID]
    
    for match in invoke_pattern.finditer(response_text):
        block_content = match.group(1)
        
        is_plans_target = any(pid in block_content for pid in plans_ids)
        if not is_plans_target:
            continue
        
        try:
            props_match = re.search(
                r'"properties"\s*:\s*(\{.*?\})\s*(?:,|\})',
                block_content,
                re.DOTALL,
            )
            if props_match:
                props_json = props_match.group(1)
                if '"Slug"' in props_json or '"Status"' in props_json:
                    payloads.append({"raw": block_content, "properties_hint": True})
        except Exception:
            pass
    
    return payloads


def _validate_status(payload: dict[str, Any]) -> tuple[bool, str]:
    """Validate Status field in payload. Returns (is_valid, error_message)."""
    properties = payload.get("properties", {})
    
    status_field = properties.get("Status", {})
    if isinstance(status_field, dict):
        select_field = status_field.get("select", {})
        status_value = select_field.get("name", "")
    else:
        return False, "Status field malformed"
    
    if not status_value:
        return False, "Status field missing"
    
    if status_value in FORBIDDEN_AT_CREATION:
        return False, (
            f"Status '{status_value}' is FORBIDDEN at plan creation. "
            f"Use 'Not Started' (default) or 'Completed' (retrospective)."
        )
    
    if status_value not in VALID_CREATION_STATUSES:
        return False, f"Invalid status '{status_value}'. Must be one of: {VALID_CREATION_STATUSES}"
    
    return True, ""


def _validate_slug(payload: dict[str, Any]) -> tuple[bool, str]:
    """Validate Slug field format."""
    properties = payload.get("properties", {})
    
    slug_field = properties.get("Slug", {})
    if isinstance(slug_field, dict):
        title_field = slug_field.get("title", [{}])
        if title_field and isinstance(title_field, list):
            text_field = title_field[0].get("text", {})
            slug_value = text_field.get("content", "")
        else:
            slug_value = ""
    else:
        slug_value = ""
    
    if not slug_value:
        return False, "Slug field missing"
    
    if not SLUG_PATTERN.match(slug_value):
        return False, f"Invalid slug '{slug_value}'. Expected format: kebab-case-6hex"
    
    return True, ""


def _validate_required_fields(payload: dict[str, Any]) -> tuple[bool, str]:
    """Validate all required fields present."""
    properties = payload.get("properties", {})
    
    required = ["Slug", "Status", "Summary", "AI Summary " ]
    missing = []
    
    for field in required:
        if field not in properties:
            missing.append(field)
    
    exists_field = properties.get("Exists On Disk", {})
    if not isinstance(exists_field, dict) or "checkbox" not in exists_field:
        missing.append("Exists On Disk")
    
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, ""


def _check_payload(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Full validation of plan creation payload. Returns (is_valid, list_of_errors)."""
    errors: list[str] = []
    
    valid, error = _validate_required_fields(payload)
    if not valid:
        errors.append(error)
    
    valid, error = _validate_slug(payload)
    if not valid:
        errors.append(error)
    
    valid, error = _validate_status(payload)
    if not valid:
        errors.append(error)
    
    return len(errors) == 0, errors


# =============================================================================
# POST-FLIGHT AUDIT (from post_agent_plan_creation_audit)
# =============================================================================

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
    """Extract successful plan creation events from Cursor Agent response."""
    creations = []
    
    invoke_pattern = re.compile(
        r'<invoke[^>]*name="(?:mcp\d+_)?API-post-page"[^>]*>(.*?)</invoke>',
        re.DOTALL,
    )
    
    for match in invoke_pattern.finditer(response_text):
        block = match.group(1)
        
        if PLANS_DATA_SOURCE_ID not in block:
            continue
        
        result_match = re.search(r'"id"\s*:\s*"([a-f0-9-]+)"', block)
        
        if result_match:
            page_id = result_match.group(1)
            
            slug_match = re.search(r'"Slug"[^}]*"content"\s*:\s*"([^"]+)"', block)
            slug = slug_match.group(1) if slug_match else "unknown"
            
            status_match = re.search(r'"Status"[^}]*"name"\s*:\s*"([^"]+)"', block)
            status = status_match.group(1) if status_match else "unknown"
            
            creations.append({
                "slug": slug,
                "page_id": page_id,
                "status": status,
                "source": "response_block",
            })
    
    marker_pattern = re.compile(r'PLAN_CREATED:\s*plan=([a-z0-9-]+)')
    for match in marker_pattern.finditer(response_text):
        slug = match.group(1)
        if not any(c["slug"] == slug for c in creations):
            creations.append({
                "slug": slug,
                "page_id": None,
                "status": "marker_only",
                "source": "marker",
            })
    
    return creations


def _validate_created_status(status: str) -> tuple[bool, str, str]:
    """Validate status of newly created plan. Returns (is_valid, recommended_status, reason)."""
    if status in VALID_CREATION_STATUSES:
        return True, status, "Valid creation status"
    
    if status in FORBIDDEN_AT_CREATION:
        return False, "Not Started", f"Status '{status}' forbidden at creation"
    
    return False, "Not Started", f"Unknown status '{status}'"


def _patch_plan_status(page_id: str, new_status: str) -> tuple[bool, str | None]:
    """Auto-correct plan status via Notion API. Returns (success, error_message)."""
    token = _notion_token()
    if not token:
        return False, "No NOTION_TOKEN available for correction"
    
    if os.environ.get("PLAN_CREATION_AUTO_CORRECT_BYPASS") == "1":
        return False, "PLAN_CREATION_AUTO_CORRECT_BYPASS=1"
    
    url = f"{_NOTION_BASE}/pages/{page_id}"
    
    payload = {
        "properties": {
            "Status": {"select": {"name": new_status}}
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


def _process_creation(creation: dict[str, Any]) -> CorrectionEvent | AlertEvent | None:
    """Process a single plan creation event."""
    slug = creation["slug"]
    page_id = creation.get("page_id")
    status = creation["status"]
    
    is_valid, recommended, reason = _validate_created_status(status)
    
    if is_valid:
        return None
    
    if not page_id:
        return AlertEvent(
            timestamp=datetime.now().isoformat(),
            slug=slug,
            page_id=None,
            alert_type="missing_page_id",
            message=f"Status '{status}' is invalid but no page_id for correction",
            recommended_action="Manual correction required",
        )
    
    success, error = _patch_plan_status(page_id, recommended)
    
    if success:
        return CorrectionEvent(
            timestamp=datetime.now().isoformat(),
            slug=slug,
            page_id=page_id,
            wrong_status=status,
            corrected_status=recommended,
            correction_ok=True,
        )
    else:
        return AlertEvent(
            timestamp=datetime.now().isoformat(),
            slug=slug,
            page_id=page_id,
            alert_type="correction_failed",
            message=f"Status '{status}' invalid but correction failed: {error}",
            recommended_action="Manual correction required",
        )


# =============================================================================
# CURSOR beforeMCPExecution STAGE 2 (AFTER pre_mcp_gate)
# =============================================================================


def _ensure_hook_import_path() -> None:
    hooks = _REPO_ROOT / ".claude" / "hooks"
    hs = str(hooks)
    if hs not in sys.path:
        sys.path.insert(0, hs)


def _mcp_tool_targets_plans_create(tool_short: str, tool_input: dict[str, Any]) -> bool:
    if tool_short != "API-post-page":
        return False
    parent = tool_input.get("parent")
    if not isinstance(parent, dict):
        return False
    db_id = parent.get("database_id")
    if db_id and str(db_id) in PLANS_PARENT_IDS:
        return True
    ds = parent.get("data_source_id")
    if ds and str(ds) in PLANS_PARENT_IDS:
        return True
    return False


def run_mcp_plan_auditor_stage(payload: dict[str, Any]) -> int:
    """
    Cursor ``beforeMCPExecution`` stage 2 — runs after ``pre_mcp_gate`` allows.

    Exit 0 = allow, 2 = BLOCK (stderr carries ``[PLAN_AUDITOR_BLOCK]`` / ``[PLAN_CREATION_BLOCK]``).
    """
    if os.environ.get("NOTION_PLAN_CREATION_GATE_BYPASS") == "1":
        print("[unified-auditor] BYPASS: NOTION_PLAN_CREATION_GATE_BYPASS=1", file=sys.stderr)
        return 0

    _ensure_hook_import_path()
    from lib.claude_hook_common import (  # noqa: PLC0415
        normalize_mcp_payload,
        parse_mcp_tool_input,
        resolve_mcp_server_name,
        strip_mcp_tool_prefix,
    )

    normalized = normalize_mcp_payload(payload)
    server = resolve_mcp_server_name(payload, normalized).strip().lower()
    tool_raw = str(normalized.get("tool_info", {}).get("mcp_tool_name", ""))
    tool_short = strip_mcp_tool_prefix(tool_raw)

    if server != _NOTION_MCP_SERVER_KEY:
        print(
            f"[PLAN_AUDITOR] NOT_APPLICABLE reason=non_notion_mcp server={server or '<unknown>'}",
            file=sys.stderr,
        )
        return 0

    if tool_short == "API-patch-page":
        print(
            "[PLAN_AUDITOR] NOT_APPLICABLE reason=notion_plan_patch_deferred_w1 tool=API-patch-page",
            file=sys.stderr,
        )
        return 0

    if tool_short != "API-post-page":
        print(
            f"[PLAN_AUDITOR] NOT_APPLICABLE reason=not_plans_create_tool tool={tool_raw or '<empty>'}",
            file=sys.stderr,
        )
        return 0

    args = parse_mcp_tool_input(payload)
    if args is None:
        print(
            "[PLAN_AUDITOR_BLOCK] code=MCP_TOOL_INPUT_JSON_INVALID reason=cannot_parse_tool_input",
            file=sys.stderr,
        )
        return 2

    if not _mcp_tool_targets_plans_create(tool_short, args):
        parent = args.get("parent")
        parent_kind = ""
        pid = ""
        if isinstance(parent, dict):
            if parent.get("database_id"):
                parent_kind = "database_id"
                pid = str(parent.get("database_id"))
            elif parent.get("data_source_id"):
                parent_kind = "data_source_id"
                pid = str(parent.get("data_source_id"))
        print(
            f"[PLAN_AUDITOR] NOT_APPLICABLE reason=not_plans_database parent={parent_kind}:{pid or '<missing>'}",
            file=sys.stderr,
        )
        return 0

    notion_body: dict[str, Any] = {"properties": args.get("properties", {})}
    if not notion_body["properties"]:
        print(
            "[PLAN_AUDITOR_BLOCK] code=PLAN_CREATE_MISSING_PROPERTIES reason=API-post-page_missing_properties",
            file=sys.stderr,
        )
        return 2

    ok, errors = _check_payload(notion_body)
    if not ok:
        for error in errors:
            print(f"[PLAN_CREATION_BLOCK] {error}", file=sys.stderr)
        return 2

    print("[PLAN_AUDITOR] APPLICABLE outcome=ALLOW reason=plans_create_payload_ok", file=sys.stderr)
    return 0


# =============================================================================
# UNIFIED ENTRY POINTS
# =============================================================================

def run_pre_flight() -> int:
    """
    Pre-flight validation (blocking mode).
    
    Runs in pre-cursor_agent or pre-mcp chain.
    Exit 0 = allow, Exit 2 = BLOCK
    """
    if os.environ.get("NOTION_PLAN_CREATION_GATE_BYPASS") == "1":
        print("[unified-auditor] BYPASS: NOTION_PLAN_CREATION_GATE_BYPASS=1", file=sys.stderr)
        return 0
    
    input_data = _get_payload_from_stdin()
    
    if input_data is None:
        return 0
    
    response_text = input_data.get("response_text", "")
    
    if response_text:
        payloads = _extract_plans_creation_payloads(response_text)
        
        if not payloads:
            return 0
        
        for payload in payloads:
            is_valid, errors = _check_payload(payload)
            if not is_valid:
                for error in errors:
                    print(f"[PLAN_CREATION_BLOCK] {error}", file=sys.stderr)
                return 2
    
    return 0


def run_post_flight() -> int:
    """
    Post-flight audit (advisory mode).
    
    Runs after Cursor Agent response.
    Always exits 0, logs corrections/alerts.
    """
    input_data = _get_payload_from_stdin()
    
    if input_data is None:
        return 0
    
    response_text = input_data.get("response_text", "")
    
    if not response_text:
        return 0
    
    creations = _extract_plan_creation_from_response(response_text)
    
    for creation in creations:
        result = _process_creation(creation)
        
        if isinstance(result, CorrectionEvent):
            _log_correction(result)
            print(f"[CORRECTION] {result.slug}: {result.wrong_status} -> {result.corrected_status}", file=sys.stderr)
        elif isinstance(result, AlertEvent):
            _log_alert(result)
            print(f"[ALERT] {result.slug}: {result.message}", file=sys.stderr)
    
    return 0


def main() -> int:
    """
    Main entry point.
    
    Determines mode from argv[1]:
    - 'mcp_before': Cursor beforeMCPExecution JSON on stdin (after pre_mcp_gate)
    - 'pre': Run pre-flight validation (blocking)
    - 'post': Run post-flight audit (advisory)
    - Default: Run both (pre then post logic detection)
    """
    if len(sys.argv) > 1 and sys.argv[1] == "mcp_before":
        raw = sys.stdin.read()
        if not raw.strip():
            print(
                "[PLAN_AUDITOR_BLOCK] code=MCP_HOOK_EMPTY_STDIN reason=no_payload_for_mcp_before",
                file=sys.stderr,
            )
            return 2
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            print(
                "[PLAN_AUDITOR_BLOCK] code=MCP_HOOK_JSON reason=mcp_before_stdin_not_json",
                file=sys.stderr,
            )
            return 2
        if not isinstance(parsed, dict):
            print(
                "[PLAN_AUDITOR_BLOCK] code=MCP_HOOK_PAYLOAD reason=mcp_before_stdin_not_object",
                file=sys.stderr,
            )
            return 2
        return run_mcp_plan_auditor_stage(parsed)

    if len(sys.argv) > 1 and sys.argv[1] == "pre":
        return run_pre_flight()
    elif len(sys.argv) > 1 and sys.argv[1] == "post":
        return run_post_flight()
    else:
        # Auto-detect: if input looks like pre-flight, run pre, else post
        input_data = _get_payload_from_stdin()
        if input_data and input_data.get("hook_stage") == "pre_mcp_tool_use":
            return run_pre_flight()
        return run_post_flight()


if __name__ == "__main__":
    sys.exit(main())
