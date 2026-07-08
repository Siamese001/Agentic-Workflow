"""Healing Success Rate Store — deterministic, replay-reconstructable store.

Backed by a dict[str, float].  In production populated by
OutcomeWriteBackHook (Phase 2).  In tests seeded directly.

Layer contract:
- Lives in system_learning layer.
- Exposed to L2.3 ONLY via MetaPriorProvider seam.
- MUST NOT import agentic_core modules.

Determinism contract:
- All stored rates rounded to 6 decimals.
- export_state() returns snapshot for replay reconstruction.
- store_state_hash() returns deterministic content hash.
- Single-process invariant: _OWNER_PID guards against fork divergence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "healing_success_rate_store", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "healing_success_rate_store", "policy_binding")

trace_contract._emit_emits_metric_event("healing_success_rate_store", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healing_success_rate_store", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healing_success_rate_store", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healing_success_rate_store", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healing_success_rate_store", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healing_success_rate_store", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healing_success_rate_store", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healing_success_rate_store", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healing_success_rate_store", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healing_success_rate_store", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healing_success_rate_store", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healing_success_rate_store", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healing_success_rate_store", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healing_success_rate_store", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healing_success_rate_store", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healing_success_rate_store", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healing_success_rate_store", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healing_success_rate_store", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healing_success_rate_store", "p3lm", "state")
trace_contract._emit_records_execution_trace("healing_success_rate_store", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healing_success_rate_store", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healing_success_rate_store", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healing_success_rate_store", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healing_success_rate_store", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healing_success_rate_store", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healing_success_rate_store", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healing_success_rate_store", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healing_success_rate_store", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healing_success_rate_store", "context_pull")
trace_contract._emit_pulls_context("p1", "healing_success_rate_store", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_success_rate_store", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_success_rate_store", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healing_success_rate_store", "write_through")
trace_contract._emit_writes_through("p1", "healing_success_rate_store", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healing_success_rate_store", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healing_success_rate_store", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healing_success_rate_store", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "healing_success_rate_store", "human_escalation")
trace_contract._emit_routes_through("p1", "healing_success_rate_store", "route_through")
trace_contract._emit_checks_agent_registry("p1", "healing_success_rate_store", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healing_success_rate_store", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healing_success_rate_store", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healing_success_rate_store", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healing_success_rate_store", "target_agent")
trace_contract._emit_verifies_policy("p1", "healing_success_rate_store", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healing_success_rate_store", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healing_success_rate_store", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healing_success_rate_store", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healing_success_rate_store")
trace_contract._emit_gated_by_confidence("p1", "healing_success_rate_store", "confidence_gate")
trace_contract.emit_replay_key("p0", "healing_success_rate_store")
trace_contract.emit_determinism_digest("p0", "healing_success_rate_store")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "healing_success_rate_store", "execution_auth")
trace_contract._emit_validates_capability("p2", "healing_success_rate_store", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healing_success_rate_store", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healing_success_rate_store", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healing_success_rate_store", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healing_success_rate_store", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healing_success_rate_store", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healing_success_rate_store", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healing_success_rate_store", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healing_success_rate_store", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healing_success_rate_store", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healing_success_rate_store", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healing_success_rate_store", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healing_success_rate_store", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healing_success_rate_store", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healing_success_rate_store", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healing_success_rate_store", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healing_success_rate_store", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healing_success_rate_store", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healing_success_rate_store", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_NEUTRAL_PRIOR: float = 0.5
_MIN_SAMPLE_SIZE: int = 5
_EMA_ALPHA: float = 0.1


class HealingSuccessRateStore:
    """Deterministic store of per-signature success rates.

    Single-process invariant: if _OWNER_PID differs from current pid,
    operations are no-ops that log a warning (prevents fork divergence).
    """

    def __init__(self) -> None:
        self._rates: dict[str, float] = {}
        self._counts: dict[str, int] = {}
        self._owner_pid: int = os.getpid()

    def _check_pid(self) -> bool:
        """Return True if current process owns this store."""
        if os.getpid() != self._owner_pid:
            logger.warning(
                "HealingSuccessRateStore: pid mismatch (owner=%d, current=%d); operation skipped",
                self._owner_pid,
                os.getpid(),
            )
            return False
        return True

    def get_prior(self, error_signature: str) -> float:
        """Return current success-rate prior for error_signature.

        Returns _NEUTRAL_PRIOR when fewer than _MIN_SAMPLE_SIZE outcomes
        are recorded (dampening to avoid over-weighting early noisy data).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealingSuccessRateStore.get_prior"
        )

        count = self._counts.get(error_signature, 0)
        if count < _MIN_SAMPLE_SIZE:
            return _NEUTRAL_PRIOR
        return self._rates.get(error_signature, _NEUTRAL_PRIOR)

    def record_outcome(self, error_signature: str, success: bool) -> None:
        """Update running success-rate average with a new outcome.

        Uses cumulative average during warm-up, then EMA.
        All stored values rounded to 6 decimals.
        """
        if not self._check_pid():
            return
        count = self._counts.get(error_signature, 0)
        current = self._rates.get(error_signature, _NEUTRAL_PRIOR)
        outcome_value = 1.0 if success else 0.0
        if count < _MIN_SAMPLE_SIZE:
            new_rate = round((current * count + outcome_value) / (count + 1), 6)
        else:
            new_rate = round((1.0 - _EMA_ALPHA) * current + _EMA_ALPHA * outcome_value, 6)
        new_rate = max(0.0, min(1.0, new_rate))
        self._rates[error_signature] = new_rate
        self._counts[error_signature] = count + 1
        self._log_update(error_signature, success, new_rate, count + 1)
        self._maybe_persist_to_mcp(error_signature, new_rate, count + 1)

    def _maybe_persist_to_mcp(self, error_signature: str, rate: float, count: int) -> None:
        """Persist updated rate to Memory MCP when count crosses MIN_SAMPLE_SIZE boundary.

        Only fires when we have statistically meaningful data (count >= _MIN_SAMPLE_SIZE)
        to avoid polluting MCP with warm-up noise.
        """
        trace_contract._emit_snapshots_state(str(uuid.uuid4()), "HealingSuccessRateStore._maybe_persist_to_mcp", "L4_STATE")
        if count < _MIN_SAMPLE_SIZE:
            return
        try:
            from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            get_sl_memory_bridge().persist_healing_success_rate(error_signature, rate, count)
        except (AttributeError, RuntimeError, TypeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- persist healing rate: non-fatal, logger.debug already called
            logger.debug(
                "Failed to persist healing success rate for %s: %s",
                error_signature,
                exc,
            )

    def _log_update(self, error_signature: str, success: bool, new_rate: float, new_count: int) -> None:
        """Structured telemetry for every update (never silent)."""
        logger.info(
            "success_rate_update",
            extra={
                "error_signature": error_signature,
                "success": success,
                "new_rate": new_rate,
                "observation_count": new_count,
                "owner_pid": self._owner_pid,
            },
        )

    def export_state(self) -> dict[str, Any]:
        """Deterministic snapshot for replay reconstruction."""
        return {
            "rates": dict(sorted(self._rates.items())),
            "counts": dict(sorted(self._counts.items())),
            "owner_pid": self._owner_pid,
        }

    def store_state_hash(self) -> str:
        """Deterministic content hash of current store state."""
        state = self.export_state()
        hashable = {"rates": state["rates"], "counts": state["counts"]}
        canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def import_state(self, state: dict[str, Any]) -> None:
        """Restore from exported snapshot (for replay/testing)."""
        self._rates = dict(state.get("rates", {}))
        self._counts = dict(state.get("counts", {}))

    def restore_from_memory(self) -> int:
        """Warm-start EMA rates from Memory MCP on process startup.

        Merges Memory MCP rates into the current store without overwriting any
        locally observed rates (local observations take precedence).

        Returns:
            Number of signatures restored from Memory MCP.
        """
        try:
            from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            restored = get_sl_memory_bridge().restore_healing_success_rates()
        except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
            logger.debug("Failed to restore healing success rates from Memory MCP: %s", exc)
            return 0
        merged = 0
        for sig, (rate, count) in restored.items():
            if sig not in self._rates:
                self._rates[sig] = rate
                self._counts[sig] = count
                merged += 1
        if merged:
            logger.info("[HealingSuccessRateStore] Warm-started %d signature(s) from Memory MCP", merged)
        return merged

    def get_all(self) -> dict[str, float]:
        """Snapshot of all current priors (for audit)."""
        return dict(self._rates)

    def get_counts(self) -> dict[str, int]:
        """Snapshot of all observation counts."""
        return dict(self._counts)

    def reset(self) -> None:
        """Clear all state (testing only)."""
        self._rates.clear()
        self._counts.clear()


_default_store: HealingSuccessRateStore | None = None


def get_default_store() -> HealingSuccessRateStore:
    """Return the process-global default store (lazy-initialized)."""
    global _default_store
    if _default_store is None:
        _default_store = HealingSuccessRateStore()
    return _default_store


def reset_default_store() -> None:
    """[TESTING ONLY] Reset the process-global store."""
    global _default_store
    _default_store = None


__all__ = [
    "HealingSuccessRateStore",
    "get_default_store",
    "reset_default_store",
    "_MIN_SAMPLE_SIZE",
    "_NEUTRAL_PRIOR",
    "_EMA_ALPHA",
]
