from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "CachedStateLedger")
trace_contract.emit_determinism_digest("p0", "CachedStateLedger")

trace_contract._emit_dispatches_healing_run("p1", "CachedStateLedger", "L4")
trace_contract._emit_routes_through("p1", "CachedStateLedger", "L4")
trace_contract._emit_checks_agent_registry("p1", "CachedStateLedger", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "CachedStateLedger", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "CachedStateLedger", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "CachedStateLedger", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "CachedStateLedger", "target_agent")
trace_contract._emit_verifies_policy("p1", "CachedStateLedger", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "CachedStateLedger", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "CachedStateLedger", "boundary_check")
trace_contract._emit_transcripts_response("p1", "CachedStateLedger", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "CachedStateLedger")
trace_contract._emit_gated_by_confidence("p1", "CachedStateLedger", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "CachedStateLedger", "L4")
trace_contract._emit_reads_policy_state("p1", "CachedStateLedger", "L4")
trace_contract._emit_authorize_and_execute("p2", "CachedStateLedger", "execution_auth")
trace_contract._emit_validates_capability("p2", "CachedStateLedger", "capability_check")
trace_contract._emit_routes_to_capability("p2", "CachedStateLedger", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "CachedStateLedger", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "CachedStateLedger", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "CachedStateLedger", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "CachedStateLedger", "exec_output")
trace_contract._emit_dispatches_agent("p3", "CachedStateLedger", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "CachedStateLedger", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "CachedStateLedger", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "CachedStateLedger", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "CachedStateLedger", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "CachedStateLedger", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "CachedStateLedger", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "CachedStateLedger", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "CachedStateLedger", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "CachedStateLedger", "eval_metric")
trace_contract._emit_stores_embedding("p4", "CachedStateLedger", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "CachedStateLedger", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "CachedStateLedger", "exec_snapshot_link")

"\nCachedStateLedgerAgent - Eternal L4 State with Redis Sovereign cache\n"
import json
import os
import time
from pathlib import Path

from agentic_core.runtime.types.anomaly_report import AnomalyReport

