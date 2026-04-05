"""HealCheckResult Adapter — Tier 3 Convergence Bridge.

Converts unstructured agent dict results to canonical HealCheckResult
for execute_ssot <-> remediation_dispatcher convergence.

Agents emit heterogeneous dicts today; this adapter normalises them to
the typed contract without requiring agents to change their return shape.
Absolute paths in changes_made are converted to repo-relative before
constructing HealCheckResult (which rejects absolute paths).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.types.heal_contract_types import (
    HealCheckResult,
    HealStatus,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "heal_result_adapter")
# Mirror the pattern used by HealCheckResult.__post_init__ to detect absolute paths.
# Must be kept in sync with heal_contract_types._ABS_PATH_RE.
_ABS_PATH_RE = re.compile(r"^[A-Za-z]:|^/")


def adapt_heal_result(
    agent_name: str,
    raw_result: dict[str, Any] | str | None,
    repo_root: str | Path | None = None,
) -> HealCheckResult:
    """Adapt unstructured agent result to canonical HealCheckResult.

    Args:
        agent_name: Name of the agent that produced the result.
        raw_result: Raw output from agent.heal_repository() — dict, str, or None.
        repo_root: Repository root used to convert absolute paths to relative.
                   When None the current working directory is used as fallback.

    Returns:
        Canonical HealCheckResult with contract-compliant field values.

    Raises:
        ValueError: Only if agent_name is empty (programming error).
    """
    if not agent_name:
        raise ValueError("agent_name must not be empty")

    _root = Path(repo_root).resolve() if repo_root else Path.cwd()

    # Normalise raw_result to a dict
    if isinstance(raw_result, str):
        result_dict: dict[str, Any] = {"raw_output": raw_result}
    elif raw_result is None:
        result_dict = {"raw_output": "No output returned"}
    else:
        result_dict = raw_result

    status = _extract_status(result_dict)
    changes_made = _extract_changes_made(result_dict, agent_name, _root)
    rollback_info: str | None = result_dict.get("rollback_info") or result_dict.get("rollback")  # type: ignore[assignment]
    notes: str | None = result_dict.get("notes") or result_dict.get("error_message")  # type: ignore[assignment]
    # Stringify errors but never store exception objects as notes
    if notes is None and "error" in result_dict:
        err = result_dict["error"]
        notes = str(err) if err is not None else None
    needs_llm = _determine_llm_escalation(result_dict, status, changes_made)
    escalation_hint = _build_escalation_hint(result_dict, agent_name, status) if needs_llm else None

    return HealCheckResult(
        check_id=agent_name,
        status=status,
        changes_made=tuple(changes_made),
        rollback_info=rollback_info,
        notes=notes,
        needs_llm_escalation=needs_llm,
        escalation_hint=escalation_hint,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_status(d: dict[str, Any]) -> HealStatus:
    """Map common result dict patterns to HealStatus."""
    # 1. Explicit status string
    if "status" in d:
        sv = str(d["status"]).upper()
        _MAP = {
            "HEALED": HealStatus.HEALED,
            "SUCCESS": HealStatus.HEALED,
            "FIXED": HealStatus.HEALED,
            "PARTIAL": HealStatus.PARTIAL,
            "PARTIALLY_FIXED": HealStatus.PARTIAL,
            "FAILED": HealStatus.FAILED,
            "ERROR": HealStatus.FAILED,
            "FAILURE": HealStatus.FAILED,
            "SKIPPED": HealStatus.SKIPPED,
            "NO_ACTION": HealStatus.SKIPPED,
        }
        if sv in _MAP:
            return _MAP[sv]

    # 2. Boolean success flag
    if "success" in d:
        return HealStatus.HEALED if d["success"] else HealStatus.FAILED

    # 3. Presence of error key
    if "error" in d or d.get("error_message"):
        return HealStatus.FAILED

    # 4. files_healed count
    fh = d.get("files_healed")
    if isinstance(fh, int):
        return HealStatus.HEALED if fh > 0 else HealStatus.SKIPPED

    # 5. Default — treat as success for backward compatibility
    return HealStatus.HEALED


def _to_relative(path_str: str, root: Path) -> str:
    """Convert path_str to repo-relative POSIX string if it looks absolute.

    Uses the same pattern as HealCheckResult.__post_init__ so the sanitised
    string always passes the contract validator.
    """
    if not _ABS_PATH_RE.match(path_str):
        return path_str  # already relative — pass through unchanged

    # Resolve platform path and attempt relative_to(repo_root)
    try:
        p = Path(path_str)
        rel = p.resolve().relative_to(root)
        return rel.as_posix()
    except ValueError as e:
        # TODO: Add proper input validation
        logger.warning(f"Invalid input: {e}")
        # Absolute but outside the repo — use just the final path component
        return Path(path_str).name


def _extract_changes_made(d: dict[str, Any], agent_name: str, root: Path) -> list[str]:
    """Extract and sanitise list of changes from result dict."""
    changes: list[str] = []

    def _add_paths(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                changes.append(_to_relative(str(item), root))
        elif isinstance(value, str) and value.strip():
            changes.append(_to_relative(value.strip(), root))
        elif isinstance(value, int) and value > 0:
            changes.append(f"Fixed {value} files")

    # Priority order: explicit changes_made > files_healed > files_modified > violations_fixed
    if "changes_made" in d:
        _add_paths(d["changes_made"])
    if "files_healed" in d:
        _add_paths(d["files_healed"])
    if "files_modified" in d:
        _add_paths(d["files_modified"])
    if "violations_fixed" in d:
        count = d["violations_fixed"]
        if isinstance(count, int) and count > 0:
            changes.append(f"Fixed {count} violations")

    # Summary string fallback
    if not changes and "summary" in d:
        changes.append(str(d["summary"]))

    # raw_output fallback (string/None normalised at call site)
    if not changes and "raw_output" in d:
        raw = d["raw_output"]
        if isinstance(raw, str) and raw.strip():
            changes.append(raw.strip())

    # Final fallback — never return empty tuple (contract allows it, but aids debugging)
    if not changes:
        changes.append(f"{agent_name}: no changes reported")

    return changes


def _determine_llm_escalation(d: dict[str, Any], status: HealStatus, changes_made: list[str]) -> bool:
    """Return True iff LLM escalation is required."""
    # Agent explicitly set the flag
    if "needs_llm_escalation" in d:
        return bool(d["needs_llm_escalation"])

    # Partial success always needs escalation for remaining issues
    if status == HealStatus.PARTIAL:
        return True

    # Failed with complex-sounding error
    if status == HealStatus.FAILED:
        error_msg = str(d.get("error", "")).lower()
        _COMPLEX = {"complex", "rewrite", "architecture", "multiple", "cascade", "semantic"}
        return any(kw in error_msg for kw in _COMPLEX)

    # Unusually large change set suggests complexity
    if len(changes_made) > 10:
        return True

    return False


def _build_escalation_hint(d: dict[str, Any], agent_name: str, status: HealStatus) -> str:
    """Build space-delimited structured hint string for tier routing."""
    parts: list[str] = []
    if "failure_type" in d:
        parts.append(f"failure_type={d['failure_type']}")
    if "blast_radius" in d:
        parts.append(f"blast_radius={d['blast_radius']}")
    parts.append(f"status={status.value}")
    parts.append(f"agent={agent_name}")
    if status == HealStatus.FAILED and "error" in d:
        parts.append(f"error_type={type(d['error']).__name__}")
    return " ".join(parts)
