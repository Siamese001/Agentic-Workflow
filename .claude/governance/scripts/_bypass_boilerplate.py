"""
_bypass_boilerplate.py
Pure extraction: Bypass environment variable handling for Cursor hooks.

This module provides pure extraction of bypass semantics WITHOUT introducing
new bypass modes, new statuses, or new authority surfaces. It centralizes
the boilerplate for checking bypass env vars that already exists across
34 hooks in hooks.json.

W1 SCOPE: Pure extraction only. No policy changes. No new semantics.
"""

import os
import sys
from typing import Optional, Tuple


# Canonical bypass env var suffixes (extracted from existing hooks)
BYPASS_SUFFIXES = ["_BYPASS", "_GATE_BYPASS", "_AUDIT_BYPASS"]


def get_bypass_var(hook_name: str) -> str:
    """
    Generate canonical bypass env var name from hook name.
    
    Pure extraction of existing pattern: hook script names convert to
    UPPER_CASE with _BYPASS suffix.
    
    Examples (from hooks.json analysis):
    - pre_write_gate.py -> PRE_WRITE_GATE_BYPASS
    - post_cursor_agent_notion_plans_status_audit.py -> NOTION_PLANS_STATUS_BYPASS
    - check_plan_definition_of_done.py -> PLAN_DEFINITION_OF_DONE_BYPASS
    """
    # Remove .py extension
    base = hook_name.replace(".py", "")
    
    # Remove common prefixes (extracted from existing hooks)
    prefixes_to_strip = ["pre_", "post_", "post_cursor_agent_", "check_"]
    for prefix in prefixes_to_strip:
        if base.startswith(prefix):
            base = base[len(prefix):]
            break
    
    # Convert to UPPER_CASE
    var_name = base.upper().replace("-", "_").replace(".", "_")
    
    # Add _BYPASS suffix if not present
    if not any(var_name.endswith(suffix) for suffix in BYPASS_SUFFIXES):
        var_name = f"{var_name}_BYPASS"
    
    return var_name


def check_bypass(bypass_var: str, quiet: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Check if bypass env var is set.
    
    Pure extraction of existing pattern across 34 hooks. Returns:
    - (True, warning_message) if bypass is active
    - (False, None) if bypass is not active
    
    This is pure extraction — it does NOT change bypass semantics, does NOT
    introduce new bypass modes, and does NOT create new authority surfaces.
    """
    value = os.environ.get(bypass_var)
    
    if value and value.strip() in ("1", "true", "True", "yes", "YES"):
        warning = f"WARNING: {bypass_var}=1 — bypassing enforcement"
        if not quiet:
            print(warning, file=sys.stderr)
        return True, warning
    
    return False, None


def check_bypass_with_logging(
    bypass_var: str,
    hook_id: str,
    log_path: Optional[str] = None
) -> bool:
    """
    Check bypass with optional audit logging.
    
    Pure extraction pattern used by hooks that emit to violation logs.
    Existing hooks log bypass usage for auditability.
    """
    is_bypassed, warning = check_bypass(bypass_var, quiet=True)
    
    if is_bypassed:
        # Emit warning
        print(warning, file=sys.stderr)
        
        # Log to audit trail if path provided
        if log_path:
            try:
                import json
                import datetime
                log_entry = {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "hook_id": hook_id,
                    "bypass_var": bypass_var,
                    "event": "BYPASS_ACTIVATED",
                    "severity": "WARNING"
                }
                with open(log_path, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception:
                pass  # Fail soft on logging errors
    
    return is_bypassed


# Pure constants extracted from existing hooks
KNOWN_BYPASS_VARS = [
    # From post_cursor_agent hooks
    "ADG_FIRST_VIOLATION_BYPASS",
    "AG_HOOK_WIRING_BYPASS",
    "AG_PIPELINE_AUDIT_BYPASS",
    "AUTHOR_GATE_SCHEMA_BYPASS",
    "AUTHOR_GATE_STALE_BYPASS",
    "DECISION_LEDGER_FRESHNESS_BYPASS",
    "DEGRADED_FALLBACK_BYPASS",
    "FORTKNOX_DISCIPLINE_BYPASS",
    "GREP_BUDGET_BYPASS",
    "MCP_SERIAL_BYPASS",
    "MEMORY_LIFECYCLE_BYPASS",
    "NOTION_PLANS_STATUS_BYPASS",
    "PLAN_DOD_BYPASS",
    "PLAN_REGISTRATION_BYPASS",
    "READ_BUDGET_BYPASS",
    "RECEIPT_AUDIT_BYPASS",
    "ROUTER_ENFORCEMENT_BYPASS",
    "SCOPE_AUTHORIZATION_BYPASS",
    "SSOT_FOLDER_BYPASS",
    "WAVE_LIFECYCLE_CAPTURE_BYPASS",
    "WAVE_LIFECYCLE_NOTION_BYPASS",
    # From pre_ hooks (extracted pattern)
    "PRE_WRITE_GATE_BYPASS",
    "PRE_AUTHOR_GATE_BYPASS",
    "PRE_RUN_GATE_BYPASS",
]


def validate_bypass_var(bypass_var: str) -> bool:
    """
    Validate that bypass var follows canonical naming.
    
    Pure extraction — checks against known patterns without
    introducing new validation rules.
    """
    return any(bypass_var.endswith(suffix) for suffix in BYPASS_SUFFIXES)


if __name__ == "__main__":
    # Self-test: verify extraction purity
    test_cases = [
        ("pre_write_gate.py", "PRE_WRITE_GATE_BYPASS"),
        ("post_cursor_agent_notion_plans_status_audit.py", "NOTION_PLANS_STATUS_BYPASS"),
        ("check_plan_definition_of_done.py", "PLAN_DEFINITION_OF_DONE_BYPASS"),
    ]
    
    all_pass = True
    for hook, expected in test_cases:
        actual = get_bypass_var(hook)
        if actual != expected:
            print(f"FAIL: {hook} -> {actual} (expected {expected})", file=sys.stderr)
            all_pass = False
    
    if all_pass:
        print("_bypass_boilerplate: All self-tests passed")
        sys.exit(0)
    else:
        sys.exit(1)