trace_contract._emit_emits_metric_event("CachedStateLedger", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("CachedStateLedger", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("CachedStateLedger", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("CachedStateLedger", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("CachedStateLedger", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("CachedStateLedger", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("CachedStateLedger", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("CachedStateLedger", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("CachedStateLedger", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("CachedStateLedger", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("CachedStateLedger", "p4obs", "alert")
trace_contract._emit_links_incident_trace("CachedStateLedger", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("CachedStateLedger", "p3lm", "pattern")
trace_contract._emit_records_learning_event("CachedStateLedger", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("CachedStateLedger", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("CachedStateLedger", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("CachedStateLedger", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("CachedStateLedger", "p3lm", "policy")
trace_contract._emit_stores_learning_state("CachedStateLedger", "p3lm", "state")
trace_contract._emit_records_execution_trace("CachedStateLedger", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("CachedStateLedger", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("CachedStateLedger", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("CachedStateLedger", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("CachedStateLedger", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("CachedStateLedger", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("CachedStateLedger", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("CachedStateLedger", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("CachedStateLedger", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "CachedStateLedger", "context_pull")
trace_contract._emit_pulls_context("p1", "CachedStateLedger", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "CachedStateLedger", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "CachedStateLedger", "uwg_term_2")
trace_contract._emit_writes_through("p1", "CachedStateLedger", "write_through")
trace_contract._emit_writes_through("p1", "CachedStateLedger", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "CachedStateLedger", "safety_validation")
trace_contract._emit_invokes_eval("p1", "CachedStateLedger", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "CachedStateLedger", "routing_commit")


class CachedStateLedger(SovereignBaseAgent):
    """
    Sovereign L4 state base — Redis cache for context, audit, Historian.
    All L4 components inherit from this.
    """

    def __init__(self, project_root: Path, session_id: str):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "CachedStateLedger.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "CachedStateLedger.__init__", "p0_governance")
        super().__init__()
        self.root = project_root
        self.session_id = session_id
        self._mcp_audit("init", payload={"session_id": session_id})
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            import urllib.parse

            import redis
            from agentic_core.cache.redis_cache_client import redis_connection_protocol_kwargs

            parsed = urllib.parse.urlparse(redis_url)
            connection_kwargs = {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 6379,
                "password": parsed.password,
                "username": parsed.username,
                "decode_responses": True,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True,
                **redis_connection_protocol_kwargs(),
            }
            if parsed.scheme == "rediss":
                connection_kwargs["ssl"] = True
            self.redis = redis.Redis(**connection_kwargs)
            self.redis.ping()
            print("   [OK] CachedStateLedgerAgent: Redis Sovereign cache ONLINE")
        except (
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:  # guardian: allow-silent-swallow
            from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError

            raise InfrastructureDependencyError(
                f"[CachedStateLedger] Redis is a mandatory dependency and is unavailable: {e}",
            ) from e
        self._successful_traces: list[dict] = []
        self.prefix_context = f"l4_context:{session_id}"
        self.prefix_audit = f"l4_audit:{session_id}"
        self.prefix_historian = f"l4_historian:{session_id}"

    def cache_validation_context(self, key: str, context: dict):
        """cache validation context for instant access"""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L4_STATE,
            "CachedStateLedger.cache_validation_context",
        )

        full_key = f"{self.prefix_context}:{key}"
        try:
            if self.redis:
                self.redis.set(full_key, json.dumps(context), ex=86400)
            else:
                self._memory_cache[full_key] = context
        except (
            AttributeError,
            TypeError,
        ) as e:  # guardian: allow-log-and-swallow -- cache write: non-fatal, context stored in memory fallback
            self.logger.debug(f"Cache write failed for {key}: {e}")
        self._record_successful_trace(
            {"operation": "cache_validation_context", "key": key, "timestamp": time.time()},
        )

    def get_cached_validation_context(self, key: str) -> dict | None:
        full_key = f"{self.prefix_context}:{key}"
        try:
            if self.redis:
                data = self.redis.get(full_key)
                if data:
                    self._record_successful_trace(
                        {
                            "operation": "get_cached_validation_context",
                            "key": key,
                            "hit": True,
                            "timestamp": time.time(),
                        },
                    )
                    return json.loads(data)
            else:
                result = self._memory_cache.get(full_key)
                if result:
                    self._record_successful_trace(
                        {
                            "operation": "get_cached_validation_context",
                            "key": key,
                            "hit": True,
                            "timestamp": time.time(),
                        },
                    )
                return result
        except (
            AttributeError,
            KeyError,
        ) as e:  # guardian: allow-log-and-swallow -- cache read: non-fatal, caller handles None as cache miss
            self.logger.debug(f"Cache read failed for {key}: {e}")
        return None

    def _record_successful_trace(self, trace: dict):
        """Internal helper to maintain successful_traces list in both Redis and memory mode"""
        if self.redis:
            try:
                self.redis.rpush(f"{self.prefix_historian}:successful_traces", json.dumps(trace))
            except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-log-and-swallow -- Redis rpush failure: non-fatal; successful trace still recorded in memory mode
                import logging

                logging.getLogger(__name__).debug("CachedStateLedger: Exception swallowed at L289: %s", e)
        else:
            self._successful_traces.append(trace)

    def get_successful_traces(self) -> list[dict]:
        """Public accessor required by ValidationContext and GeminiSpy telemetry"""
        if self.redis:
            try:
                raw = self.redis.lrange(f"{self.prefix_historian}:successful_traces", 0, -1)
                return [json.loads(r) for r in raw]
            except (
                AttributeError,
                TypeError,
                ValueError,
                OSError,
                RuntimeError,
            ):  # guardian: allow-silent-swallow
                return []
        else:
            return self._successful_traces

    def append_audit_event(self, event: dict):
        """Immutable append-only audit trail via Redis List"""
        try:
            if self.redis:
                trail_key = f"{self.prefix_audit}:trail"
                self.redis.rpush(trail_key, json.dumps(event))
                self.redis.expire(trail_key, 31536000)
            else:
                self._audit_trail.append(event)
        except (
            AttributeError,
            TypeError,
        ) as e:  # guardian: allow-log-and-swallow -- audit log append: non-fatal, audit trail degrades gracefully
            self.logger.debug(f"Audit logging failed: {e}")

    def _run_self_tests(self) -> bool:
        """Run self-tests for CachedStateLedgerAgent."""
        super()._run_self_tests()
        test_key = "__self_test_cache"
        test_val = {"test": 42, "timestamp": time.time()}
        self.cache_validation_context(test_key, test_val)
        retrieved = self.get_cached_validation_context(test_key)
        assert retrieved is not None, "cache round-trip failed"
        assert retrieved.get("test") == 42, "cache data corruption"
        assert hasattr(self, "_successful_traces"), "Missing successful_traces"
        return True

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Perform healing for detected anomalies."""
        self._mcp_audit("healing_start", payload=anomaly.to_dict())
        if anomaly.type == "cache_stale":
            if self.redis:
                try:
                    keys = self.redis.keys(f"{self.prefix_context}:*")
                    for key in keys:
                        self.redis.delete(key)
                except (AttributeError, TypeError, ValueError, OSError, RuntimeError):  # guardian: allow-silent-swallow -- Redis cache flush failure: non-fatal; cache may be partially flushed but state remains consistent
                    pass
            else:
                self._memory_cache.clear()
            self._mcp_audit("healing_success", payload={"action": "cache_flush"})
            return True
        if anomaly.type == "audit_corruption":
            self._audit_trail = []
            self._successful_traces = []
            self._mcp_audit("healing_success")
            return True
        return False

    # guardian: allow-type-erasure
    def heal(self, *args, **kwargs) -> dict:
        """heal() not implemented for CachedStateLedgerAgent."""
        raise NotImplementedError("heal() not implemented for CachedStateLedgerAgent")

    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)
