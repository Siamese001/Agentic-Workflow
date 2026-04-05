"""Prometheus Metrics Module — L6 Observability Metric Definitions.

Wave 0: Instrumentation Prerequisites
Provides Counter, Histogram, and Gauge metrics for operational visibility
across all architectural layers (L0-L6).

Design:
- All metrics use semantic naming: agentic_workflow_{layer}_{operation}_{metric_type}
- Labels enable filtering by agent_type, operation, status, layer
- Cardinality controlled via allowed label values
"""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Info

# Global registry for agentic-workflow metrics
AGENTIC_REGISTRY = CollectorRegistry()

# =============================================================================
# L0 Routing Metrics
# =============================================================================

ROUTING_DECISIONS_TOTAL = Counter(
    "agentic_workflow_l0_routing_decisions_total",
    "Total routing decisions made by L0 routing layer",
    ["destination", "outcome"],  # destination: agent/capability/tool, outcome: success/failure
    registry=AGENTIC_REGISTRY,
)

ROUTING_LATENCY_SECONDS = Histogram(
    "agentic_workflow_l0_routing_latency_seconds",
    "Latency of routing decisions in seconds",
    ["routing_type"],  # routing_type: agent/capability/tool
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=AGENTIC_REGISTRY,
)

AGENT_REGISTRY_CHECKS_TOTAL = Counter(
    "agentic_workflow_l0_agent_registry_checks_total",
    "Total agent registry checks",
    ["result"],  # result: found/not_found/error
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# L1 Cognition / Retrieval Metrics
# =============================================================================

RETRIEVAL_REQUESTS_TOTAL = Counter(
    "agentic_workflow_l1_retrieval_requests_total",
    "Total retrieval requests",
    ["source", "status"],  # source: cache/vector/db, status: hit/miss/error
    registry=AGENTIC_REGISTRY,
)

RETRIEVAL_LATENCY_SECONDS = Histogram(
    "agentic_workflow_l1_retrieval_latency_seconds",
    "Latency of retrieval operations in seconds",
    ["source"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=AGENTIC_REGISTRY,
)

RETRIEVAL_GROUNDEDNESS_SCORE = Gauge(
    "agentic_workflow_l1_retrieval_groundedness_score",
    "Groundedness score of retrieval results (0.0-1.0)",
    ["query_type"],
    registry=AGENTIC_REGISTRY,
)

RETRIEVAL_FAITHFULNESS_RATIO = Gauge(
    "agentic_workflow_l1_retrieval_faithfulness_ratio",
    "Faithfulness ratio of retrieval results (0.0-1.0)",
    ["query_type"],
    registry=AGENTIC_REGISTRY,
)

CACHE_HITS_TOTAL = Counter(
    "agentic_workflow_l1_cache_hits_total",
    "Total cache hits",
    ["cache_type"],  # cache_type: embedding/result/token
    registry=AGENTIC_REGISTRY,
)

CACHE_MISSES_TOTAL = Counter(
    "agentic_workflow_l1_cache_misses_total",
    "Total cache misses",
    ["cache_type"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# L2 Execution Metrics
# =============================================================================

TOOL_INVOCATIONS_TOTAL = Counter(
    "agentic_workflow_l2_tool_invocations_total",
    "Total tool invocations",
    ["tool_name", "status"],  # status: success/failure/timeout
    registry=AGENTIC_REGISTRY,
)

TOOL_LATENCY_SECONDS = Histogram(
    "agentic_workflow_l2_tool_latency_seconds",
    "Latency of tool invocations in seconds",
    ["tool_name"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
    registry=AGENTIC_REGISTRY,
)

EXECUTION_ATTEMPTS_TOTAL = Counter(
    "agentic_workflow_l2_execution_attempts_total",
    "Total execution attempts",
    ["executor_type", "status"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# L3 Orchestration Metrics
# =============================================================================

ORCHESTRATION_RUNS_TOTAL = Counter(
    "agentic_workflow_l3_orchestration_runs_total",
    "Total orchestration runs",
    ["orchestrator_type", "status"],  # status: success/failure/timeout
    registry=AGENTIC_REGISTRY,
)

ORCHESTRATION_LATENCY_SECONDS = Histogram(
    "agentic_workflow_l3_orchestration_latency_seconds",
    "End-to-end orchestration latency in seconds",
    ["mission_type"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
    registry=AGENTIC_REGISTRY,
)

HEAL_ATTEMPTS_TOTAL = Counter(
    "agentic_workflow_l3_heal_attempts_total",
    "Total healing attempts",
    ["healing_type", "status"],  # status: success/failure/invalid
    registry=AGENTIC_REGISTRY,
)

HEAL_LATENCY_SECONDS = Histogram(
    "agentic_workflow_l3_heal_latency_seconds",
    "Latency of healing operations in seconds",
    ["healing_type"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
    registry=AGENTIC_REGISTRY,
)

AGENT_DISPATCHES_TOTAL = Counter(
    "agentic_workflow_l3_agent_dispatches_total",
    "Total agent dispatches",
    ["agent_type", "status"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# L4 State Metrics
# =============================================================================

SNAPSHOT_GENERATION_TOTAL = Counter(
    "agentic_workflow_l4_snapshot_generation_total",
    "Total runtime ADG snapshot generations",
    ["status"],  # status: success/failure
    registry=AGENTIC_REGISTRY,
)

SNAPSHOT_PERSIST_DURATION_SECONDS = Histogram(
    "agentic_workflow_l4_snapshot_persist_duration_seconds",
    "Time to persist snapshot to storage",
    [],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=AGENTIC_REGISTRY,
)

SNAPSHOT_SIZE_BYTES = Histogram(
    "agentic_workflow_l4_snapshot_size_bytes",
    "Size of generated snapshots in bytes",
    [],
    buckets=[1024, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216],
    registry=AGENTIC_REGISTRY,
)

REPLAY_ATTEMPTS_TOTAL = Counter(
    "agentic_workflow_l4_replay_attempts_total",
    "Total replay attempts",
    ["status"],  # status: success/divergence_detected/failure
    registry=AGENTIC_REGISTRY,
)

UWG_WRITES_TOTAL = Counter(
    "agentic_workflow_l4_uwg_writes_total",
    "Total writes through Universal Write Gateway",
    ["write_type", "status"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# L5 Safety Metrics
# =============================================================================

GUARDRAIL_TRIGGERS_TOTAL = Counter(
    "agentic_workflow_l5_guardrail_triggers_total",
    "Total guardrail triggers",
    ["guardrail_type", "action"],  # action: block/warn/alert
    registry=AGENTIC_REGISTRY,
)

POLICY_DENIALS_TOTAL = Counter(
    "agentic_workflow_l5_policy_denials_total",
    "Total policy denials",
    ["policy_type", "reason"],
    registry=AGENTIC_REGISTRY,
)

POLICY_CHECKS_TOTAL = Counter(
    "agentic_workflow_l5_policy_checks_total",
    "Total policy compliance checks",
    ["result"],  # result: pass/fail/error
    registry=AGENTIC_REGISTRY,
)

SAFETY_VALIDATION_LATENCY_SECONDS = Histogram(
    "agentic_workflow_l5_safety_validation_latency_seconds",
    "Latency of safety validations",
    [],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25],
    registry=AGENTIC_REGISTRY,
)

HUMAN_ESCALATIONS_TOTAL = Counter(
    "agentic_workflow_l5_human_escalations_total",
    "Total human escalations",
    ["escalation_reason"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# L6 Observability / Meta-Learning Metrics
# =============================================================================

TELEMETRY_EVENTS_TOTAL = Counter(
    "agentic_workflow_l6_telemetry_events_total",
    "Total telemetry events emitted",
    ["event_type"],
    registry=AGENTIC_REGISTRY,
)

META_LEARNING_PROPOSALS_TOTAL = Counter(
    "agentic_workflow_l6_meta_learning_proposals_total",
    "Total meta-learning proposals generated",
    ["status"],  # status: accepted/rejected/pending
    registry=AGENTIC_REGISTRY,
)

PATTERN_EXTRACTION_TOTAL = Counter(
    "agentic_workflow_l6_pattern_extraction_total",
    "Total patterns extracted from telemetry",
    ["pattern_type"],
    registry=AGENTIC_REGISTRY,
)

ANOMALY_DETECTIONS_TOTAL = Counter(
    "agentic_workflow_l6_anomaly_detections_total",
    "Total anomalies detected",
    ["anomaly_type", "severity"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# Cross-Layer / System Metrics
# =============================================================================

REQUESTS_TOTAL = Counter(
    "agentic_workflow_requests_total",
    "Total requests processed",
    ["layer", "status"],
    registry=AGENTIC_REGISTRY,
)

REQUEST_LATENCY_SECONDS = Histogram(
    "agentic_workflow_request_latency_seconds",
    "Request latency by layer",
    ["layer"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=AGENTIC_REGISTRY,
)

ACTIVE_RUNS = Gauge(
    "agentic_workflow_active_runs",
    "Number of currently active runs",
    ["layer"],
    registry=AGENTIC_REGISTRY,
)

EVALUATION_SCENARIOS_TOTAL = Counter(
    "agentic_workflow_evaluation_scenarios_total",
    "Total evaluation scenarios executed",
    ["suite_id", "status"],
    registry=AGENTIC_REGISTRY,
)

EVALUATION_PASS_RATE = Gauge(
    "agentic_workflow_evaluation_pass_rate",
    "Pass rate for evaluations (0.0-1.0)",
    ["suite_id"],
    registry=AGENTIC_REGISTRY,
)

# =============================================================================
# Build Info
# =============================================================================

BUILD_INFO = Info(
    "agentic_workflow_build",
    "Build information",
    registry=AGENTIC_REGISTRY,
)


def set_build_info(version: str, commit: str, branch: str) -> None:
    """Set build info metrics.

    Args:
        version: Semantic version string
        commit: Git commit hash
        branch: Git branch name
    """
    BUILD_INFO.info({
        "version": version,
        "commit": commit,
        "branch": branch,
    })


# =============================================================================
# Convenience Functions
# =============================================================================

def record_routing_decision(destination: str, outcome: str) -> None:
    """Record a routing decision.

    Args:
        destination: Where the request was routed (agent/capability/tool)
        outcome: Result of routing (success/failure)
    """
    ROUTING_DECISIONS_TOTAL.labels(destination=destination, outcome=outcome).inc()


def record_retrieval(source: str, status: str, latency_seconds: float) -> None:
    """Record a retrieval operation.

    Args:
        source: Source of retrieval (cache/vector/db)
        status: Result status (hit/miss/error)
        latency_seconds: Latency in seconds
    """
    RETRIEVAL_REQUESTS_TOTAL.labels(source=source, status=status).inc()
    RETRIEVAL_LATENCY_SECONDS.labels(source=source).observe(latency_seconds)


def record_tool_invocation(tool_name: str, status: str, latency_seconds: float) -> None:
    """Record a tool invocation.

    Args:
        tool_name: Name of the tool invoked
        status: Result status (success/failure/timeout)
        latency_seconds: Latency in seconds
    """
    TOOL_INVOCATIONS_TOTAL.labels(tool_name=tool_name, status=status).inc()
    TOOL_LATENCY_SECONDS.labels(tool_name=tool_name).observe(latency_seconds)


def record_guardrail_trigger(guardrail_type: str, action: str) -> None:
    """Record a guardrail trigger.

    Args:
        guardrail_type: Type of guardrail triggered
        action: Action taken (block/warn/alert)
    """
    GUARDRAIL_TRIGGERS_TOTAL.labels(guardrail_type=guardrail_type, action=action).inc()


def record_orchestration(mission_type: str, status: str, latency_seconds: float) -> None:
    """Record an orchestration run.

    Args:
        mission_type: Type of mission
        status: Result status (success/failure/timeout)
        latency_seconds: End-to-end latency in seconds
    """
    ORCHESTRATION_RUNS_TOTAL.labels(orchestrator_type=mission_type, status=status).inc()
    ORCHESTRATION_LATENCY_SECONDS.labels(mission_type=mission_type).observe(latency_seconds)


def record_heal_attempt(healing_type: str, status: str, latency_seconds: float) -> None:
    """Record a healing attempt.

    Args:
        healing_type: Type of healing performed
        status: Result status (success/failure/invalid)
        latency_seconds: Latency in seconds
    """
    HEAL_ATTEMPTS_TOTAL.labels(healing_type=healing_type, status=status).inc()
    HEAL_LATENCY_SECONDS.labels(healing_type=healing_type).observe(latency_seconds)


def record_snapshot_generation(status: str, persist_duration_seconds: float, size_bytes: int) -> None:
    """Record a snapshot generation.

    Args:
        status: Generation status (success/failure)
        persist_duration_seconds: Time to persist in seconds
        size_bytes: Size of snapshot in bytes
    """
    SNAPSHOT_GENERATION_TOTAL.labels(status=status).inc()
    SNAPSHOT_PERSIST_DURATION_SECONDS.observe(persist_duration_seconds)
    SNAPSHOT_SIZE_BYTES.observe(size_bytes)


def record_evaluation(suite_id: str, status: str, pass_rate: float) -> None:
    """Record an evaluation result.

    Args:
        suite_id: Evaluation suite identifier
        status: Overall status (passed/failed)
        pass_rate: Pass rate 0.0-1.0
    """
    EVALUATION_SCENARIOS_TOTAL.labels(suite_id=suite_id, status=status).inc()
    EVALUATION_PASS_RATE.labels(suite_id=suite_id).set(pass_rate)


def update_active_runs(layer: str, count: int) -> None:
    """Update the active runs gauge.

    Args:
        layer: Layer identifier (L0-L6)
        count: Current number of active runs
    """
    ACTIVE_RUNS.labels(layer=layer).set(count)


def record_telemetry_event(event_type: str) -> None:
    """Record a telemetry event.

    Args:
        event_type: Type of telemetry event
    """
    TELEMETRY_EVENTS_TOTAL.labels(event_type=event_type).inc()
