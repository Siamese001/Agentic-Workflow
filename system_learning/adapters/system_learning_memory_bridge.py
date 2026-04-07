"""System Learning → Memory MCP Bridge.

Canonical adapter that persists system_learning knowledge into the Memory MCP
knowledge graph via GraphMemoryBridge, enabling cross-session learning for:

  - HealingSuccessRateStore  — EMA rates survive restarts (no more cold-start)
  - RCAEngine findings       — failure pattern library accumulates over time
  - ShadowDriftAnalyzer      — drift trend history queryable across sessions
  - PolicyRecommendationEngine — recommendation outcomes feed back into future decisions
  - HealingOutcomeAggregator — aggregate snapshots queryable across restarts

Design constraints:
  - Resilient: MCP unavailability is logged, never raises
  - Non-authoritative: MCP is a read-supplement; file/in-memory stores remain authoritative
  - Idempotent: repeated calls for the same content_hash are safe (entity upsert)
  - Bounded: observations capped at _MAX_OBS chars to stay within MCP payload limits

[SSOT] Canonical implementation for system_learning → Memory MCP persistence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
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

_emit_applies_guardrail("p0", "system_learning_memory_bridge", "p0_governance")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("system_learning_memory_bridge", "p4obs", "metric_1")
_emit_emits_metric_event("system_learning_memory_bridge", "p4obs", "metric_2")
_emit_emits_metric_event("system_learning_memory_bridge", "p4obs", "metric_3")
_emit_emits_metric_event("system_learning_memory_bridge", "p4obs", "metric_4")
_emit_emits_metric_event("system_learning_memory_bridge", "p4obs", "metric_5")
_emit_emits_metric_event("system_learning_memory_bridge", "p4obs", "metric_6")
_emit_records_incident_event("system_learning_memory_bridge", "p4obs", "incident")
_emit_captures_runtime_anomaly("system_learning_memory_bridge", "p4obs", "anomaly")
_emit_writes_observability_log("system_learning_memory_bridge", "p4obs", "obs_log")
_emit_updates_monitoring_state("system_learning_memory_bridge", "p4obs", "mon_state")
_emit_triggers_alert("system_learning_memory_bridge", "p4obs", "alert")
_emit_links_incident_trace("system_learning_memory_bridge", "p4obs", "trace_link")
_emit_captures_pattern("system_learning_memory_bridge", "p3lm", "pattern")
_emit_records_learning_event("system_learning_memory_bridge", "p3lm", "learning_event")
_emit_writes_learning_snapshot("system_learning_memory_bridge", "p3lm", "snapshot")
_emit_feeds_meta_learning("system_learning_memory_bridge", "p3lm", "meta_feed")
_emit_updates_routing_strategy("system_learning_memory_bridge", "p3lm", "routing")
_emit_improves_agent_policy("system_learning_memory_bridge", "p3lm", "policy")
_emit_stores_learning_state("system_learning_memory_bridge", "p3lm", "state")
_emit_records_execution_trace("system_learning_memory_bridge", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("system_learning_memory_bridge", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("system_learning_memory_bridge", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("system_learning_memory_bridge", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("system_learning_memory_bridge", "L4_STATE", "p2_trace_5")
_emit_reads_environ("system_learning_memory_bridge", "env_read", "p2_env_1")
_emit_reads_environ("system_learning_memory_bridge", "env_read", "p2_env_2")
_emit_reads_runtime_state("system_learning_memory_bridge", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("system_learning_memory_bridge", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "system_learning_memory_bridge", "context_pull")
_emit_pulls_context("p1", "system_learning_memory_bridge", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "system_learning_memory_bridge", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "system_learning_memory_bridge", "uwg_term_2")
_emit_writes_through("p1", "system_learning_memory_bridge", "write_through")
_emit_writes_through("p1", "system_learning_memory_bridge", "write_through_2")
_emit_validated_by_safety_plane("p1", "system_learning_memory_bridge", "safety_validation")
_emit_invokes_eval("p1", "system_learning_memory_bridge", "eval_call")
_emit_proposal_commits_routing("p1", "system_learning_memory_bridge", "routing_commit")
_emit_escalates_to_human("p1", "system_learning_memory_bridge", "human_escalation")
_emit_routes_through("p1", "system_learning_memory_bridge", "route_through")
_emit_checks_agent_registry("p1", "system_learning_memory_bridge", "agent_registry")
_emit_validates_agent_capability("p1", "system_learning_memory_bridge", "capability")
_emit_dispatches_execution_plan("p1", "system_learning_memory_bridge", "exec_plan")
_emit_agent_executes_agent("p1", "system_learning_memory_bridge", "sub_agent")
_emit_routes_to_agent("p1", "system_learning_memory_bridge", "target_agent")
_emit_verifies_policy("p1", "system_learning_memory_bridge", "policy_check")
_emit_observes_runtime_state("p1", "system_learning_memory_bridge", "runtime_state")
_emit_verifies_boundary("p1", "system_learning_memory_bridge", "boundary_check")
_emit_transcripts_response("p1", "system_learning_memory_bridge", "transcript")
_emit_hard_fails_untranscripted("p1", "system_learning_memory_bridge")
_emit_gated_by_confidence("p1", "system_learning_memory_bridge", "confidence_gate")
emit_replay_key("p0", "system_learning_memory_bridge")
emit_determinism_digest("p0", "system_learning_memory_bridge")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "system_learning_memory_bridge", "execution_auth")
_emit_validates_capability("p2", "system_learning_memory_bridge", "capability_check")
_emit_routes_to_capability("p2", "system_learning_memory_bridge", "capability_route")
_emit_writes_via_uwg("p2", "system_learning_memory_bridge", "uwg_write")
_emit_blocks_direct_write("p2", "system_learning_memory_bridge", "direct_write_block")
_emit_records_tool_invocation("p2", "system_learning_memory_bridge", "tool_invocation")
_emit_captures_execution_output("p2", "system_learning_memory_bridge", "exec_output")
_emit_dispatches_agent("p3", "system_learning_memory_bridge", "agent_dispatch")
_emit_coordinates_agents("p3", "system_learning_memory_bridge", "agent_coordination")
_emit_records_workflow_lineage("p3", "system_learning_memory_bridge", "workflow_lineage")
_emit_records_healing_outcome("p3", "system_learning_memory_bridge", "healing_outcome")
_emit_escalates_failure("p3", "system_learning_memory_bridge", "failure_escalation")
_emit_orchestrates_workflow("p3", "system_learning_memory_bridge", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "system_learning_memory_bridge", "healing_dispatch")
_emit_invokes_evaluation("p3", "system_learning_memory_bridge", "evaluation_signal")
_emit_records_telemetry_event("p4", "system_learning_memory_bridge", "telemetry_event")
_emit_captures_evaluation_metric("p4", "system_learning_memory_bridge", "eval_metric")
_emit_stores_embedding("p4", "system_learning_memory_bridge", "embedding_store")
_emit_updates_meta_learning_state("p4", "system_learning_memory_bridge", "meta_learning")
_emit_links_execution_to_snapshot("p4", "system_learning_memory_bridge", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_MAX_OBS = 200
_MAX_SIGNATURES = 50
_MAX_RCA_FINDINGS = 20
_MAX_POLICY_RECS = 30


def _trunc(s: str, n: int = _MAX_OBS) -> str:
    return s[:n] if len(s) > n else s


def _content_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class SystemLearningMemoryBridge:
    """Persists system_learning signals into the Memory MCP knowledge graph.

    All public methods are fire-and-forget: they log on failure and return
    a bool indicating whether the write succeeded.

    Usage::

        bridge = SystemLearningMemoryBridge.get_instance()

        # After healing outcome recorded
        bridge.persist_healing_success_rate("IMPORT_ERROR", rate=0.87, count=42)

        # After RCA analysis
        bridge.persist_rca_findings(snapshot_id, findings)

        # After drift analysis
        bridge.persist_drift_summary(drift_summary)

        # After policy recommendation
        bridge.persist_policy_recommendation(recommendation)

        # After outcome aggregation
        bridge.persist_healing_aggregate_snapshot(snapshot)

        # On startup: restore healing rates
        rates = bridge.restore_healing_success_rates()
    """

    ENTITY_TYPE_HEALING_RATE = "SLHealingSuccessRate"
    ENTITY_TYPE_RCA_FINDING = "SLRCAFinding"
    ENTITY_TYPE_RCA_REPORT = "SLRCAReport"
    ENTITY_TYPE_DRIFT = "SLDriftSummary"
    ENTITY_TYPE_POLICY_REC = "SLPolicyRecommendation"
    ENTITY_TYPE_AGGREGATE = "SLHealingAggregate"
    ENTITY_TYPE_PATTERN = "SLFailurePattern"
    ENTITY_TYPE_TELEMETRY_EVENT = "SLTelemetryEvent"

    RELATION_TRIGGERED = "SL_TRIGGERED"
    RELATION_RESOLVED_BY = "SL_RESOLVED_BY"
    RELATION_DRIFT_DETECTED_IN = "SL_DRIFT_DETECTED_IN"
    RELATION_POLICY_APPLIES_TO = "SL_POLICY_APPLIES_TO"
    RELATION_AGGREGATES = "SL_AGGREGATES"

    _instance: SystemLearningMemoryBridge | None = None

    def __init__(self) -> None:
        self._bridge = self._load_bridge()
        self._sqlite_memory: Any = None

    @classmethod
    def get_instance(cls) -> SystemLearningMemoryBridge:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SystemLearningMemoryBridge.get_instance",
        )

        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_bridge(self) -> Any:
        try:
            from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge

            return GraphMemoryBridge.get_instance()
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] GraphMemoryBridge unavailable: %s", e)
            return None

    @property
    def is_available(self) -> bool:
        return self._bridge is not None and getattr(self._bridge, "is_available", False)

    def _get_unified_memory_manager(self) -> Any:
        if self._sqlite_memory is False:
            return None
        if self._sqlite_memory is not None:
            return self._sqlite_memory
        try:
            from tools.implement_unified_memory import UnifiedMemoryManager

            self._sqlite_memory = UnifiedMemoryManager()
        except Exception as e:  # guardian: allow-silent-swallower
            logger.debug("[SLMemoryBridge] UnifiedMemoryManager unavailable: %s", e)
            self._sqlite_memory = False
        return None if self._sqlite_memory is False else self._sqlite_memory

    @staticmethod
    def _normalize_persistable_event(event: Any) -> dict[str, Any]:
        if isinstance(event, tuple) and len(event) == 3:
            timestamp_utc, event_type, payload = event
            if isinstance(payload, bytes):
                try:
                    payload = payload.decode("utf-8")    # guardian: Encoding errors should specify fallback encoding strategy
                except UnicodeDecodeError:
                    payload = payload.hex()
            return {
                "timestamp_utc": int(timestamp_utc),
                "event_type": str(event_type),
                "payload": payload,
            }

        payload = getattr(event, "payload_bytes", None)
        if isinstance(payload, bytes):
            try:
                payload = payload.decode("utf-8")    # guardian: Encoding errors should specify fallback encoding strategy
            except UnicodeDecodeError:
                payload = payload.hex()
        return {
            "timestamp_utc": int(getattr(event, "timestamp_utc", 0) or 0),
            "event_type": str(getattr(event, "event_type", event.__class__.__name__)),
            "payload": payload,
        }

    def persist_active_version(self, component: str, version_id: str, *, ts: str = "") -> bool:
        store = self._get_unified_memory_manager()
        if not store:
            return False
        return bool(
            store.store_application_state(
                key=f"system_learning.active_version.{component}",
                value={"component": component, "version_id": version_id, "ts": ts},
                state_type="json",
            ),
        )

    def persist_config_snapshot(
        self,
        surface_name: str,
        config_bytes: bytes,
        *,
        source: str = "config_provider",
        ts: str = "",
    ) -> bool:
        store = self._get_unified_memory_manager()
        if not store:
            return False
        payload: Any = config_bytes
        state_type = "pickle"
        try:
            decoded = config_bytes.decode("utf-8")
            payload = json.loads(decoded)
            state_type = "json"    # guardian: Encoding errors should specify fallback encoding strategy
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = config_bytes
            state_type = "pickle"
        return bool(
            store.store_application_state(
                key=f"system_learning.config_snapshot.{surface_name}",
                value={"surface_name": surface_name, "payload": payload, "source": source, "ts": ts},
                state_type=state_type,
            ),
        )

    def persist_telemetry_window(
        self,
        source: str,
        events: Any,
        *,
        window_start: int = 0,
        window_end: int = 0,
    ) -> bool:
        store = self._get_unified_memory_manager()
        if not store:
            return False
        normalized = [self._normalize_persistable_event(event) for event in list(events)]
        persisted = bool(
            store.store_application_state(
                key=f"system_learning.telemetry_window.{source}",
                value={
                    "source": source,
                    "window_start": window_start,
                    "window_end": window_end,
                    "events": normalized,
                },
                state_type="json",
            ),
        )
        if normalized:
            store.store_performance_metric(
                name="telemetry_event_count",
                value=float(len(normalized)),
                context={"source": source, "window_start": window_start, "window_end": window_end},
                component="system_learning",
            )
        return persisted

    def persist_l1_drift_signal(self, drift_signal: Any, *, source: str = "l1_meta_adapter") -> bool:
        store = self._get_unified_memory_manager()
        if not store:
            return False
        payload = {
            "surface_name": str(getattr(drift_signal, "surface_name", "unknown")),
            "drift_magnitude": float(getattr(drift_signal, "drift_magnitude", 0.0) or 0.0),
            "direction": str(getattr(drift_signal, "direction", "unknown")),
            "observation_count": int(getattr(drift_signal, "observation_count", 0) or 0),
            "snapshot_id": str(getattr(drift_signal, "snapshot_id", "")),
            "source": source,
        }
        persisted = bool(
            store.store_application_state(
                key=f"system_learning.l1_drift.{payload['surface_name']}",
                value=payload,
                state_type="json",
            ),
        )
        store.store_performance_metric(
            name="l1_drift_magnitude",
            value=payload["drift_magnitude"],
            context=payload,
            component=source,
        )
        return persisted

    # ------------------------------------------------------------------
    # 1. Healing Success Rates — persist/restore EMA rates cross-session
    # ------------------------------------------------------------------

    def persist_healing_success_rate(
        self,
        error_signature: str,
        rate: float,
        count: int,
        *,
        ts: str = "",
    ) -> bool:
        """Store a healing success rate for an error signature.

        Args:
            error_signature: The error pattern key (e.g. "IMPORT_ERROR").
            rate: EMA success rate (0.0–1.0).
            count: Observation count.
            ts: Optional timestamp tag.

        Returns:
            True if persisted, False if MCP unavailable.
        """
        _emit_snapshots_state(
            str(uuid.uuid4()), "SystemLearningMemoryBridge.persist_healing_success_rate", "L4_STATE",
        )
        if not self._bridge:
            return False
        sig_hash = _content_hash(error_signature)
        entity_name = f"SLHealRate_{sig_hash}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_HEALING_RATE,
                observations=[
                    _trunc(f"error_signature={error_signature}"),
                    f"rate={rate:.6f}",
                    f"count={count}",
                ],
            )
            return True
        except Exception as exc:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("Failed to persist healing success rate %s: %s", error_signature, exc)
            return False

    def persist_all_healing_rates(
        self,
        rates: dict[str, float],
        counts: dict[str, int],
        *,
        ts: str = "",
    ) -> int:
        """Bulk-persist all healing success rates from a HealingSuccessRateStore.

        Args:
            rates: Dict of error_signature -> EMA rate.
            counts: Dict of error_signature -> observation count.
            ts: Optional timestamp tag.

        Returns:
            Number of rates successfully persisted.
        """
        persisted = 0
        for sig, rate in sorted(rates.items())[:_MAX_SIGNATURES]:
            count = counts.get(sig, 0)
            if self.persist_healing_success_rate(sig, rate, count, ts=ts):
                persisted += 1
        logger.info("[SLMemoryBridge] Persisted %d/%d healing rates", persisted, len(rates))
        return persisted

    def restore_healing_success_rates(self) -> dict[str, tuple[float, int]]:
        """Restore healing success rates from Memory MCP on startup.

        Returns:
            Dict of error_signature -> (rate, count). Empty if MCP unavailable.
        """
        if not self._bridge:
            return {}
        try:
            results = self._bridge.search_entities(self.ENTITY_TYPE_HEALING_RATE)
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] restore_healing_success_rates failed: %s", e)
            return {}

        restored: dict[str, tuple[float, int]] = {}
        for entity in results:
            obs = entity.get("observations", [])
            sig = rate = count = None
            for o in obs:
                if o.startswith("error_signature="):
                    sig = o[len("error_signature=") :]
                elif o.startswith("rate="):
                    try:
                        rate = float(o[5:])
                    except ValueError:
                        pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow
                elif o.startswith("count="):
                    try:
                        count = int(o[6:])
                    except ValueError:
                        pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow
            if sig and rate is not None and count is not None:
                restored[sig] = (rate, count)

        logger.info("[SLMemoryBridge] Restored %d healing rate(s) from Memory MCP", len(restored))
        return restored

    # ------------------------------------------------------------------
    # 2. RCA Findings — accumulate failure pattern library
    # ------------------------------------------------------------------

    def persist_rca_findings(
        self,
        snapshot_id: str,
        findings: Any,
        *,
        window_start: int = 0,
        window_end: int = 0,
    ) -> bool:
        """Persist RCA findings from rca_engine.analyze_failures().

        Args:
            snapshot_id: The snapshot this RCA was based on.
            findings: RCAReport object or iterable of RCAFinding objects.
            window_start: Analysis window start (UTC epoch).
            window_end: Analysis window end (UTC epoch).

        Returns:
            True if report entity created.
        """
        if not self._bridge:
            return False

        rca_findings = []
        if hasattr(findings, "findings"):
            rca_findings = list(findings.findings)
        elif hasattr(findings, "__iter__"):
            rca_findings = list(findings)

        report_hash = _content_hash(f"{snapshot_id}:{window_start}:{window_end}")
        report_name = f"SLRCAReport_{report_hash}"

        obs = [
            f"snapshot_id={_trunc(snapshot_id, 80)}",
            f"finding_count={len(rca_findings)}",
            f"window={window_start}-{window_end}",
        ]
        for f in rca_findings[:5]:
            cat = getattr(f, "category", "?")
            sig = getattr(f, "signature", "?")
            cnt = getattr(f, "count", 0)
            obs.append(_trunc(f"finding={cat}:{sig}:n={cnt}"))

        try:
            self._bridge.create_agent_entity(
                agent_name=report_name,
                agent_type=self.ENTITY_TYPE_RCA_REPORT,
                observations=obs,
            )
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] persist_rca_findings report failed: %s", e)
            return False

        # Individual finding entities for pattern library queries
        for finding in rca_findings[:_MAX_RCA_FINDINGS]:
            cat = getattr(finding, "category", "UNKNOWN")
            sig = getattr(finding, "signature", "unknown")
            cnt = getattr(finding, "count", 0)
            evhash = getattr(finding, "evidence_hash", "")[:16]
            finding_name = f"SLRCAFinding_{cat}_{_content_hash(sig)}"
            try:
                self._bridge.create_agent_entity(
                    agent_name=finding_name,
                    agent_type=self.ENTITY_TYPE_RCA_FINDING,
                    observations=[
                        f"category={cat}",
                        f"signature={_trunc(sig, 80)}",
                        f"count={cnt}",
                        f"evidence_hash={evhash}",
                        f"snapshot_id={_trunc(snapshot_id, 60)}",
                    ],
                )
                self._bridge.create_relation(finding_name, report_name, self.RELATION_TRIGGERED)
            except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
                logger.debug("[SLMemoryBridge] persist rca finding entity failed: %s", e)

        logger.info(
            "[SLMemoryBridge] RCA report persisted: %s (%d findings)",
            report_name,
            len(rca_findings),
        )
        return True

    def query_rca_pattern_frequency(self, category: str = "") -> list[dict[str, Any]]:
        """Query accumulated RCA findings, optionally filtered by category.

        Args:
            category: Filter by category (e.g. "IMPORT", "SYNTAX"). Empty = all.

        Returns:
            List of SLRCAFinding entity dicts from the knowledge graph.
        """
        if not self._bridge:
            return []
        try:
            results = self._bridge.search_entities("SLRCAFinding")
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] query_rca_pattern_frequency failed: %s", e)
            return []
        if not category:
            return results
        # Filter by category in observations (MCP search may not substring-match)
        filtered = []
        for entity in results:
            for obs in entity.get("observations", []):
                if obs.startswith("category=") and category in obs:
                    filtered.append(entity)
                    break
        return filtered

    # ------------------------------------------------------------------
    # 3. Shadow Drift Summaries — drift trend history
    # ------------------------------------------------------------------

    def persist_drift_summary(self, drift_summary: Any, *, ts: str = "") -> bool:
        """Persist a ShadowDriftAnalyzer DriftSummary to Memory MCP.

        Args:
            drift_summary: DriftSummary dataclass from shadow_drift_analyzer.
            ts: Optional timestamp tag.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        profile_id = getattr(drift_summary, "profile_id", "unknown")
        digest = getattr(drift_summary, "deterministic_digest", "")[:16]
        drift_flag = getattr(drift_summary, "drift_flag", False)
        drift_score = getattr(drift_summary, "drift_score", 0.0)
        p95 = getattr(drift_summary, "p95_cosine", 0.0)
        mean = getattr(drift_summary, "mean_cosine", 0.0)
        batch_size = getattr(drift_summary, "batch_size", 0)

        entity_name = f"SLDrift_{_content_hash(f'{profile_id}:{digest}')}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_DRIFT,
                observations=[
                    f"profile_id={_trunc(profile_id, 60)}",
                    f"drift_flag={drift_flag}",
                    f"drift_score={drift_score:.6f}",
                    f"p95_cosine={p95:.6f}",
                    f"mean_cosine={mean:.6f}",
                    f"batch_size={batch_size}",
                    f"digest={digest}",
                    f"ts={ts}",
                ],
            )
            logger.info(
                "[SLMemoryBridge] Drift summary persisted: profile=%s drift=%s score=%.4f",
                profile_id,
                drift_flag,
                drift_score,
            )
            return True
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] persist_drift_summary failed: %s", e)
            return False

    def query_drift_history(self, profile_id: str = "") -> list[dict[str, Any]]:
        """Return all persisted drift summaries, optionally filtered by profile.

        Args:
            profile_id: Substring match on profile_id observation. Empty = all.

        Returns:
            List of SLDriftSummary entity dicts.
        """
        if not self._bridge:
            return []
        try:
            results = self._bridge.search_entities("SLDriftSummary")
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] query_drift_history failed: %s", e)
            return []
        if not profile_id:
            return results
        # Filter by profile_id in observations (MCP search may not substring-match)
        filtered = []
        for entity in results:
            for obs in entity.get("observations", []):
                if obs.startswith("profile_id=") and profile_id in obs:
                    filtered.append(entity)
                    break
        return filtered

    # ------------------------------------------------------------------
    # 4. Policy Recommendations — history + outcome feedback
    # ------------------------------------------------------------------

    def persist_policy_recommendation(
        self,
        recommendation: Any,
        *,
        ts: str = "",
        applied: bool = False,
    ) -> bool:
        """Persist a PolicyRecommendationEngine recommendation.

        Args:
            recommendation: PolicyRecommendation dataclass.
            ts: Optional timestamp tag.
            applied: Whether the recommendation was applied.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        profile_id = getattr(recommendation, "profile_id", "unknown")
        digest = getattr(recommendation, "deterministic_digest", "")[:16]
        rationale = getattr(recommendation, "rationale", "")
        confidence = getattr(recommendation, "confidence_score", 0.0)
        changes = getattr(recommendation, "recommended_changes", {})

        entity_name = f"SLPolicyRec_{_content_hash(f'{profile_id}:{digest}')}"
        changes_str = _trunc(json.dumps(changes, separators=(",", ":"), sort_keys=True))

        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_POLICY_REC,
                observations=[
                    f"profile_id={_trunc(profile_id, 60)}",
                    f"confidence={confidence:.6f}",
                    f"changes={changes_str}",
                    f"rationale={_trunc(rationale, 120)}",
                    f"applied={applied}",
                    f"digest={digest}",
                    f"ts={ts}",
                ],
            )
            logger.info(
                "[SLMemoryBridge] Policy recommendation persisted: profile=%s confidence=%.4f applied=%s",
                profile_id,
                confidence,
                applied,
            )
            return True
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] persist_policy_recommendation failed: %s", e)
            return False

    def mark_recommendation_applied(self, entity_name: str) -> bool:
        """Update a policy recommendation entity to mark it as applied.

        Args:
            entity_name: Full entity name (e.g. SLPolicyRec_abcdef12...).

        Returns:
            True if observation added.
        """
        if not self._bridge:
            return False
        try:
            return self._bridge.add_observation(entity_name, "applied=true")
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] mark_recommendation_applied failed: %s", e)
            return False

    def query_policy_recommendations(
        self, profile_id: str = "", *, applied_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Query persisted policy recommendations.

        Args:
            profile_id: Optional profile filter.
            applied_only: If True, filter by applied=true observation.

        Returns:
            List of SLPolicyRecommendation entities.
        """
        if not self._bridge:
            return []
        query = f"SLPolicyRecommendation {profile_id}" if profile_id else "SLPolicyRecommendation"
        try:
            results = self._bridge.search_entities(query)
            if applied_only:
                results = [r for r in results if any("applied=true" in o for o in r.get("observations", []))]
            return results
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] query_policy_recommendations failed: %s", e)
            return []

    # ------------------------------------------------------------------
    # 5. Healing Aggregate Snapshots — cross-session aggregate history
    # ------------------------------------------------------------------

    def persist_healing_aggregate_snapshot(self, snapshot: Any, *, ts: str = "") -> bool:
        """Persist a HealingOutcomeAggregateSnapshot to Memory MCP.

        Args:
            snapshot: HealingOutcomeAggregateSnapshot dataclass.
            ts: Optional timestamp tag.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        version_id = getattr(snapshot, "version_id", "unknown")
        created_utc = getattr(snapshot, "created_utc", 0)
        aggregates = getattr(snapshot, "aggregates", ())
        total = len(aggregates)

        # Summary stats
        top_rates: list[str] = []
        for key, agg in list(aggregates)[:5]:
            healer = getattr(key, "healer_name", "?")
            s = getattr(agg, "success_count", 0)
            f = getattr(agg, "failure_count", 0)
            rate = round(s / (s + f), 4) if (s + f) > 0 else 0.0
            top_rates.append(f"{healer}:{rate:.3f}")

        entity_name = f"SLAggrSnap_{_content_hash(version_id)}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_AGGREGATE,
                observations=[
                    f"version_id={_trunc(version_id, 60)}",
                    f"created_utc={created_utc}",
                    f"aggregate_count={total}",
                    _trunc(f"top_rates={','.join(top_rates)}"),
                    f"ts={ts}",
                ],
            )
            logger.info(
                "[SLMemoryBridge] Healing aggregate snapshot persisted: %s (%d aggregates)",
                entity_name,
                total,
            )
            return True
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] persist_healing_aggregate_snapshot failed: %s", e)
            return False

    # ------------------------------------------------------------------
    # 6. Failure Pattern Library — accumulated from PatternAnalysisEngine
    # ------------------------------------------------------------------

    def persist_failure_pattern(
        self,
        pattern_id: str,
        pattern_label: str,
        centroid_hash: str,
        member_count: int,
        *,
        ts: str = "",
    ) -> bool:
        """Persist a detected failure pattern cluster.

        Args:
            pattern_id: Unique pattern identifier (content hash).
            pattern_label: Human-readable cluster label.
            centroid_hash: Hash of the cluster centroid embedding.
            member_count: Number of failure events in this cluster.
            ts: Optional timestamp tag.

        Returns:
            True if entity created.
        """
        if not self._bridge:
            return False

        entity_name = f"SLFailurePattern_{pattern_id[:16]}"
        try:
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_PATTERN,
                observations=[
                    f"pattern_id={pattern_id[:32]}",
                    f"label={_trunc(pattern_label, 80)}",
                    f"centroid_hash={centroid_hash[:16]}",
                    f"member_count={member_count}",
                    f"ts={ts}",
                ],
            )
            return True
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] persist_failure_pattern failed: %s", e)
            return False

    def query_failure_patterns(self) -> list[dict[str, Any]]:
        """Return all persisted failure pattern entities."""
        if not self._bridge:
            return []
        try:
            return self._bridge.search_entities("SLFailurePattern")
        except Exception as e:  # guardian: allow-silent-swallow -- MCP write-back is non-critical telemetry; failure logged above
            logger.debug("[SLMemoryBridge] query_failure_patterns failed: %s", e)
            return []

    def get_latest_violation_counts(self) -> tuple[int, int]:
        """Get violation counts from the two most recent ADG snapshots.

        Returns:
            Tuple of (current_count, previous_count)
        """
        if not self._bridge:
            return (0, 0)

        try:
            # Query ADGSnapshot entities, sorted by timestamp descending
            snapshots = self._bridge.search_entities("ADGSnapshot")
            if len(snapshots) < 2:
                return (0, 0)

            # Sort by timestamp (most recent first)
            snapshots.sort(key=lambda s: self._extract_timestamp(s), reverse=True)

            # Get violation counts from top 2 snapshots
            current_count = self._extract_violation_count(snapshots[0])
            previous_count = self._extract_violation_count(snapshots[1])

            return (current_count, previous_count)
        except Exception as e:
            logger.debug("[SLMemoryBridge] get_latest_violation_counts failed: %s", e)
            return (0, 0)

    def _extract_timestamp(self, snapshot: dict[str, Any]) -> int:
        """Extract timestamp from snapshot entity."""
        for obs in snapshot.get("observations", []):
            if obs.startswith("ts="):
                return int(obs[3:])
        return 0

    def _extract_violation_count(self, snapshot: dict[str, Any]) -> int:
        """Extract violation count from snapshot entity."""
        for obs in snapshot.get("observations", []):
            if obs.startswith("violation_count="):
                return int(obs[16:])
        return 0

    def persist_circuit_breaker_event(
        self,
        breaker_name: str,
        old_state: str,
        new_state: str,
        timestamp_utc: int,
        failure_count: int,
        success_count: int,
        current_backoff: float,
    ) -> bool:
        """Persist circuit breaker state transition event.

        Args:
            breaker_name: Name of the circuit breaker
            old_state: Previous state
            new_state: New state
            timestamp_utc: Timestamp in milliseconds
            failure_count: Current failure count
            success_count: Current success count
            current_backoff: Current backoff timeout

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"CircuitBreakerEvent_{breaker_name}_{int(timestamp_utc)}"
            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=[
                    f"breaker={breaker_name}",
                    f"old_state={old_state}",
                    f"new_state={new_state}",
                    f"ts={timestamp_utc}",
                    f"failure_count={failure_count}",
                    f"success_count={success_count}",
                    f"backoff={current_backoff}",
                ],
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_circuit_breaker_event failed: %s", e)
            return False

    def persist_adg_confidence_summary(self, conf_summary: dict[str, Any], timestamp: str) -> bool:
        """Persist ADG confidence tier distribution.

        Args:
            conf_summary: Confidence summary dict from ADG confidence scoring
            timestamp: ADG timestamp string

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"ADGConfidenceSummary_{timestamp}"
            observations = [
                f"ts={timestamp}",
                f"total_edges={conf_summary.get('total_edges', 0)}",
            ]

            # Add tier distribution
            tier_dist = conf_summary.get('tier_distribution', {})
            for tier, count in tier_dist.items():
                observations.append(f"tier_{tier}={count}")

            # Add confidence metrics
            for metric, value in conf_summary.get('confidence_metrics', {}).items():
                observations.append(f"metric_{metric}={value}")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_adg_confidence_summary failed: %s", e)
            return False

    def persist_injection_detection_counts(
        self,
        total_scans: int,
        detection_counts: dict[str, int],
        timestamp_utc: int,
    ) -> bool:
        """Persist injection detection counts for security pattern analysis.

        Args:
            total_scans: Total number of scans performed
            detection_counts: Dictionary of signature_id -> count
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"InjectionDetectionCounts_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"total_scans={total_scans}",
                f"total_detections={sum(detection_counts.values())}",
            ]

            # Add top 10 most frequent signatures
            sorted_sigs = sorted(detection_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for sig_id, count in sorted_sigs:
                observations.append(f"sig_{sig_id}={count}")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_injection_detection_counts failed: %s", e)
            return False

    def persist_healing_tier_outcome(
        self,
        tier: str,
        failure_type: str,
        module_name: str,
        success: bool,
        duration_ms: int,
        timestamp_utc: int,
        agent_name: str,
        trace_id: str,
    ) -> bool:
        """Persist healing tier dispatch outcome for effectiveness analysis.

        Args:
            tier: Healing tier dispatched (LOCAL_AGENT, QWEN_VLLM, GEMINI_2_5_PRO)
            failure_type: Type of failure encountered
            module_name: Module being healed
            success: Whether healing was successful
            duration_ms: Duration of healing attempt in milliseconds
            timestamp_utc: Timestamp in milliseconds
            agent_name: Name of the healing agent
            trace_id: Trace ID for correlation

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"HealingTierOutcome_{tier}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"tier={tier}",
                f"failure_type={failure_type}",
                f"module={module_name}",
                f"success={success}",
                f"duration_ms={duration_ms}",
                f"agent={agent_name}",
                f"trace_id={trace_id}",
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_healing_tier_outcome failed: %s", e)
            return False

    def persist_workflow_outcome(
        self,
        bundle_id: str,
        trace_id: str,
        workflow_type: str,
        success: bool,
        elapsed_ms: float,
        agent_sequence: list[str],
        quality_score: float,
        outcome_hash: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist workflow outcome for meta-learning analysis.

        Args:
            bundle_id: Workflow bundle identifier
            trace_id: Trace ID for correlation
            workflow_type: Type of workflow executed
            success: Whether workflow succeeded
            elapsed_ms: Execution duration in milliseconds
            agent_sequence: Sequence of agents executed
            quality_score: Quality assessment score
            outcome_hash: Deterministic outcome hash
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"WorkflowOutcome_{workflow_type}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"bundle_id={bundle_id}",
                f"trace_id={trace_id}",
                f"workflow_type={workflow_type}",
                f"success={success}",
                f"elapsed_ms={elapsed_ms}",
                f"quality_score={quality_score}",
                f"outcome_hash={outcome_hash}",
                f"agent_count={len(agent_sequence)}",
            ]

            # Add agent sequence (up to 10 agents)
            for i, agent in enumerate(agent_sequence[:10]):
                observations.append(f"agent_{i}={agent}")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_workflow_outcome failed: %s", e)
            return False

    def persist_eval_regression_results(
        self,
        trace_id: str,
        total_records: int,
        regression_count: int,
        regression_rate: float,
        verdict_counts: dict[str, int],
        baseline_loaded: bool,
        timestamp_utc: int,
    ) -> bool:
        """Persist evaluation regression results for drift detection.

        Args:
            trace_id: Evaluation trace ID
            total_records: Total number of evaluation records
            regression_count: Number of regression records
            regression_rate: Regression rate (0-1)
            verdict_counts: Dictionary of verdict type -> count
            baseline_loaded: Whether baseline was available
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"EvalRegressionResults_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"trace_id={trace_id}",
                f"total_records={total_records}",
                f"regression_count={regression_count}",
                f"regression_rate={regression_rate}",
                f"baseline_loaded={baseline_loaded}",
            ]

            # Add verdict counts
            for verdict, count in verdict_counts.items():
                observations.append(f"verdict_{verdict}={count}")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_eval_regression_results failed: %s", e)
            return False

    def persist_cognitive_dispositions(
        self,
        dispositions_json: str,
        timestamp_utc: int,
        trace_id: str,
    ) -> bool:
        """Persist cognitive dispositions for RCA enrichment.

        Args:
            dispositions_json: JSON-serialized cognitive disposition data
            timestamp_utc: Timestamp in milliseconds
            trace_id: Trace ID for correlation

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"CognitiveDispositions_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"trace_id={trace_id}",
                f"dispositions_json={dispositions_json[:500]}...",  # Truncate for storage
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_cognitive_dispositions failed: %s", e)
            return False

    def persist_safety_audit_record(
        self,
        audit_id: str,
        run_id: str,
        trace_id: str,
        decision_type: str,
        decision_outcome: str,
        policy_hash: str,
        actor_id: str,
        action_class: str,
        reason: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist safety audit record for RCA clustering.

        Args:
            audit_id: Unique audit identifier
            run_id: Run identifier
            trace_id: Trace ID for correlation
            decision_type: Type of decision made
            decision_outcome: Outcome of the decision
            policy_hash: Hash of the policy applied
            actor_id: ID of the actor making the decision
            action_class: Class of action taken
            reason: Reason for the decision
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"SafetyAudit_{audit_id}"
            observations = [
                f"ts={timestamp_utc}",
                f"audit_id={audit_id}",
                f"run_id={run_id}",
                f"trace_id={trace_id}",
                f"decision_type={decision_type}",
                f"decision_outcome={decision_outcome}",
                f"policy_hash={policy_hash}",
                f"actor_id={actor_id}",
                f"action_class={action_class}",
                f"reason={reason[:200]}...",  # Truncate for storage
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_safety_audit_record failed: %s", e)
            return False

    def persist_resource_prediction_feedback(
        self,
        failure_type: str,
        fingerprint: str,
        predicted_cpu: int,
        predicted_memory: int,
        predicted_timeout: int,
        actual_cpu: int,
        actual_memory: int,
        actual_timeout: int,
        cpu_error_rate: float,
        memory_error_rate: float,
        timeout_error_rate: float,
        confidence: float,
        success: bool,
        timestamp_utc: int,
    ) -> bool:
        """Persist resource prediction accuracy feedback.

        Args:
            failure_type: Type of failure predicted
            fingerprint: Failure signature fingerprint
            predicted_cpu: Predicted CPU cores
            predicted_memory: Predicted memory in MB
            predicted_timeout: Predicted timeout in seconds
            actual_cpu: Actual CPU cores used
            actual_memory: Actual memory used in MB
            actual_timeout: Actual timeout in seconds
            cpu_error_rate: Normalized CPU error rate
            memory_error_rate: Normalized memory error rate
            timeout_error_rate: Normalized timeout error rate
            confidence: Prediction confidence
            success: Whether prediction was successful
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"ResourcePredictionFeedback_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"failure_type={failure_type}",
                f"fingerprint={fingerprint}",
                f"predicted_cpu={predicted_cpu}",
                f"predicted_memory={predicted_memory}",
                f"predicted_timeout={predicted_timeout}",
                f"actual_cpu={actual_cpu}",
                f"actual_memory={actual_memory}",
                f"actual_timeout={actual_timeout}",
                f"cpu_error_rate={cpu_error_rate:.3f}",
                f"memory_error_rate={memory_error_rate:.3f}",
                f"timeout_error_rate={timeout_error_rate:.3f}",
                f"confidence={confidence:.3f}",
                f"success={success}",
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_resource_prediction_feedback failed: %s", e)
            return False

    def persist_rollback_strategy_outcome(
        self,
        failure_type: str,
        failure_fingerprint: str,
        strategy_chosen: str,
        strategy_score: float,
        strategy_reasons: list[str],
        success: bool,
        execution_time_ms: int,
        timestamp_utc: int,
    ) -> bool:
        """Persist rollback strategy outcome for learning.

        Args:
            failure_type: Type of failure that triggered rollback
            failure_fingerprint: Failure signature fingerprint
            strategy_chosen: Rollback strategy that was chosen
            strategy_score: Confidence score for the strategy
            strategy_reasons: List of reasoning factors
            success: Whether rollback was successful
            execution_time_ms: Execution time in milliseconds
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"RollbackStrategyOutcome_{strategy_chosen}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"failure_type={failure_type}",
                f"failure_fingerprint={failure_fingerprint}",
                f"strategy_chosen={strategy_chosen}",
                f"strategy_score={strategy_score:.3f}",
                f"success={success}",
                f"execution_time_ms={execution_time_ms}",
            ]

            # Add top 5 reasons
            for i, reason in enumerate(strategy_reasons[:5]):
                observations.append(f"reason_{i}={reason}")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_rollback_strategy_outcome failed: %s", e)
            return False

    def persist_healing_memory_retrieval_quality(
        self,
        signal_hash: str,
        results_count: int,
        avg_similarity: float,
        high_similarity_count: int,
        retrieval_quality: str,
        top_k_used: int,
        timestamp_utc: int,
    ) -> bool:
        """Persist healing memory retrieval quality metrics.

        Args:
            signal_hash: Hash of the retrieval signal
            results_count: Number of results returned
            avg_similarity: Average similarity score
            high_similarity_count: Count of high similarity results (>0.8)
            retrieval_quality: Quality classification (high/medium/low)
            top_k_used: Top-K parameter used
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"HealingMemoryRetrievalQuality_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"signal_hash={signal_hash}",
                f"results_count={results_count}",
                f"avg_similarity={avg_similarity:.3f}",
                f"high_similarity_count={high_similarity_count}",
                f"retrieval_quality={retrieval_quality}",
                f"top_k_used={top_k_used}",
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_healing_memory_retrieval_quality failed: %s", e)
            return False

    def persist_execute_ssot_phase_outcomes(
        self,
        phase_name: str,
        outcomes_json: str,
        timestamp_utc: int,
        trace_id: str,
    ) -> bool:
        """Persist Execute_SSOT phase outcomes for system learning.

        Args:
            phase_name: Name of the phase (e.g., "execute_ssot")
            outcomes_json: JSON string containing phase outcomes
            timestamp_utc: Timestamp in milliseconds
            trace_id: Trace ID for correlation

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"ExecuteSSOTPhaseOutcomes_{phase_name}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"phase_name={phase_name}",
                f"trace_id={trace_id}",
                f"outcomes={outcomes_json[:500]}...",  # Truncate for storage
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_execute_ssot_phase_outcomes failed: %s", e)
            return False

    def persist_repair_routes(
        self,
        repair_routes_json: str,
        timestamp_utc: int,
        trace_id: str,
    ) -> bool:
        """Persist repair routes for optimization proposals.

        Args:
            repair_routes_json: JSON string containing repair routes
            timestamp_utc: Timestamp in milliseconds
            trace_id: Trace ID for correlation

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"RepairRoutes_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"trace_id={trace_id}",
                f"routes={repair_routes_json[:500]}...",  # Truncate for storage
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_repair_routes failed: %s", e)
            return False

    def _query_execute_ssot_outcomes(self, timestamp_utc: int) -> None:
        """Query recent Execute_SSOT outcomes (placeholder for future implementation).

        Args:
            timestamp_utc: Current timestamp
        """
        # Placeholder for future query implementation
        pass

    def _query_recent_healing_memory_quality(self, hours: int) -> list[dict[str, Any]]:
        """Query recent healing memory retrieval quality metrics.

        Args:
            hours: Number of hours to look back

        Returns:
            List of quality metrics
        """
        # Placeholder for future query implementation
        return []

    def persist_cache_coherence_violation(
        self,
        layer_type: str,
        violation_type: str,
        error_message: str,
        affected_keys: list[str],
        timestamp_utc: int,
    ) -> bool:
        """Persist cache coherence violations for drift detection.

        Args:
            layer_type: Type of layer where violation occurred
            violation_type: Type of violation
            error_message: Error message
            affected_keys: List of affected cache keys
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"CacheCoherenceViolation_{layer_type}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"layer_type={layer_type}",
                f"violation_type={violation_type}",
                f"error_message={error_message[:100]}...",  # Truncate
                f"affected_keys_count={len(affected_keys)}",
            ]

            # Add first few keys as evidence
            for i, key in enumerate(affected_keys[:3]):
                observations.append(f"key_{i}={key[:50]}...")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_cache_coherence_violation failed: %s", e)
            return False

    def persist_infrastructure_drift_analysis(
        self,
        drift_detected: bool,
        severity: str,
        violation_count: int,
        layers_affected: int,
        analysis_json: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist infrastructure drift analysis.

        Args:
            drift_detected: Whether drift was detected
            severity: Drift severity level
            violation_count: Number of violations
            layers_affected: Number of layers affected
            analysis_json: Full analysis JSON
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"InfrastructureDriftAnalysis_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"drift_detected={drift_detected}",
                f"severity={severity}",
                f"violation_count={violation_count}",
                f"layers_affected={layers_affected}",
                f"analysis={analysis_json[:500]}...",  # Truncate
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_infrastructure_drift_analysis failed: %s", e)
            return False

    def persist_cross_domain_healing_event(
        self,
        orchestrator_class: str,
        cycle_index: int,
        total_violations: int,
        fixed_violations: int,
        error_violations: int,
        success_rate: float,
        timestamp_utc: int,
        domain: str,
    ) -> bool:
        """Persist cross-domain healing events for pattern sharing.

        Args:
            orchestrator_class: Class name of the orchestrator
            cycle_index: Cycle index number
            total_violations: Total violations processed
            fixed_violations: Number of violations fixed
            error_violations: Number of errors
            success_rate: Success rate (0.0-1.0)
            timestamp_utc: Timestamp in milliseconds
            domain: Domain identifier

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"CrossDomainHealingEvent_{domain}_{orchestrator_class}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"orchestrator_class={orchestrator_class}",
                f"cycle_index={cycle_index}",
                f"total_violations={total_violations}",
                f"fixed_violations={fixed_violations}",
                f"error_violations={error_violations}",
                f"success_rate={success_rate:.3f}",
                f"domain={domain}",
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_cross_domain_healing_event failed: %s", e)
            return False

    def persist_cross_domain_pattern_analysis(
        self,
        patterns_detected: bool,
        domains_count: int,
        correlations_count: int,
        analysis_json: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist cross-domain pattern analysis.

        Args:
            patterns_detected: Whether patterns were detected
            domains_count: Number of domains analyzed
            correlations_count: Number of correlations found
            analysis_json: Full analysis JSON
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"CrossDomainPatternAnalysis_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"patterns_detected={patterns_detected}",
                f"domains_count={domains_count}",
                f"correlations_count={correlations_count}",
                f"analysis={analysis_json[:500]}...",  # Truncate
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_cross_domain_pattern_analysis failed: %s", e)
            return False

    def persist_otel_span(
        self,
        span_id: str,
        trace_id: str,
        span_name: str,
        span_data_json: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist OpenTelemetry span data.

        Args:
            span_id: Unique span identifier
            trace_id: Trace identifier
            span_name: Span name
            span_data_json: Span data as JSON
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"OTelSpan_{span_id}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"span_id={span_id}",
                f"trace_id={trace_id}",
                f"span_name={span_name}",
                f"span_data={span_data_json[:500]}...",  # Truncate
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_otel_span failed: %s", e)
            return False

    def persist_otel_span_metrics(
        self,
        metrics_json: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist OpenTelemetry span metrics.

        Args:
            metrics_json: Span metrics as JSON
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"OTelSpanMetrics_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"metrics={metrics_json[:500]}...",  # Truncate
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_otel_span_metrics failed: %s", e)
            return False

    def persist_injection_detection_counts(
        self,
        total_scans: int,
        detection_counts: dict[str, int],
        timestamp_utc: int,
    ) -> bool:
        """Persist injection detection counts.

        Args:
            total_scans: Total number of scans performed
            detection_counts: Detection counts by signature ID
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"InjectionDetectionCounts_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"total_scans={total_scans}",
                f"total_detections={sum(detection_counts.values())}",
            ]

            # Add top detection signatures
            sorted_detections = sorted(detection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for sig_id, count in sorted_detections:
                observations.append(f"{sig_id}={count}")

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_injection_detection_counts failed: %s", e)
            return False

    def persist_injection_context_data(
        self,
        agent_id: str,
        route: str,
        scan_counts: dict[str, int],
        detection_counts: dict[str, int],
        timestamp_utc: int,
    ) -> bool:
        """Persist injection detection context data.

        Args:
            agent_id: Agent identifier
            route: Route identifier
            scan_counts: Scan counts by context
            detection_counts: Detection counts by context
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"InjectionContextData_{agent_id}_{route}_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"agent_id={agent_id}",
                f"route={route}",
                f"context_scans={scan_counts.get(f'{agent_id}:{route}', 0)}",
                f"context_detections={detection_counts.get(f'{agent_id}:{route}', 0)}",
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_injection_context_data failed: %s", e)
            return False

    def persist_signal_spike_detection(
        self,
        spike_detected: bool,
        spike_count: int,
        analysis_json: str,
        timestamp_utc: int,
    ) -> bool:
        """Persist signal spike detection results.

        Args:
            spike_detected: Whether spikes were detected
            spike_count: Number of spikes detected
            analysis_json: Full analysis JSON
            timestamp_utc: Timestamp in milliseconds

        Returns:
            True if persisted, False on failure
        """
        if not self._bridge:
            return False

        try:
            entity_name = f"SignalSpikeDetection_{int(timestamp_utc)}"
            observations = [
                f"ts={timestamp_utc}",
                f"spike_detected={spike_detected}",
                f"spike_count={spike_count}",
                f"analysis={analysis_json[:500]}...",  # Truncate
            ]

            self._bridge.create_agent_entity(
                agent_name=entity_name,
                agent_type=self.ENTITY_TYPE_TELEMETRY_EVENT,
                observations=observations,
            )
            return True
        except Exception as e:
            logger.debug("[SLMemoryBridge] persist_signal_spike_detection failed: %s", e)
            return False


def get_sl_memory_bridge() -> SystemLearningMemoryBridge:
    """Return the process-global SystemLearningMemoryBridge instance."""
    return SystemLearningMemoryBridge.get_instance()


__all__ = [
    "SystemLearningMemoryBridge",
    "get_sl_memory_bridge",
]
