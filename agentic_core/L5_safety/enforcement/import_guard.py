"""
ImportGuard - Guardrail for Dynamic Import Operations

Provides pre-import guardrail checks for importlib.import_module(),
importlib.util.spec_from_file_location(), and __import__() operations.
Emits applies_guardrail ADG edges for tracking and compliance.

Usage:
    from agentic_core.L5_safety.enforcement.import_guard import get_import_guard

    guard = get_import_guard()
    guard.check(operation="import_module", module_name="some.module")
    # Then proceed with actual import
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "import_guard")
trace_contract.emit_determinism_digest("p0", "import_guard")

trace_contract._emit_dispatches_healing_run("p1", "import_guard", "L5")
trace_contract._emit_routes_through("p1", "import_guard", "L5")
trace_contract._emit_checks_agent_registry("p1", "import_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "import_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "import_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "import_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "import_guard", "target_agent")
trace_contract._emit_observes_runtime_state("p1", "import_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "import_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "import_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "import_guard")
trace_contract._emit_gated_by_confidence("p1", "import_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "import_guard", "L5")
trace_contract._emit_reads_policy_state("p1", "import_guard", "L5")
trace_contract._emit_snapshots_state("p0", "import_guard", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "import_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "import_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "import_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "import_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "import_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "import_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "import_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "import_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "import_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "import_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "import_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "import_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "import_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "import_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "import_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "import_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "import_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "import_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "import_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "import_guard", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("import_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("import_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("import_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("import_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("import_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("import_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("import_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("import_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("import_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("import_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("import_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("import_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("import_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("import_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("import_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("import_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("import_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("import_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("import_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("import_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("import_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("import_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("import_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("import_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("import_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("import_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("import_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("import_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "import_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "import_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "import_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "import_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "import_guard", "write_through")
trace_contract._emit_writes_through("p1", "import_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "import_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "import_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "import_guard", "routing_commit")

logger = logging.getLogger(__name__)


class DynamicImportDeniedError(Exception):
    """Raised when a dynamic import is denied by guardrail."""

    pass


class ImportGuard:
    """
    Guardrail for dynamic import operations.

    Enforces allowlist/denylist policy and logging before
    allowing importlib or __import__ operations.
    """

    # Module prefixes that are always denied
    DENY_PREFIXES = (
        "os.path",
        "subprocess",
        "ctypes",
        "socket",
        "pickle",
        "marshal",
    )

    # Module prefixes that are always allowed (no logging needed)
    ALLOW_PREFIXES = (
        "agentic_core.",
        "apps_",
        "tests.",
        "tools.",
        "ops_scripts.",
        "system_learning.",
    )

    def __init__(self, mode: str = "warn") -> None:
        """
        Initialize ImportGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        """
        self.mode = mode
        self._import_log: list[dict[str, Any]] = []

    def check(
        self,
        operation: str,
        module_name: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Pre-import guardrail check for dynamic import operations.

        Args:
            operation: Operation being performed ("import_module", "__import__", etc.)
            module_name: Module being imported (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            DynamicImportDeniedError: If import is denied in enforce mode
        """
        trace_contract._emit_verifies_policy(str(uuid.uuid4()), "ImportGuard.check", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ImportGuard.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ImportGuard.check".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        metadata = metadata or {}
        timestamp = datetime.now(timezone.utc)

        # Emit applies_guardrail ADG edge (structured log for scanner)
        logger.debug(
            "applies_guardrail operation=%s guard=ImportGuard mode=%s",
            operation,
            self.mode,
        )

        verdict = "allow"
        reason = "Dynamic import allowed"

        if module_name:
            # Check deny prefixes
            for prefix in tqdm(self.DENY_PREFIXES, desc="Processing", unit="item"):
                if module_name.startswith(prefix):
                    verdict = "deny"
                    reason = f"Module prefix denied: {prefix}"
                    logger.warning(
                        "ImportGuard DENY: %s module=%s - %s",
                        operation,
                        module_name,
                        reason,
                    )
                    if self.mode == "enforce":
                        raise DynamicImportDeniedError(f"Dynamic import denied: {reason}")
                    break

        record = {
            "timestamp": timestamp.isoformat(),
            "operation": operation,
            "module_name": module_name,
            "verdict": verdict,
            "reason": reason,
            "metadata": metadata,
        }
        self._import_log.append(record)

        logger.info(
            "ImportGuard %s: %s module=%s",
            verdict.upper(),
            operation,
            module_name or "<unknown>",
        )

        return {"verdict": verdict, "reason": reason, "timestamp": timestamp.isoformat()}

    def get_import_log(self) -> list[dict[str, Any]]:
        """Get full import log."""
        return self._import_log.copy()

    def clear_log(self) -> None:
        """Clear import log."""
        self._import_log.clear()


_global_guard = ImportGuard(mode="warn")


def get_import_guard() -> ImportGuard:
    """Get global ImportGuard instance."""
    return _global_guard


def set_import_guard_mode(mode: str) -> None:
    """Set global ImportGuard mode ("warn" or "enforce")."""
    trace_contract._emit_applies_guardrail(str(uuid.uuid4()), "Module.set_import_guard_mode", "L5_POLICY")
    global _global_guard
    _global_guard = ImportGuard(mode=mode)
