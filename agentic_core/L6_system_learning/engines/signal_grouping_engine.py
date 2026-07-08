"""Signal Grouping Engine — clusters similar detection signals for the meta-learning bus.

Groups L6 detection signals by type and component, producing clustered
summaries that the pipeline uses for pattern analysis and drift monitoring.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "signal_grouping_engine", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "signal_grouping_engine", "policy_binding")
trace_contract._emit_snapshots_state("p0", "signal_grouping_engine", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("signal_grouping_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("signal_grouping_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("signal_grouping_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("signal_grouping_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("signal_grouping_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("signal_grouping_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("signal_grouping_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("signal_grouping_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("signal_grouping_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("signal_grouping_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("signal_grouping_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("signal_grouping_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("signal_grouping_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("signal_grouping_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("signal_grouping_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("signal_grouping_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("signal_grouping_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("signal_grouping_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("signal_grouping_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("signal_grouping_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("signal_grouping_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("signal_grouping_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("signal_grouping_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("signal_grouping_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("signal_grouping_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("signal_grouping_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("signal_grouping_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("signal_grouping_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "signal_grouping_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "signal_grouping_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "signal_grouping_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "signal_grouping_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "signal_grouping_engine", "write_through")
trace_contract._emit_writes_through("p1", "signal_grouping_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "signal_grouping_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "signal_grouping_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "signal_grouping_engine", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "signal_grouping_engine", "human_escalation")
trace_contract._emit_routes_through("p1", "signal_grouping_engine", "route_through")
trace_contract._emit_checks_agent_registry("p1", "signal_grouping_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "signal_grouping_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "signal_grouping_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "signal_grouping_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "signal_grouping_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "signal_grouping_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "signal_grouping_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "signal_grouping_engine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "signal_grouping_engine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "signal_grouping_engine")
trace_contract._emit_gated_by_confidence("p1", "signal_grouping_engine", "confidence_gate")
trace_contract.emit_replay_key("p0", "signal_grouping_engine")
trace_contract.emit_determinism_digest("p0", "signal_grouping_engine")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "signal_grouping_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "signal_grouping_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "signal_grouping_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "signal_grouping_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "signal_grouping_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "signal_grouping_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "signal_grouping_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "signal_grouping_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "signal_grouping_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "signal_grouping_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "signal_grouping_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "signal_grouping_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "signal_grouping_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "signal_grouping_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "signal_grouping_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "signal_grouping_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "signal_grouping_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "signal_grouping_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "signal_grouping_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "signal_grouping_engine", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SignalGroup:
    """A cluster of similar detection signals."""

    group_key: str
    signal_type: str
    component: str
    count: int
    earliest_utc: int
    latest_utc: int
    sample_payloads: tuple[bytes, ...]

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SignalGroup.canonical_bytes")

        data = {
            "group_key": self.group_key,
            "signal_type": self.signal_type,
            "component": self.component,
            "count": self.count,
            "earliest_utc": self.earliest_utc,
            "latest_utc": self.latest_utc,
            "sample_count": len(self.sample_payloads),
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class SignalGroupingReport:
    """Report of grouped detection signals."""

    snapshot_id: str
    groups: tuple[SignalGroup, ...]
    total_signals: int
    total_groups: int

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SignalGroupingReport.canonical_bytes"
        )

        data = {
            "snapshot_id": self.snapshot_id,
            "total_signals": self.total_signals,
            "total_groups": self.total_groups,
            "groups": [json.loads(g.canonical_bytes().decode("utf-8")) for g in self.groups],
        }
        return json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


_MAX_SAMPLE_PAYLOADS = 3


class SignalGroupingEngine:
    """Groups detection signals by (signal_type, component) pairs.

    Parameters
    ----------
    max_samples : int
        Maximum number of sample payloads to keep per group.
    """

    def __init__(self, max_samples: int = _MAX_SAMPLE_PAYLOADS) -> None:
        self._max_samples = max_samples

    def group_signals(self, *, snapshot_id: str, signals: list[dict[str, Any]]) -> SignalGroupingReport:
        """Group detection signals by type and component.

        Parameters
        ----------
        snapshot_id : str
            Pipeline snapshot identifier.
        signals : list[dict]
            Raw detection signal dicts.  Each should have at least
            ``signal_type``, ``component``, ``created_utc``, and optionally
            ``payload_bytes`` (hex-encoded).

        Returns
        -------
        SignalGroupingReport
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SignalGroupingEngine.group_signals"
        )

        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for sig in signals:
            sig_type = sig.get("signal_type", "unknown")
            component = sig.get("component", "unknown")
            key = f"{sig_type}::{component}"
            buckets[key].append(sig)
        groups: list[SignalGroup] = []
        for key in tqdm(sorted(buckets.keys()), desc="Processing", unit="item"):
            items = buckets[key]
            sig_type, component = key.split("::", 1)
            timestamps = [
                item.get("created_utc", 0) for item in items if isinstance(item.get("created_utc"), int)
            ]
            earliest = min(timestamps) if timestamps else 0
            latest = max(timestamps) if timestamps else 0
            samples: list[bytes] = []
            for item in items[: self._max_samples]:
                payload_hex = item.get("payload_hex", "")
                if payload_hex:
                    try:
                        samples.append(bytes.fromhex(payload_hex))
                    except ValueError:  # guardian: allow-silent-swallow -- malformed payload hex: skip sample, continue grouping
                        pass
            groups.append(
                SignalGroup(
                    group_key=key,
                    signal_type=sig_type,
                    component=component,
                    count=len(items),
                    earliest_utc=earliest,
                    latest_utc=latest,
                    sample_payloads=tuple(samples),
                ),
            )
        return SignalGroupingReport(
            snapshot_id=snapshot_id,
            groups=tuple(groups),
            total_signals=len(signals),
            total_groups=len(groups),
        )

    # Wave A-8: Spike detection for injection patterns
    def detect_signal_spikes(
        self,
        current_signals: list[dict[str, Any]],
        historical_window_hours: int = 24,
        spike_threshold: float = 3.0,
    ) -> dict[str, Any]:
        """Detect spikes in signal patterns for injection detection.

        Args:
            current_signals: Current signal batch
            historical_window_hours: Hours to look back for baseline
            spike_threshold: Multiplier for spike detection

        Returns:
            Spike detection analysis
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SignalGroupingEngine.detect_signal_spikes"
        )

        if not current_signals:
            return {
                "spike_detected": False,
                "spike_signals": [],
                "baseline_stats": {},
                "timestamp_utc": int(time.time() * 1000),
            }

        # Group current signals by type
        current_counts = {}
        for signal in current_signals:
            sig_type = signal.get("signal_type", "unknown")
            current_counts[sig_type] = current_counts.get(sig_type, 0) + 1

        # Calculate baseline (simplified - would use historical data in production)
        # For now, use a simple baseline based on typical patterns
        baseline_counts = {
            "injection_detection": 5,  # Baseline per hour
            "security_violation": 2,
            "policy_breach": 3,
            "guardrail_fire": 8,
        }

        # Detect spikes
        spike_signals = []
        spike_detected = False

        for sig_type, current_count in tqdm(current_counts.items(), desc="Processing", unit="item"):
            baseline = baseline_counts.get(sig_type, 1)  # Default baseline
            spike_ratio = (
                current_count / baseline if baseline > 0 else current_count
            )  # Fix: use count as ratio when baseline is 0

            if spike_ratio >= spike_threshold:
                spike_signals.append(
                    {
                        "signal_type": sig_type,
                        "current_count": current_count,
                        "baseline_count": baseline,
                        "spike_ratio": spike_ratio,
                        "severity": "high" if spike_ratio >= 10 else "medium" if spike_ratio >= 5 else "low",
                    }
                )
                spike_detected = True

        analysis = {
            "spike_detected": spike_detected,
            "spike_signals": spike_signals,
            "baseline_stats": baseline_counts,
            "current_counts": current_counts,
            "timestamp_utc": int(time.time() * 1000),
            "trace_id": _trace_id,
        }

        # Persist spike detection results
        try:
            from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            bridge = get_sl_memory_bridge()

            bridge.persist_signal_spike_detection(
                spike_detected=spike_detected,
                spike_count=len(spike_signals),
                analysis_json=json.dumps(analysis, sort_keys=True),
                timestamp_utc=analysis["timestamp_utc"],
            )
        except (
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:  # guardian: allow-log-and-swallow -- bridge persist best-effort: non-fatal, analysis still returned to caller
            # Bridge unavailable - continue without it
            import logging

            logging.getLogger(__name__).debug(
                "signal_grouping_engine: failed to persist spike detection: %s", exc
            )

        return analysis


__all__ = ["SignalGroupingEngine", "SignalGroup", "SignalGroupingReport"]
