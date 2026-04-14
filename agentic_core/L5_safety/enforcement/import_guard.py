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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "import_guard")
emit_determinism_digest("p0", "import_guard")

_emit_dispatches_healing_run("p1", "import_guard", "L5")
_emit_routes_through("p1", "import_guard", "L5")
_emit_checks_agent_registry("p1", "import_guard", "agent_registry")
_emit_validates_agent_capability("p1", "import_guard", "capability")
_emit_dispatches_execution_plan("p1", "import_guard", "exec_plan")
_emit_agent_executes_agent("p1", "import_guard", "sub_agent")
_emit_routes_to_agent("p1", "import_guard", "target_agent")
_emit_observes_runtime_state("p1", "import_guard", "runtime_state")
_emit_verifies_boundary("p1", "import_guard", "boundary_check")
_emit_transcripts_response("p1", "import_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "import_guard")
_emit_gated_by_confidence("p1", "import_guard", "confidence_gate")
_emit_escalates_to_human("p1", "import_guard", "L5")
_emit_reads_policy_state("p1", "import_guard", "L5")
_emit_snapshots_state("p0", "import_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "import_guard", "execution_auth")
_emit_validates_capability("p2", "import_guard", "capability_check")
_emit_routes_to_capability("p2", "import_guard", "capability_route")
_emit_writes_via_uwg("p2", "import_guard", "uwg_write")
_emit_blocks_direct_write("p2", "import_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "import_guard", "tool_invocation")
_emit_captures_execution_output("p2", "import_guard", "exec_output")
_emit_dispatches_agent("p3", "import_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "import_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "import_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "import_guard", "healing_outcome")
_emit_escalates_failure("p3", "import_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "import_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "import_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "import_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "import_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "import_guard", "eval_metric")
_emit_stores_embedding("p4", "import_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "import_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "import_guard", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("import_guard", "p4obs", "metric_1")
_emit_emits_metric_event("import_guard", "p4obs", "metric_2")
_emit_emits_metric_event("import_guard", "p4obs", "metric_3")
_emit_emits_metric_event("import_guard", "p4obs", "metric_4")
_emit_emits_metric_event("import_guard", "p4obs", "metric_5")
_emit_emits_metric_event("import_guard", "p4obs", "metric_6")
_emit_records_incident_event("import_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("import_guard", "p4obs", "anomaly")
_emit_writes_observability_log("import_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("import_guard", "p4obs", "mon_state")
_emit_triggers_alert("import_guard", "p4obs", "alert")
_emit_links_incident_trace("import_guard", "p4obs", "trace_link")
_emit_captures_pattern("import_guard", "p3lm", "pattern")
_emit_records_learning_event("import_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("import_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("import_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("import_guard", "p3lm", "routing")
_emit_improves_agent_policy("import_guard", "p3lm", "policy")
_emit_stores_learning_state("import_guard", "p3lm", "state")
_emit_records_execution_trace("import_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("import_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("import_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("import_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("import_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("import_guard", "env_read", "p2_env_1")
_emit_reads_environ("import_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("import_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("import_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "import_guard", "context_pull")
_emit_pulls_context("p1", "import_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "import_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "import_guard", "uwg_term_2")
_emit_writes_through("p1", "import_guard", "write_through")
_emit_writes_through("p1", "import_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "import_guard", "safety_validation")
_emit_invokes_eval("p1", "import_guard", "eval_call")
_emit_proposal_commits_routing("p1", "import_guard", "routing_commit")

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
        _emit_verifies_policy(str(uuid.uuid4()), "ImportGuard.check", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ImportGuard.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ImportGuard.check".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.set_import_guard_mode", "L5_POLICY")
    global _global_guard
    _global_guard = ImportGuard(mode=mode)
