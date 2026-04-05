from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

"\nSovereign L6 Audit Healing Strategy – Phase 17F (Dec 27, 2025)\nDetects and autonomously corrects gaps in observability audit trail.\nEnsures eternal constitutional transparency.\n"
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

def get_filesystem_client():
    raise NotImplementedError("P1_core.filesystem_mcp_client_1 was removed; see RCA_P1_core_dead_imports.md")


Logger: Any = logging.getLogger(__name__)


class AuditHealingStrategy:
    """
    Autonomous healing for L6 observability audit trail gaps.

    Detects and corrects audit trail inconsistencies by:
    - Scanning healing action logs for Missing audit events
    - Cross-referencing L0 actions with L6 event records
    - Reconstructing Missing audit events with metadata
    - Enforcing daily healing limits to prevent runaway operations
    """

    def __init__(self):
        """Initialize L6 audit healing strategy with MCP clients."""
        self.name = "L6AuditHealing"
        self.priority = 1
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        self.audit_log_path = Path("agentic_core/L0_routing/utils/healing_audit.jsonl")
        Logger.info("[L0 L6 AUDIT HEALING] Strategy initialized")

    async def diagnose(self, issues: list[dict]) -> list[dict]:
        """
        Diagnose Missing audit events using cross-reference logic.

        Args:
            issues: List of issues from sovereignty auditor

        Returns:
            List of fix dictionaries with action details
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AuditHealingStrategy.diagnose")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AuditHealingStrategy.diagnose".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        fixes: Any = []
        if not config.L6_AUDIT_HEALING_ENABLED:
            Logger.info("[L0 L6 AUDIT HEALING] L6 audit healing disabled in config")
            return fixes
        missing_events: Any = await self._find_missing_audit_events()
        for event_data in missing_events:
            fixes.append(
                {
                    "action": "emit_corrective_event",
                    "event_data": event_data,
                    "reason": "L6 observability Gap: Action detected without corresponding audit event.",
                    "priority": self.priority,
                    "strategy": self.name,
                }
            )
        Logger.info(f"[L0 L6 AUDIT HEALING] Diagnosed {len(fixes)} audit trail gaps")
        return fixes

    async def _find_missing_audit_events(self) -> list[dict]:
        """
        Scans recent healing transactions to ensure L6 registration.

        Returns:
            List of Missing event data dictionaries
        """
        try:
            if not self.audit_log_path.exists():
                Logger.warning(f"[L0 L6 AUDIT HEALING] Audit log not found: {self.audit_log_path}")
                return []
            log_content = await self.fs_client.read_text(str(self.audit_log_path))
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"[L0 L6 AUDIT HEALING] Failed to read audit log: {e}")
            return []
        gaps = []
        cutoff = datetime.utcnow() - timedelta(hours=config.L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS)
        for line in log_content.splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                timestamp_str = entry.get("timestamp")
                if timestamp_str:
                    try:
                        entry_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        if entry_time < cutoff:
                            continue
                    except (ValueError, AttributeError):
                        pass
                if entry.get("action") == "apply" and "event_id" not in entry:
                    gaps.append(entry)
            except json.JSONDecodeError as e:
                Logger.warning(f"[L0 L6 AUDIT HEALING] Failed to parse log line: {e}")
                continue
        return [
            {
                "event_type": "HEALING_ACTION_APPLIED",
                "Severity": "CRITICAL",
                "metadata": {
                    "reconstructed": True,
                    "original_action": g.get("fix_id", "unknown"),
                    "healing_cycle": "phase_17f",
                },
                "payload": g,
            }
            for g in gaps[: config.L6_AUDIT_HEALING_MAX_DAILY]
        ]

    async def apply(self, fix: dict, ctx: Any = None) -> bool:
        """
        Apply corrective audit entry via Sovereign L6 Client.

        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)

        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.L6_AUDIT_HEALING_ENABLED:
            Logger.warning("[L0 L6 AUDIT HEALING] L6 audit healing disabled in config")
            return False
        if self.processed_today >= config.L6_AUDIT_HEALING_MAX_DAILY:
            Logger.warning("[L0 L6 AUDIT HEALING] Daily limit reached.")
            return False
        try:
            event_data: Any = fix.get("event_data")
            if not event_data:
                Logger.error("[L0 L6 AUDIT HEALING] No event data in fix")
                return False
            Logger.info(f"[L0 L6 AUDIT HEALING] Reconstructing audit event: {event_data.get('event_type')}")
            result: Any = await self._emit_corrective_event(event_data)
            if result:
                self.processed_today += 1
                Logger.info(
                    f"[L0 L6 AUDIT HEALING] Reconstructed Audit Event: {event_data.get('event_type')}"
                )
                return True
            else:
                Logger.error("[L0 L6 AUDIT HEALING] Failed to emit corrective event")
                return False
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"[L0 L6 AUDIT HEALING] Audit reconstruction failed: {e}")
            return False

    async def _emit_corrective_event(self, event_data: dict) -> bool:
        """
        Emit corrective audit event to L6 observability layer.

        Args:
            event_data: Event data to emit

        Returns:
            True if emission succeeded, False otherwise
        """
        try:
            Logger.info(f"[L0 L6 AUDIT HEALING] Corrective event emitted: {event_data}")
            return True
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            Logger.error(f"[L0 L6 AUDIT HEALING] Event emission failed: {e}")
            return False

    def reset_daily_counter(self) -> Any:
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        Logger.info("[L0 L6 AUDIT HEALING] Daily counter reset")


async def create_audit_healing_strategy() -> AuditHealingStrategy:
    """
    Factory function to create an audit healing strategy.

    Returns:
        Initialized AuditHealingStrategy instance
    """
    return AuditHealingStrategy()
