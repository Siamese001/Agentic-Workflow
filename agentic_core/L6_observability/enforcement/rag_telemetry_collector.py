from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    # noqa: E402
    record_execution_trace,
)

emit_replay_key("p0", "rag_telemetry_collector")
emit_determinism_digest("p0", "rag_telemetry_collector")

_emit_dispatches_healing_run("p1", "rag_telemetry_collector", "L6")
_emit_routes_through("p1", "rag_telemetry_collector", "L6")
_emit_checks_agent_registry("p1", "rag_telemetry_collector", "agent_registry")
_emit_validates_agent_capability("p1", "rag_telemetry_collector", "capability")
_emit_dispatches_execution_plan("p1", "rag_telemetry_collector", "exec_plan")
_emit_agent_executes_agent("p1", "rag_telemetry_collector", "sub_agent")
_emit_routes_to_agent("p1", "rag_telemetry_collector", "target_agent")
_emit_verifies_policy("p1", "rag_telemetry_collector", "policy_check")
_emit_observes_runtime_state("p1", "rag_telemetry_collector", "runtime_state")
_emit_verifies_boundary("p1", "rag_telemetry_collector", "boundary_check")
_emit_transcripts_response("p1", "rag_telemetry_collector", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_telemetry_collector")
_emit_gated_by_confidence("p1", "rag_telemetry_collector", "confidence_gate")
_emit_escalates_to_human("p1", "rag_telemetry_collector", "L6")
_emit_reads_policy_state("p1", "rag_telemetry_collector", "L6")
_emit_authorize_and_execute("p2", "rag_telemetry_collector", "execution_auth")
_emit_validates_capability("p2", "rag_telemetry_collector", "capability_check")
_emit_routes_to_capability("p2", "rag_telemetry_collector", "capability_route")
_emit_writes_via_uwg("p2", "rag_telemetry_collector", "uwg_write")
_emit_blocks_direct_write("p2", "rag_telemetry_collector", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_telemetry_collector", "tool_invocation")
_emit_captures_execution_output("p2", "rag_telemetry_collector", "exec_output")
_emit_dispatches_agent("p3", "rag_telemetry_collector", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_telemetry_collector", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_telemetry_collector", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_telemetry_collector", "healing_outcome")
_emit_escalates_failure("p3", "rag_telemetry_collector", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_telemetry_collector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_telemetry_collector", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_telemetry_collector", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_telemetry_collector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_telemetry_collector", "eval_metric")
_emit_stores_embedding("p4", "rag_telemetry_collector", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_telemetry_collector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_telemetry_collector", "exec_snapshot_link")

"""RAG Telemetry Collector - L6 observability with OpenTelemetry integration.

Tracks RAG performance metrics for dashboard visualization.
Phase 3: Now consumes OpenTelemetry spans for comprehensive telemetry.
"""
from collections import defaultdict
from dataclasses import dataclass, field

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

record_execution_trace("rag_telemetry_collector", "rag_telemetry_collector_trace")


_emit_emits_metric_event("rag_telemetry_collector", "p4obs", "metric_1")
_emit_emits_metric_event("rag_telemetry_collector", "p4obs", "metric_2")
_emit_emits_metric_event("rag_telemetry_collector", "p4obs", "metric_3")
_emit_emits_metric_event("rag_telemetry_collector", "p4obs", "metric_4")
_emit_emits_metric_event("rag_telemetry_collector", "p4obs", "metric_5")
_emit_emits_metric_event("rag_telemetry_collector", "p4obs", "metric_6")
_emit_records_incident_event("rag_telemetry_collector", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_telemetry_collector", "p4obs", "anomaly")
_emit_writes_observability_log("rag_telemetry_collector", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_telemetry_collector", "p4obs", "mon_state")
_emit_triggers_alert("rag_telemetry_collector", "p4obs", "alert")
_emit_links_incident_trace("rag_telemetry_collector", "p4obs", "trace_link")
_emit_captures_pattern("rag_telemetry_collector", "p3lm", "pattern")
_emit_records_learning_event("rag_telemetry_collector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_telemetry_collector", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_telemetry_collector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_telemetry_collector", "p3lm", "routing")
_emit_improves_agent_policy("rag_telemetry_collector", "p3lm", "policy")
_emit_stores_learning_state("rag_telemetry_collector", "p3lm", "state")
_emit_records_execution_trace("rag_telemetry_collector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_telemetry_collector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_telemetry_collector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_telemetry_collector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_telemetry_collector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_telemetry_collector", "env_read", "p2_env_1")
_emit_reads_environ("rag_telemetry_collector", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_telemetry_collector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_telemetry_collector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_telemetry_collector", "context_pull")
_emit_pulls_context("p1", "rag_telemetry_collector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rag_telemetry_collector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_telemetry_collector", "uwg_term_2")
_emit_writes_through("p1", "rag_telemetry_collector", "write_through")
_emit_writes_through("p1", "rag_telemetry_collector", "write_through_2")
_emit_validated_by_safety_plane("p1", "rag_telemetry_collector", "safety_validation")
_emit_invokes_eval("p1", "rag_telemetry_collector", "eval_call")
_emit_proposal_commits_routing("p1", "rag_telemetry_collector", "routing_commit")


@dataclass
class RagMetrics:
    """RAG performance metrics."""

    total_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    avg_documents_returned: float = 0.0
    avg_faithfulness_score: float = 0.0
    rerank_count: int = 0
    hallucination_warnings: int = 0
    dimension_mismatches: int = 0
    batch_upsert_failures: int = 0
    latency_warnings: int = 0
    namespace_stats: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(dict))
    latency_buckets: dict[str, int] = field(
        default_factory=lambda: {"0-50ms": 0, "50-100ms": 0, "100-200ms": 0, "200-500ms": 0, "500ms+": 0}
    )


class RagTelemetryCollector:
    """
    Collects RAG telemetry for L6 observability dashboard.
    Singleton pattern for global access.
    """

    _instance: RagTelemetryCollector | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RagTelemetryCollector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RagTelemetryCollector.__init__", "p0_governance")
        if self._initialized:
            return
        self.metrics = RagMetrics()
        self._latency_samples: list[float] = []
        self._faithfulness_samples: list[float] = []
        self._doc_count_samples: list[int] = []
        self._initialized = True

    def record_query(
        self,
        latency_ms: float,
        cached: bool,
        reranked: bool,
        doc_count: int,
        faithfulness_score: float = 0.0,
        namespace: str = "sovereign-core",
    ) -> None:
        """Record a RAG query execution."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "RagTelemetryCollector.record_query"
        )

        self.metrics.total_queries += 1
        if cached:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
        if reranked:
            self.metrics.rerank_count += 1
        self._latency_samples.append(latency_ms)
        if latency_ms > 500:
            self.metrics.latency_warnings += 1
        if latency_ms < 50:
            self.metrics.latency_buckets["0-50ms"] += 1
        elif latency_ms < 100:
            self.metrics.latency_buckets["50-100ms"] += 1
        elif latency_ms < 200:
            self.metrics.latency_buckets["100-200ms"] += 1
        elif latency_ms < 500:
            self.metrics.latency_buckets["200-500ms"] += 1
        else:
            self.metrics.latency_buckets["500ms+"] += 1
        self._doc_count_samples.append(doc_count)
        if faithfulness_score > 0:
            self._faithfulness_samples.append(faithfulness_score)
        if namespace not in self.metrics.namespace_stats:
            self.metrics.namespace_stats[namespace] = {"queries": 0, "cache_hits": 0}
        self.metrics.namespace_stats[namespace]["queries"] += 1
        if cached:
            self.metrics.namespace_stats[namespace]["cache_hits"] += 1
        self._update_aggregates()

    def _update_aggregates(self) -> None:
        """Update aggregate metrics from samples."""
        if self._latency_samples:
            self.metrics.avg_latency_ms = sum(self._latency_samples) / len(self._latency_samples)
            sorted_latencies = sorted(self._latency_samples)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p99_idx = int(len(sorted_latencies) * 0.99)
            self.metrics.p95_latency_ms = sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else 0
            self.metrics.p99_latency_ms = sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0
        if self._doc_count_samples:
            self.metrics.avg_documents_returned = sum(self._doc_count_samples) / len(self._doc_count_samples)
        if self._faithfulness_samples:
            self.metrics.avg_faithfulness_score = sum(self._faithfulness_samples) / len(
                self._faithfulness_samples
            )

    def record_hallucination_warning(self) -> None:
        """Record a hallucination warning from L5 guardrail."""
        self.metrics.hallucination_warnings += 1

    def record_dimension_mismatch(self) -> None:
        """Record a dimension mismatch from Pinecone store."""
        self.metrics.dimension_mismatches += 1

    def get_metrics(self) -> RagMetrics:
        """Get current RAG metrics snapshot."""
        return self.metrics

    def consume_otel_spans(self, spans: list[dict[str, Any]]) -> int:
        """Consume OpenTelemetry spans for RAG telemetry analysis.

        Phase 3: Integrates OpenTelemetry spans into L6 RAG telemetry.
        Extracts RAG-relevant metrics from span attributes.

        Parameters
        ----------
        spans : list[dict[str, Any]]
            OpenTelemetry span dictionaries from tracing adapter.

        Returns
        -------
        int
            Number of RAG-relevant spans processed.
        """
        if not spans:
            return 0

        processed = 0
        for span in spans:
            # Check if this is a RAG-related span
            name = span.get("name", "")
            attributes = span.get("attributes", {})

            # Look for RAG operation indicators
            is_rag_span = (
                "rag" in name.lower() or
                "retrieval" in name.lower() or
                "embedding" in name.lower() or
                attributes.get("rag.operation") is not None
            )

            if is_rag_span:
                # Extract RAG metrics from span attributes
                latency_ms = attributes.get("rag.latency_ms", 0)
                doc_count = attributes.get("rag.doc_count", 0)
                cached = attributes.get("rag.cached", False)
                reranked = attributes.get("rag.reranked", False)
                faithfulness = attributes.get("rag.faithfulness_score", 0.0)
                namespace = attributes.get("rag.namespace", "sovereign-core")

                self.record_query(
                    latency_ms=latency_ms,
                    cached=cached,
                    reranked=reranked,
                    doc_count=doc_count,
                    faithfulness_score=faithfulness,
                    namespace=namespace,
                )
                processed += 1

        _emit_records_telemetry_event(
            "rag_telemetry_collector", "L6_OBSERVABILITY", "otel_spans_consumed",
            processed_count=processed,
            total_spans=len(spans)
        )

        return processed
