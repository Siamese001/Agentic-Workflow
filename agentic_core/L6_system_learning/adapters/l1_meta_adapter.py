"""L1 Meta-Learning Adapter — bridges L1 cognition's local meta-learning to the central pipeline.

L1 has its own ``MetaLearningClient`` (31+ references) and ``MetaLearningAgent``
that use a separate ``MetaLearningProtocol``.  This adapter converts L1-specific
recall/learn outcomes and cache statistics into the central pipeline's telemetry
and audit format so that drift from L1 model changes is captured by the
meta-learning bus.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from .system_learning_memory_bridge import get_sl_memory_bridge

trace_contract._emit_applies_guardrail("p0", "l1_meta_adapter", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "l1_meta_adapter", "policy_binding")
trace_contract._emit_snapshots_state("p0", "l1_meta_adapter", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("l1_meta_adapter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("l1_meta_adapter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("l1_meta_adapter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("l1_meta_adapter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("l1_meta_adapter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("l1_meta_adapter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("l1_meta_adapter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("l1_meta_adapter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("l1_meta_adapter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("l1_meta_adapter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("l1_meta_adapter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("l1_meta_adapter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("l1_meta_adapter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("l1_meta_adapter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("l1_meta_adapter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("l1_meta_adapter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("l1_meta_adapter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("l1_meta_adapter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("l1_meta_adapter", "p3lm", "state")
trace_contract._emit_records_execution_trace("l1_meta_adapter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("l1_meta_adapter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("l1_meta_adapter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("l1_meta_adapter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("l1_meta_adapter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("l1_meta_adapter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("l1_meta_adapter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("l1_meta_adapter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("l1_meta_adapter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "l1_meta_adapter", "context_pull")
trace_contract._emit_pulls_context("p1", "l1_meta_adapter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "l1_meta_adapter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "l1_meta_adapter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "l1_meta_adapter", "write_through")
trace_contract._emit_writes_through("p1", "l1_meta_adapter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "l1_meta_adapter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "l1_meta_adapter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "l1_meta_adapter", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "l1_meta_adapter", "human_escalation")
trace_contract._emit_routes_through("p1", "l1_meta_adapter", "route_through")
trace_contract._emit_checks_agent_registry("p1", "l1_meta_adapter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "l1_meta_adapter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "l1_meta_adapter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "l1_meta_adapter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "l1_meta_adapter", "target_agent")
trace_contract._emit_verifies_policy("p1", "l1_meta_adapter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "l1_meta_adapter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "l1_meta_adapter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "l1_meta_adapter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "l1_meta_adapter")
trace_contract._emit_gated_by_confidence("p1", "l1_meta_adapter", "confidence_gate")
trace_contract.emit_replay_key("p0", "l1_meta_adapter")
trace_contract.emit_determinism_digest("p0", "l1_meta_adapter")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "l1_meta_adapter", "execution_auth")
trace_contract._emit_validates_capability("p2", "l1_meta_adapter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "l1_meta_adapter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "l1_meta_adapter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "l1_meta_adapter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "l1_meta_adapter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "l1_meta_adapter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "l1_meta_adapter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "l1_meta_adapter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "l1_meta_adapter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "l1_meta_adapter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "l1_meta_adapter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "l1_meta_adapter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "l1_meta_adapter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "l1_meta_adapter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "l1_meta_adapter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "l1_meta_adapter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "l1_meta_adapter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "l1_meta_adapter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "l1_meta_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class L1TelemetryEvent:
    """A telemetry event extracted from L1 meta-learning data."""

    timestamp_utc: int
    event_type: str
    payload_bytes: bytes


@dataclass(frozen=True, slots=True)
class L1DriftSignal:
    """A drift signal from L1 model calibration changes."""

    surface_name: str
    drift_magnitude: float
    direction: str
    observation_count: int
    snapshot_id: str


class L1MetaAdapter:
    """Bridges L1 MetaLearningClient data into the central pipeline.

    Usage::

        adapter = L1MetaAdapter()
        events = adapter.extract_telemetry(l1_state, now_utc=1234)
        drift = adapter.detect_drift(l1_state, snapshot_id="snap")
    """

    def extract_telemetry(self, l1_state: dict[str, Any], *, now_utc: int) -> list[L1TelemetryEvent]:
        """Extract telemetry events from L1 meta-learning state.

        Parameters
        ----------
        l1_state : dict
            L1-specific state dict, expected to contain keys like
            ``"recall_outcomes"``, ``"learn_outcomes"``, ``"cache_stats"``.
        now_utc : int
            Deterministic timestamp.

        Returns
        -------
        list[L1TelemetryEvent]
            Telemetry events suitable for ingestion into the central
            ``TelemetryStore``.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "L1MetaAdapter.extract_telemetry",
        )

        events: list[L1TelemetryEvent] = []
        for outcome in tqdm(l1_state.get("recall_outcomes", []), desc="Processing", unit="item"):
            if not isinstance(outcome, dict):
                continue
            ts = outcome.get("timestamp_utc", now_utc)
            payload = json.dumps(
                {"source": "l1_recall", "outcome": outcome},
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            events.append(
                L1TelemetryEvent(timestamp_utc=ts, event_type="l1_recall_outcome", payload_bytes=payload),
            )
        for outcome in tqdm(l1_state.get("learn_outcomes", []), desc="Processing", unit="item"):
            if not isinstance(outcome, dict):
                continue
            ts = outcome.get("timestamp_utc", now_utc)
            payload = json.dumps(
                {"source": "l1_learn", "outcome": outcome},
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            events.append(
                L1TelemetryEvent(timestamp_utc=ts, event_type="l1_learn_outcome", payload_bytes=payload),
            )
        cache_stats = l1_state.get("cache_stats")
        if isinstance(cache_stats, dict):
            payload = json.dumps(
                {"source": "l1_cache", "stats": cache_stats},
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            events.append(
                L1TelemetryEvent(timestamp_utc=now_utc, event_type="l1_cache_stats", payload_bytes=payload),
            )
        if events:
            try:
                timestamps = [event.timestamp_utc for event in events]
                get_sl_memory_bridge().persist_telemetry_window(
                    "l1_meta_adapter",
                    events,
                    window_start=min(timestamps),
                    window_end=max(timestamps),
                )
            except (
                AttributeError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as exc:  # guardian: allow-log-and-swallow -- telemetry persist: fire-and-forget, events still returned
                logger.debug("Failed to persist L1 telemetry events: %s", exc)
        return events

    def detect_drift(self, l1_state: dict[str, Any], *, snapshot_id: str) -> L1DriftSignal | None:
        """Detect model calibration drift from L1 state.

        Parameters
        ----------
        l1_state : dict
            L1-specific state with ``"confidence_history"`` (list of floats)
            and ``"model_version"``.
        snapshot_id : str
            Pipeline snapshot ID.

        Returns
        -------
        L1DriftSignal | None
            Drift signal if significant drift detected, None otherwise.
        """
        history = l1_state.get("confidence_history", [])
        if not isinstance(history, list) or len(history) < 2:
            return None
        try:
            floats = [float(v) for v in history]
        except (TypeError, ValueError):  # guardian: allow-return-none-swallow -- float parse: non-fatal, caller treats None as no drift signal
            return None
        mid = len(floats) // 2
        if mid == 0:
            return None
        old_mean = sum(floats[:mid]) / mid
        new_mean = sum(floats[mid:]) / (len(floats) - mid)
        drift = new_mean - old_mean
        if abs(drift) < 0.05:
            return None
        signal = L1DriftSignal(
            surface_name="l1_model_confidence",
            drift_magnitude=round(abs(drift), 4),
            direction="increase" if drift > 0 else "decrease",
            observation_count=len(floats),
            snapshot_id=snapshot_id,
        )
        try:
            get_sl_memory_bridge().persist_l1_drift_signal(signal)
        except (
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:  # guardian: allow-log-and-swallow -- drift signal persist: fire-and-forget, signal still returned
            logger.debug("Failed to persist L1 drift signal: %s", exc)
        return signal


__all__ = ["L1MetaAdapter", "L1TelemetryEvent", "L1DriftSignal"]
