"""
post_cascade_plan_scope_audit.py — Post-cascade hook for plan scope authorization audit.

Wraps W2 pure logic from _plan_scope_expansion_check.py. Does NOT re-implement marker parsing.

Environment:
    PLAN_SCOPE_AUDIT_STRICT=1     — Enable strict mode (exit 2 on unauthorized drift)
    PLAN_SCOPE_AUDIT_BYPASS=1     — Bypass all checks (exit 0, log bypass)
    MIN_FILES_FOR_AUDIT           — Threshold for "substantial work" (default 3)
    AUTH_MARKER_RECENCY_SEC       — Authorization validity window (default 300)

Logs: artifacts/windsurf/plan_scope_audit.jsonl
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Load W2 module via importlib (can't import from dot-prefixed .windsurf directly)
REPO_ROOT = Path(__file__).parent.parent.parent
W2_MODULE_PATH = REPO_ROOT / ".windsurf" / "scripts" / "_plan_scope_expansion_check.py"

_w2_spec = importlib.util.spec_from_file_location(
    "_plan_scope_expansion_check", W2_MODULE_PATH
)
_w2_module = importlib.util.module_from_spec(_w2_spec)
sys.modules["_plan_scope_expansion_check"] = _w2_module
_w2_spec.loader.exec_module(_w2_module)

# W2 imports — all marker parsing happens in W2
from _plan_scope_expansion_check import (
    check_scope_authorization,
    ScopeAuthorizationResult,
    REASON_OK,
    REASON_MISSING_DISCOVERED,
    REASON_MISSING_AUTHORIZATION,
    REASON_RETROACTIVE,
    REASON_DEFERRED,
    REASON_SPLIT,
    REASON_REJECTED,
    REASON_EXPIRED,
    DEFAULT_AUTH_RECENCY_SEC,
    MIN_FILES_FOR_AUDIT,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOG_PATH = Path("artifacts/windsurf/plan_scope_audit.jsonl")


def get_config() -> dict:
    """Load configuration from environment."""
    return {
        "strict": os.getenv("PLAN_SCOPE_AUDIT_STRICT") == "1",
        "bypass": os.getenv("PLAN_SCOPE_AUDIT_BYPASS") == "1",
        "min_files": int(os.getenv("MIN_FILES_FOR_AUDIT", MIN_FILES_FOR_AUDIT)),
        "recency_sec": int(os.getenv("AUTH_MARKER_RECENCY_SEC", DEFAULT_AUTH_RECENCY_SEC)),
    }


# ---------------------------------------------------------------------------
# Marker Extraction (response text → marker strings)
# ---------------------------------------------------------------------------

# Patterns to detect marker lines in response text
_MARKER_PATTERNS = [
    re.compile(r'DISCOVERED_SCOPE:\s*plan=[\w-]+'),
    re.compile(r'AUTHORIZATION_DECISION:\s*plan=[\w-]+'),
    re.compile(r'SCOPE_EXPANSION:\s*plan=[\w-]+'),
]


def extract_markers_from_text(text: str) -> list[str]:
    """Extract authorization marker lines from response text.
    
    This is NOT parsing — it's just extracting full marker strings.
    All parsing happens in W2.
    """
    markers = []
    for line in text.split('\n'):
        line = line.strip()
        for pattern in _MARKER_PATTERNS:
            if pattern.match(line):
                markers.append(line)
                break
    return markers


# ---------------------------------------------------------------------------
# Plan Detection
# ---------------------------------------------------------------------------

_PLAN_FILE_RE = re.compile(r'[\\/]plan[-_]([a-z0-9-]+)-([a-f0-9]{6,})\.md$', re.IGNORECASE)
_PLAN_EDIT_RE = re.compile(r'file_path=["\']([^"\']*plan[-_][a-z0-9-]+-[a-f0-9]{6,}\.md)["\']', re.IGNORECASE)


def detect_active_plan(response_text: str, file_paths: list[str]) -> str | None:
    """Detect active plan from context.
    
    Strategy:
    1. Look for plan=xxx markers in response
    2. Check file paths for .windsurf/plans/ references
    3. Return first valid plan_id found
    """
    # Check markers in response
    # Match plan=<slug> where slug is descriptive-name-6hex (e.g., foo-bar-a7d4e1)
    # Pattern: starts with letter, contains hyphens, ends with hyphen + 6+ hex chars
    # The non-greedy [a-z0-9-]*? ensures we stop at the last hyphen before hex digits
    marker_match = re.search(r'plan=([a-z][a-z0-9-]*?-[a-f0-9]{6,})\b', response_text, re.IGNORECASE)
    if marker_match:
        return marker_match.group(1).lower()
    
    # Check file paths for plan file references
    for path in file_paths:
        match = _PLAN_FILE_RE.search(path)
        if match:
            return f"{match.group(1)}-{match.group(2)}"
    
    # Check for plan mentions in text (fallback)
    text_match = re.search(r'plan[-_]([a-z][a-z0-9-]*?-[a-f0-9]{6,})\b', response_text, re.IGNORECASE)
    if text_match:
        return text_match.group(1).lower()
    
    return None


# ---------------------------------------------------------------------------
# Work Detection
# ---------------------------------------------------------------------------

def detect_changed_files(response_text: str) -> list[str]:
    """Detect file changes from response text.
    
    Looks for:
    - edit() calls with file paths
    - write_to_file() calls
    - File references in tool calls
    """
    changed = []
    
    # Match edit() and write_to_file() calls
    patterns = [
        re.compile(r'edit\([^)]*file_path=["\']([^"\']+)["\']'),
        re.compile(r'write_to_file\([^)]*TargetFile=["\']([^"\']+)["\']'),
        re.compile(r'<target_file>([^<]+)</target_file>'),
    ]
    
    for pattern in patterns:
        for match in pattern.finditer(response_text):
            path = match.group(1)
            if path and path not in changed:
                changed.append(path)
    
    return changed


# ---------------------------------------------------------------------------
# Audit Logging
# ---------------------------------------------------------------------------

def write_audit_record(
    plan_id: str | None,
    mode: str,
    changed_files_count: int,
    markers_count: int,
    result: ScopeAuthorizationResult | None,
    exit_code: int,
    extra: dict | None = None
) -> None:
    """Write JSONL audit record."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    record: dict[str, Any] = {
        "plan_id": plan_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "changed_files_count": changed_files_count,
        "markers_count": markers_count,
        "exit_code": exit_code,
    }
    
    if result:
        record["authorized"] = result.authorized
        record["reason"] = result.reason
        record["message"] = result.message
        record["decision"] = result.decision
        record["should_warn"] = result.should_warn if hasattr(result, 'should_warn') else False
        record["should_block"] = result.should_block if hasattr(result, 'should_block') else False
    
    # Merge extra fields at top level (not nested)
    if extra:
        for key, value in extra.items():
            record[key] = value
    
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        json.dump(record, f, default=str)
        f.write('\n')


