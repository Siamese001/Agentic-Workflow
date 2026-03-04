"""HealCheckResult Adapter Layer - Tier 3 Convergence.

Converts unstructured agent dict results to canonical HealCheckResult
for execute_ssot ↔ remediation_dispatcher convergence.

This is a bridge - agents will gradually migrate to emit HealCheckResult
directly, but this adapter ensures immediate compatibility.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)


def adapt_heal_result(
    agent_name: str,
    raw_result: dict[str, Any] | str | None,
    violations_submitted: int = 0,
) -> HealCheckResult:
    """Adapt unstructured agent result to canonical HealCheckResult.

    Args:
        agent_name: Name of the agent that produced the result
        raw_result: Raw output from agent.heal_repository() (dict, string, or None)
        violations_submitted: Number of violations the agent attempted to fix

    Returns:
        Canonical HealCheckResult for unified processing
    """
    # Normalize raw_result to dict
    if isinstance(raw_result, str):
        result_dict = {"raw_output": raw_result}
    elif raw_result is None:
        result_dict = {"raw_output": "No output returned"}
    else:
        result_dict = raw_result

    # Extract status from common patterns
    status = _extract_status(result_dict)

    # Extract changes_made from common patterns
    changes_made = _extract_changes_made(result_dict, agent_name)

    # Extract rollback info if present
    rollback_info = result_dict.get("rollback_info") or result_dict.get("rollback")

    # Extract notes/error info
    notes = result_dict.get("notes") or result_dict.get("error") or result_dict.get("message")

    # Determine if LLM escalation is needed
    needs_llm_escalation = _determine_llm_escalation(result_dict, status, changes_made)

    # Build escalation hint if needed
    escalation_hint = (
        _build_escalation_hint(result_dict, agent_name, status) if needs_llm_escalation else None
    )

    return HealCheckResult(
        check_id=agent_name,
        status=status,
        changes_made=tuple(changes_made),
        rollback_info=rollback_info,
        notes=notes,
        needs_llm_escalation=needs_llm_escalation,
        escalation_hint=escalation_hint,
    )


def _extract_status(result_dict: dict[str, Any]) -> HealStatus:
    """Extract HealStatus from result dict using common patterns."""
    # Check explicit status field
    if "status" in result_dict:
        status_val = str(result_dict["status"]).upper()
        if status_val in ("HEALED", "SUCCESS", "FIXED"):
            return HealStatus.HEALED
        elif status_val in ("PARTIAL", "PARTIALLY_FIXED"):
            return HealStatus.PARTIAL
        elif status_val in ("FAILED", "ERROR", "FAILURE"):
            return HealStatus.FAILED
        elif status_val in ("SKIPPED", "NO_ACTION"):
            return HealStatus.SKIPPED

    # Check success boolean
    if "success" in result_dict:
        return HealStatus.HEALED if result_dict["success"] else HealStatus.FAILED

    # Check error field (presence indicates failure)
    if "error" in result_dict or result_dict.get("error_message"):
        return HealStatus.FAILED

    # Check for files_healed count
    if "files_healed" in result_dict:
        count = result_dict["files_healed"]
        if isinstance(count, int) and count > 0:
            return HealStatus.HEALED
        elif isinstance(count, int) and count == 0:
            return HealStatus.SKIPPED

    # Default to HEALED for backward compatibility
    return HealStatus.HEALED


def _extract_changes_made(result_dict: dict[str, Any], agent_name: str) -> list[str]:
    """Extract list of changes made from result dict."""
    changes = []

    # Direct changes_made field
    if "changes_made" in result_dict:
        changes_list = result_dict["changes_made"]
        if isinstance(changes_list, list):
            changes.extend(str(c) for c in changes_list)
        elif isinstance(changes_list, str):
            changes.append(changes_list)

    # files_healed field
    if "files_healed" in result_dict:
        files = result_dict["files_healed"]
        if isinstance(files, list):
            changes.extend(str(f) for f in files)
        elif isinstance(files, (str, int)):
            if isinstance(files, int) and files > 0:
                changes.append(f"Fixed {files} files")
            elif isinstance(files, str):
                changes.append(files)

    # files_modified field
    if "files_modified" in result_dict:
        files = result_dict["files_modified"]
        if isinstance(files, list):
            changes.extend(str(f) for f in files)

    # violations_fixed field
    if "violations_fixed" in result_dict:
        count = result_dict["violations_fixed"]
        if isinstance(count, int) and count > 0:
            changes.append(f"Fixed {count} violations")

    # Generic action summary
    if not changes and "summary" in result_dict:
        changes.append(str(result_dict["summary"]))

    # Handle raw_output field (from string/None conversion)
    if not changes and "raw_output" in result_dict:
        raw = result_dict["raw_output"]
        if isinstance(raw, str) and raw.strip():
            changes.append(raw.strip())

    # Fallback to agent name with generic action
    if not changes:
        changes.append(f"{agent_name} healing action")

    return changes


def _determine_llm_escalation(
    result_dict: dict[str, Any], status: HealStatus, changes_made: list[str]
) -> bool:
    """Determine if LLM escalation is needed based on result."""
    # Explicit escalation flag
    if "needs_llm_escalation" in result_dict:
        return bool(result_dict["needs_llm_escalation"])

    # Failed attempts often need escalation
    if status == HealStatus.FAILED:
        # Check if failure reason suggests complexity
        error_msg = str(result_dict.get("error", "")).lower()
        complex_indicators = ["complex", "rewrite", "architecture", "multiple", "cascade"]
        return any(indicator in error_msg for indicator in complex_indicators)

    # Partial success might need escalation for remaining issues
    if status == HealStatus.PARTIAL:
        return True

    # Large number of changes might indicate complexity
    if len(changes_made) > 10:
        return True

    return False


def _build_escalation_hint(result_dict: dict[str, Any], agent_name: str, status: HealStatus) -> str:
    """Build structured escalation hint for tier routing."""
    hints = []

    # Include failure type if available
    if "failure_type" in result_dict:
        hints.append(f"failure_type={result_dict['failure_type']}")

    # Include blast radius if available
    if "blast_radius" in result_dict:
        hints.append(f"blast_radius={result_dict['blast_radius']}")

    # Include status context
    hints.append(f"status={status.value}")

    # Include agent for context
    hints.append(f"agent={agent_name}")

    # Include error class if failed
    if status == HealStatus.FAILED and "error" in result_dict:
        error_type = type(result_dict["error"]).__name__
        hints.append(f"error_type={error_type}")

    return " ".join(hints)