# ---------------------------------------------------------------------------
# Main Hook
# ---------------------------------------------------------------------------

def main() -> int:
    """Post-cascade hook entry point.
    
    Returns:
        0 — authorized or advisory mode warning
        2 — strict mode blocking unauthorized scope drift
    """
    # Load configuration
    config = get_config()
    
    # Check bypass
    if config["bypass"]:
        print("[PLAN_SCOPE_AUDIT] BYPASS enabled via PLAN_SCOPE_AUDIT_BYPASS=1")
        write_audit_record(
            plan_id=None,
            mode="bypass",
            changed_files_count=0,
            markers_count=0,
            result=None,
            exit_code=0,
            extra={"bypass_reason": "PLAN_SCOPE_AUDIT_BYPASS=1"}
        )
        return 0
    
    # Read response from stdin or env (Windsurf passes cascade response)
    response_text = os.getenv("CASCADE_RESPONSE", "")
    if not response_text and not sys.stdin.isatty():
        try:
            response_text = sys.stdin.read()
        except:
            pass
    
    # Detect work and markers
    changed_files = detect_changed_files(response_text)
    markers = extract_markers_from_text(response_text)
    
    # Check substantial work threshold
    if len(changed_files) < config["min_files"]:
        # Not enough files to trigger audit
        return 0
    
    # Detect active plan
    plan_id = detect_active_plan(response_text, changed_files)
    
    if not plan_id:
        # No plan detected, but substantial work detected — advisory warning
        if config["strict"]:
            print(f"[PLAN_SCOPE_AUDIT] BLOCKING: {len(changed_files)} files modified but no active plan detected")
            write_audit_record(
                plan_id=None,
                mode="strict",
                changed_files_count=len(changed_files),
                markers_count=len(markers),
                result=None,
                exit_code=2,
                extra={"reason": "NO_ACTIVE_PLAN"}
            )
            return 2
        else:
            print(f"[PLAN_SCOPE_AUDIT] WARNING: {len(changed_files)} files modified but no active plan detected")
            return 0
    
    # Call W2 for authorization check — W2 handles ALL parsing
    result = check_scope_authorization(
        plan_id=plan_id,
        changed_files=changed_files,
        markers=markers,
        recency_window_sec=config["recency_sec"]
    )
    
    # Determine outcome
    mode = "strict" if config["strict"] else "advisory"
    
    if result.authorized:
        # Authorized — silent success
        write_audit_record(
            plan_id=plan_id,
            mode=mode,
            changed_files_count=len(changed_files),
            markers_count=len(markers),
            result=result,
            exit_code=0
        )
        return 0
    
    # Not authorized — handle based on mode
    reason_codes = [result.reason]
    
    if result.reason == REASON_RETROACTIVE:
        message = f"RETROACTIVE_AUTHORIZATION_DETECTED: Work on {len(changed_files)} files detected before authorization markers"
    elif result.reason == REASON_MISSING_DISCOVERED:
        message = f"MISSING_DISCOVERED_SCOPE: No DISCOVERED_SCOPE marker found for {len(changed_files)} files modified"
    elif result.reason == REASON_MISSING_AUTHORIZATION:
        message = f"MISSING_AUTHORIZATION_DECISION: Work on {len(changed_files)} files without preceding AUTHORIZATION_DECISION"
    elif result.reason == REASON_DEFERRED:
        message = f"AUTHORIZATION_NOT_ACCEPTED: Scope DEFERRED — not authorized for current-plan expansion"
    elif result.reason == REASON_SPLIT:
        message = f"AUTHORIZATION_NOT_ACCEPTED: Scope SPLIT_TO_NEW_PLAN — not authorized for current-plan expansion"
    elif result.reason == REASON_REJECTED:
        message = f"AUTHORIZATION_NOT_ACCEPTED: Scope REJECTED — gold plating or off-charter"
    elif result.reason == REASON_EXPIRED:
        message = f"AUTHORIZATION_EXPIRED: Decision older than {config['recency_sec']}s"
    else:
        message = f"UNAUTHORIZED_SCOPE_DRIFT: {result.message}"
    
    should_block = config["strict"] and (
        result.reason in {REASON_RETROACTIVE, REASON_MISSING_AUTHORIZATION, REASON_EXPIRED}
    )
    
    exit_code = 2 if should_block else 0
    
    if should_block:
        print(f"[PLAN_SCOPE_AUDIT] BLOCKING (strict mode): {message}")
    else:
        print(f"[PLAN_SCOPE_AUDIT] WARNING ({mode} mode): {message}")
    
    write_audit_record(
        plan_id=plan_id,
        mode=mode,
        changed_files_count=len(changed_files),
        markers_count=len(markers),
        result=result,
        exit_code=exit_code,
        extra={"reason_codes": reason_codes}
    )
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
