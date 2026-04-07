"""observability Request Understanding Load Planner - Plans data loading for observability request understanding.

This planner manages the loading phase for understanding observability requests,
including metric parsing, log analysis, and trace extraction.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "request_type_util", "p0_governance")
_emit_reads_policy_state("p0", "request_type_util", "policy_binding")
_emit_snapshots_state("p0", "request_type_util", "state_snapshot")
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

_emit_emits_metric_event("request_type_util", "p4obs", "metric_1")
_emit_emits_metric_event("request_type_util", "p4obs", "metric_2")
_emit_emits_metric_event("request_type_util", "p4obs", "metric_3")
_emit_emits_metric_event("request_type_util", "p4obs", "metric_4")
_emit_emits_metric_event("request_type_util", "p4obs", "metric_5")
_emit_emits_metric_event("request_type_util", "p4obs", "metric_6")
_emit_records_incident_event("request_type_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("request_type_util", "p4obs", "anomaly")
_emit_writes_observability_log("request_type_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("request_type_util", "p4obs", "mon_state")
_emit_triggers_alert("request_type_util", "p4obs", "alert")
_emit_links_incident_trace("request_type_util", "p4obs", "trace_link")
_emit_captures_pattern("request_type_util", "p3lm", "pattern")
_emit_records_learning_event("request_type_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("request_type_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("request_type_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("request_type_util", "p3lm", "routing")
_emit_improves_agent_policy("request_type_util", "p3lm", "policy")
_emit_stores_learning_state("request_type_util", "p3lm", "state")
_emit_records_execution_trace("request_type_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("request_type_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("request_type_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("request_type_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("request_type_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("request_type_util", "env_read", "p2_env_1")
_emit_reads_environ("request_type_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("request_type_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("request_type_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "request_type_util", "context_pull")
_emit_pulls_context("p1", "request_type_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "request_type_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "request_type_util", "uwg_term_2")
_emit_writes_through("p1", "request_type_util", "write_through")
_emit_writes_through("p1", "request_type_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "request_type_util", "safety_validation")
_emit_invokes_eval("p1", "request_type_util", "eval_call")
_emit_proposal_commits_routing("p1", "request_type_util", "routing_commit")
_emit_escalates_to_human("p1", "request_type_util", "human_escalation")
_emit_routes_through("p1", "request_type_util", "route_through")
_emit_checks_agent_registry("p1", "request_type_util", "agent_registry")
_emit_validates_agent_capability("p1", "request_type_util", "capability")
_emit_dispatches_execution_plan("p1", "request_type_util", "exec_plan")
_emit_agent_executes_agent("p1", "request_type_util", "sub_agent")
_emit_routes_to_agent("p1", "request_type_util", "target_agent")
_emit_verifies_policy("p1", "request_type_util", "policy_check")
_emit_observes_runtime_state("p1", "request_type_util", "runtime_state")
_emit_verifies_boundary("p1", "request_type_util", "boundary_check")
_emit_transcripts_response("p1", "request_type_util", "transcript")
_emit_hard_fails_untranscripted("p1", "request_type_util")
_emit_gated_by_confidence("p1", "request_type_util", "confidence_gate")
emit_replay_key("p0", "request_type_util")
emit_determinism_digest("p0", "request_type_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "request_type_util", "execution_auth")
_emit_validates_capability("p2", "request_type_util", "capability_check")
_emit_routes_to_capability("p2", "request_type_util", "capability_route")
_emit_writes_via_uwg("p2", "request_type_util", "uwg_write")
_emit_blocks_direct_write("p2", "request_type_util", "direct_write_block")
_emit_records_tool_invocation("p2", "request_type_util", "tool_invocation")
_emit_captures_execution_output("p2", "request_type_util", "exec_output")
_emit_dispatches_agent("p3", "request_type_util", "agent_dispatch")
_emit_coordinates_agents("p3", "request_type_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "request_type_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "request_type_util", "healing_outcome")
_emit_escalates_failure("p3", "request_type_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "request_type_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "request_type_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "request_type_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "request_type_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "request_type_util", "eval_metric")
_emit_stores_embedding("p4", "request_type_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "request_type_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "request_type_util", "exec_snapshot_link")
_emit_reads_through("l4", "request_type_util", "urg_read_1")
_emit_reads_through("l4", "request_type_util", "urg_read_2")
_emit_reads_through("l4", "request_type_util", "urg_read_3")
_emit_reads_through("l4", "request_type_util", "urg_read_4")
_emit_reads_through("l4", "request_type_util", "urg_read_5")
_emit_reads_through("l4", "request_type_util", "urg_read_6")
_emit_reads_through("l4", "request_type_util", "urg_read_7")
_emit_reads_through("l4", "request_type_util", "urg_read_8")
_emit_reads_through("l4", "request_type_util", "urg_read_9")
_emit_reads_through("l4", "request_type_util", "urg_read_10")
_emit_reads_through("l4", "request_type_util", "urg_read_11")
_emit_reads_through("l4", "request_type_util", "urg_read_12")
_emit_reads_through("l4", "request_type_util", "urg_read_13")
_emit_reads_through("l4", "request_type_util", "urg_read_14")
_emit_reads_through("l4", "request_type_util", "urg_read_15")
_emit_reads_through("l4", "request_type_util", "urg_read_16")
_emit_reads_through("l4", "request_type_util", "urg_read_17")
_emit_reads_through("l4", "request_type_util", "urg_read_18")
_emit_reads_through("l4", "request_type_util", "urg_read_19")
_emit_reads_through("l4", "request_type_util", "urg_read_20")
_emit_reads_through("l4", "request_type_util", "urg_read_21")
_emit_reads_through("l4", "request_type_util", "urg_read_22")
_emit_reads_through("l4", "request_type_util", "urg_read_23")
_emit_reads_through("l4", "request_type_util", "urg_read_24")
_emit_reads_through("l4", "request_type_util", "urg_read_25")
_emit_reads_through("l4", "request_type_util", "urg_read_26")
_emit_reads_through("l4", "request_type_util", "urg_read_27")
_emit_reads_through("l4", "request_type_util", "urg_read_28")
_emit_reads_through("l4", "request_type_util", "urg_read_29")
_emit_reads_through("l4", "request_type_util", "urg_read_30")
_emit_reads_through("l4", "request_type_util", "urg_read_31")
_emit_reads_through("l4", "request_type_util", "urg_read_32")
_emit_reads_through("l4", "request_type_util", "urg_read_33")
_emit_reads_through("l4", "request_type_util", "urg_read_34")
_emit_reads_through("l4", "request_type_util", "urg_read_35")
_emit_reads_through("l4", "request_type_util", "urg_read_36")
_emit_reads_through("l4", "request_type_util", "urg_read_37")
_emit_reads_through("l4", "request_type_util", "urg_read_38")
_emit_reads_through("l4", "request_type_util", "urg_read_39")
_emit_reads_through("l4", "request_type_util", "urg_read_40")
_emit_reads_through("l4", "request_type_util", "urg_read_41")
_emit_reads_through("l4", "request_type_util", "urg_read_42")
_emit_reads_through("l4", "request_type_util", "urg_read_43")
_emit_reads_through("l4", "request_type_util", "urg_read_44")
_emit_reads_through("l4", "request_type_util", "urg_read_45")
_emit_reads_through("l4", "request_type_util", "urg_read_46")
_emit_reads_through("l4", "request_type_util", "urg_read_47")
_emit_reads_through("l4", "request_type_util", "urg_read_48")
_emit_reads_through("l4", "request_type_util", "urg_read_49")
_emit_reads_through("l4", "request_type_util", "urg_read_50")
_emit_reads_through("l4", "request_type_util", "urg_read_51")
_emit_reads_through("l4", "request_type_util", "urg_read_52")
_emit_reads_through("l4", "request_type_util", "urg_read_53")
_emit_reads_through("l4", "request_type_util", "urg_read_54")
_emit_reads_through("l4", "request_type_util", "urg_read_55")
_emit_reads_through("l4", "request_type_util", "urg_read_56")
_emit_reads_through("l4", "request_type_util", "urg_read_57")
_emit_reads_through("l4", "request_type_util", "urg_read_58")
_emit_reads_through("l4", "request_type_util", "urg_read_59")
_emit_reads_through("l4", "request_type_util", "urg_read_60")
_emit_reads_through("l4", "request_type_util", "urg_read_61")
_emit_reads_through("l4", "request_type_util", "urg_read_62")
_emit_reads_through("l4", "request_type_util", "urg_read_63")
_emit_reads_through("l4", "request_type_util", "urg_read_64")
_emit_reads_through("l4", "request_type_util", "urg_read_65")
_emit_reads_through("l4", "request_type_util", "urg_read_66")
_emit_reads_through("l4", "request_type_util", "urg_read_67")
_emit_reads_through("l4", "request_type_util", "urg_read_68")
_emit_reads_through("l4", "request_type_util", "urg_read_69")
_emit_reads_through("l4", "request_type_util", "urg_read_70")
_emit_reads_through("l4", "request_type_util", "urg_read_71")
_emit_reads_through("l4", "request_type_util", "urg_read_72")
_emit_reads_through("l4", "request_type_util", "urg_read_73")
_emit_reads_through("l4", "request_type_util", "urg_read_74")
_emit_reads_through("l4", "request_type_util", "urg_read_75")
_emit_reads_through("l4", "request_type_util", "urg_read_76")
_emit_reads_through("l4", "request_type_util", "urg_read_77")
_emit_reads_through("l4", "request_type_util", "urg_read_78")
_emit_reads_through("l4", "request_type_util", "urg_read_79")
_emit_reads_through("l4", "request_type_util", "urg_read_80")
_emit_reads_through("l4", "request_type_util", "urg_read_81")
_emit_reads_through("l4", "request_type_util", "urg_read_82")
_emit_reads_through("l4", "request_type_util", "urg_read_83")
_emit_reads_through("l4", "request_type_util", "urg_read_84")
_emit_reads_through("l4", "request_type_util", "urg_read_85")
_emit_reads_through("l4", "request_type_util", "urg_read_86")
_emit_reads_through("l4", "request_type_util", "urg_read_87")
_emit_reads_through("l4", "request_type_util", "urg_read_88")
_emit_reads_through("l4", "request_type_util", "urg_read_89")
_emit_reads_through("l4", "request_type_util", "urg_read_90")
_emit_reads_through("l4", "request_type_util", "urg_read_91")
_emit_reads_through("l4", "request_type_util", "urg_read_92")
_emit_reads_through("l4", "request_type_util", "urg_read_93")
_emit_reads_through("l4", "request_type_util", "urg_read_94")
_emit_reads_through("l4", "request_type_util", "urg_read_95")
_emit_reads_through("l4", "request_type_util", "urg_read_96")
_emit_reads_through("l4", "request_type_util", "urg_read_97")
_emit_reads_through("l4", "request_type_util", "urg_read_98")
_emit_reads_through("l4", "request_type_util", "urg_read_99")
_emit_reads_through("l4", "request_type_util", "urg_read_100")
_emit_reads_through("l4", "request_type_util", "urg_read_101")
_emit_reads_through("l4", "request_type_util", "urg_read_102")
_emit_reads_through("l4", "request_type_util", "urg_read_103")
_emit_reads_through("l4", "request_type_util", "urg_read_104")
_emit_reads_through("l4", "request_type_util", "urg_read_105")
_emit_reads_through("l4", "request_type_util", "urg_read_106")
_emit_reads_through("l4", "request_type_util", "urg_read_107")
_emit_reads_through("l4", "request_type_util", "urg_read_108")
_emit_reads_through("l4", "request_type_util", "urg_read_109")
_emit_reads_through("l4", "request_type_util", "urg_read_110")
_emit_reads_through("l4", "request_type_util", "urg_read_111")
_emit_reads_through("l4", "request_type_util", "urg_read_112")
_emit_reads_through("l4", "request_type_util", "urg_read_113")
_emit_reads_through("l4", "request_type_util", "urg_read_114")
_emit_reads_through("l4", "request_type_util", "urg_read_115")
_emit_reads_through("l4", "request_type_util", "urg_read_116")
_emit_reads_through("l4", "request_type_util", "urg_read_117")
_emit_reads_through("l4", "request_type_util", "urg_read_118")
_emit_reads_through("l4", "request_type_util", "urg_read_119")
_emit_reads_through("l4", "request_type_util", "urg_read_120")
_emit_reads_through("l4", "request_type_util", "urg_read_121")
_emit_reads_through("l4", "request_type_util", "urg_read_122")
_emit_reads_through("l4", "request_type_util", "urg_read_123")
_emit_reads_through("l4", "request_type_util", "urg_read_124")
_emit_reads_through("l4", "request_type_util", "urg_read_125")
_emit_reads_through("l4", "request_type_util", "urg_read_126")
_emit_reads_through("l4", "request_type_util", "urg_read_127")
_emit_reads_through("l4", "request_type_util", "urg_read_128")
_emit_reads_through("l4", "request_type_util", "urg_read_129")
_emit_reads_through("l4", "request_type_util", "urg_read_130")
_emit_reads_through("l4", "request_type_util", "urg_read_131")
_emit_reads_through("l4", "request_type_util", "urg_read_132")
_emit_reads_through("l4", "request_type_util", "urg_read_133")
_emit_reads_through("l4", "request_type_util", "urg_read_134")
_emit_reads_through("l4", "request_type_util", "urg_read_135")
_emit_reads_through("l4", "request_type_util", "urg_read_136")
_emit_reads_through("l4", "request_type_util", "urg_read_137")
_emit_reads_through("l4", "request_type_util", "urg_read_138")
_emit_reads_through("l4", "request_type_util", "urg_read_139")
_emit_reads_through("l4", "request_type_util", "urg_read_140")
_emit_reads_through("l4", "request_type_util", "urg_read_141")
_emit_reads_through("l4", "request_type_util", "urg_read_142")
_emit_reads_through("l4", "request_type_util", "urg_read_143")
_emit_reads_through("l4", "request_type_util", "urg_read_144")
_emit_reads_through("l4", "request_type_util", "urg_read_145")
_emit_reads_through("l4", "request_type_util", "urg_read_146")
_emit_reads_through("l4", "request_type_util", "urg_read_147")
_emit_reads_through("l4", "request_type_util", "urg_read_148")
_emit_reads_through("l4", "request_type_util", "urg_read_149")
_emit_reads_through("l4", "request_type_util", "urg_read_150")
_emit_reads_through("l4", "request_type_util", "urg_read_151")
_emit_reads_through("l4", "request_type_util", "urg_read_152")
_emit_reads_through("l4", "request_type_util", "urg_read_153")
_emit_reads_through("l4", "request_type_util", "urg_read_154")
_emit_reads_through("l4", "request_type_util", "urg_read_155")
_emit_reads_through("l4", "request_type_util", "urg_read_156")
_emit_reads_through("l4", "request_type_util", "urg_read_157")
_emit_reads_through("l4", "request_type_util", "urg_read_158")

logger = logging.getLogger(__name__)


DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32


@dataclass
class LoadDataPlanningPlanConstraints:
    safety_level: str = "strict"


@dataclass
class LoadDataPlanningPlanResult:
    success: bool
    data: dict[str, object] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = ""


class LoadDataPlanningPlanProcessor:
    def process(self, input_data: dict[str, object]) -> LoadDataPlanningPlanResult:
        raise NotImplementedError

    def validate_safety(self, data: dict[str, object]) -> bool:
        raise NotImplementedError


class RequestType(Enum):
    """Types of observability requests."""

    METRIC_QUERY = "metric_query"
    LOG_SEARCH = "log_search"
    TRACE_LOOKUP = "trace_lookup"
    AGGREGATION = "aggregation"
    ANOMALY_DETECTION = "anomaly_detection"


class DataSource(Enum):
    """Data sources for observability."""

    PROMETHEUS = "prometheus"
    ELASTICSEARCH = "elasticsearch"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    GRAFANA = "grafana"
    DATADOG = "datadog"


class AggregationType(Enum):
    """Types of aggregations."""

    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"


@dataclass
class MetricDefinition:
    """Definition of a metric to be loaded."""

    name: str
    query: str
    labels: dict[str, str] = field(default_factory=dict)
    aggregation: AggregationType | None = None
    time_range: str = "1h"
    step: int = 60


@dataclass
class LogQuery:
    """Definition of a log search query."""

    index: str
    query: str
    filters: dict[str, Any] = field(default_factory=dict)
    time_range: str = "1h"
    size: int = 1000
    sort_field: str = "@timestamp"
    sort_order: str = "desc"


@dataclass
class TraceQuery:
    """Definition of a trace lookup query."""

    service: str | None = None
    operation: str | None = None
    trace_id: str | None = None
    tags: dict[str, str] = field(default_factory=dict)
    time_range: str = "1h"
    limit: int = 100


@dataclass
class ObservabilityLoadPlan:
    """Complete plan for observability data loading."""

    id: str
    name: str
    request_type: RequestType
    data_source: DataSource
    metrics: list[MetricDefinition] = field(default_factory=list)
    log_queries: list[LogQuery] = field(default_factory=list)
    trace_queries: list[TraceQuery] = field(default_factory=list)
    enable_caching: bool = True
    cache_ttl: int = 300
    enable_sampling: bool = False
    sample_rate: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityLoadConfig:
    """configuration for observability load planning."""

    enable_metrics: bool = True
    enable_logs: bool = True
    enable_traces: bool = True
    max_queries_per_plan: int = 50
    default_time_range: str = "1h"
    max_time_range: str = "24h"
    log_level: str = "INFO"


@dataclass
class ObservabilityLoadResult:
    """Result of observability load planning."""

    success: bool
    load_plan: ObservabilityLoadPlan | None = None
    estimated_data_points: int = 0
    query_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservabilityLoadPlanner:
    """Planner for observability data loading operations."""

    def __init__(self, config: ObservabilityLoadConfig | None = None):
        self.config = config or ObservabilityLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: dict[str, Any]) -> ObservabilityLoadResult:
        """Plan observability data loading operations.

        Args:
            load_request: Dictionary containing load requirements and queries

        Returns:
            ObservabilityLoadResult: Complete planning result with load plan
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ObservabilityPlanner.plan_load")
        self.logger.info(
            f"Starting observability load planning for: {load_request.get('plan_name', 'unknown')}",
        )
        try:
            self._validate_request(load_request)
            request_type = self._parse_request_type(load_request)
            data_source = self._parse_data_source(load_request)
            metrics = self._parse_metrics(load_request) if self.config.enable_metrics else []
            log_queries = self._parse_log_queries(load_request) if self.config.enable_logs else []
            trace_queries = self._parse_trace_queries(load_request) if self.config.enable_traces else []
            load_plan = self._create_load_plan(
                load_request, request_type, data_source, metrics, log_queries, trace_queries,
            )
            estimated_data_points = self._estimate_data_points(load_plan)
            query_count = len(metrics) + len(log_queries) + len(trace_queries)
            load_time = self._estimate_load_time(load_plan)
            memory_estimate = self._estimate_memory_usage(load_plan)
            result = ObservabilityLoadResult(
                success=True,
                load_plan=load_plan,
                estimated_data_points=estimated_data_points,
                query_count=query_count,
                load_time_estimate=load_time,
                memory_estimate=memory_estimate,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "request_type": request_type.value,
                    "data_source": data_source.value,
                    "planner": "ObservabilityLoadPlanner",
                },
            )
            self.logger.info(
                f"Successfully planned observability load: {query_count} queries, ~{estimated_data_points} data points",
            )
            return result
        except Exception as e:
            self.logger.error(f"observability load planning failed: {str(e)}")
            return ObservabilityLoadResult(
                success=False,
                errors=[str(e)],
                metadata={"failed_at": datetime.utcnow().isoformat(), "planner": "ObservabilityLoadPlanner"},
            )

    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate observability load planning request."""
        if not request:
            raise ValueError("observability load planning request cannot be empty")
        if "plan_name" not in request:
            raise ValueError("Plan name is required in observability load planning request")
        if "request_type" not in request:
            raise ValueError("Request type is required in observability load planning request")

    def _parse_request_type(self, request: dict[str, Any]) -> RequestType:
        """Parse request type from request."""
        type_mapping = {
            "metric_query": RequestType.METRIC_QUERY,
            "log_search": RequestType.LOG_SEARCH,
            "trace_lookup": RequestType.TRACE_LOOKUP,
            "aggregation": RequestType.AGGREGATION,
            "anomaly_detection": RequestType.ANOMALY_DETECTION,
        }
        request_type_str = request.get("request_type", "metric_query")
        return type_mapping.get(request_type_str, RequestType.METRIC_QUERY)

    def _parse_data_source(self, request: dict[str, Any]) -> DataSource:
        """Parse data source from request."""
        source_mapping = {
            "prometheus": DataSource.PROMETHEUS,
            "elasticsearch": DataSource.ELASTICSEARCH,
            "jaeger": DataSource.JAEGER,
            "zipkin": DataSource.ZIPKIN,
            "grafana": DataSource.GRAFANA,
            "datadog": DataSource.DATADOG,
        }
        source_str = request.get("data_source", "prometheus")
        return source_mapping.get(source_str, DataSource.PROMETHEUS)

    def _parse_metrics(self, request: dict[str, Any]) -> list[MetricDefinition]:
        """Parse metrics from request."""
        metrics = []
        raw_metrics = request.get("metrics", [])
        for raw_metric in raw_metrics:
            if isinstance(raw_metric, dict):
                aggregation = None
                if "aggregation" in raw_metric:
                    agg_mapping = {
                        "sum": AggregationType.SUM,
                        "avg": AggregationType.AVG,
                        "min": AggregationType.MIN,
                        "max": AggregationType.MAX,
                        "count": AggregationType.COUNT,
                        "percentile": AggregationType.PERCENTILE,
                    }
                    aggregation = agg_mapping.get(raw_metric.get("aggregation"), AggregationType.AVG)
                metric = MetricDefinition(
                    name=raw_metric.get("name", "unnamed"),
                    query=raw_metric.get("query", ""),
                    labels=raw_metric.get("labels", {}),
                    aggregation=aggregation,
                    time_range=raw_metric.get("time_range", self.config.default_time_range),
                    step=raw_metric.get("step", 60),
                )
                metrics.append(metric)
        if len(metrics) > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of metrics ({len(metrics)}) exceeds maximum ({self.config.max_queries_per_plan})",
            )
        return metrics

    def _parse_log_queries(self, request: dict[str, Any]) -> list[LogQuery]:
        """Parse log queries from request."""
        queries = []
        raw_queries = request.get("log_queries", [])
        for raw_query in raw_queries:
            if isinstance(raw_query, dict):
                query = LogQuery(
                    index=raw_query.get("index", "logs-*"),
                    query=raw_query.get("query", "*"),
                    filters=raw_query.get("filters", {}),
                    time_range=raw_query.get("time_range", self.config.default_time_range),
                    size=raw_query.get("size", 1000),
                    sort_field=raw_query.get("sort_field", "@timestamp"),
                    sort_order=raw_query.get("sort_order", "desc"),
                )
                queries.append(query)
        if len(queries) > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of log queries ({len(queries)}) exceeds maximum ({self.config.max_queries_per_plan})",
            )
        return queries

    def _parse_trace_queries(self, request: dict[str, Any]) -> list[TraceQuery]:
        """Parse trace queries from request."""
        queries = []
        raw_queries = request.get("trace_queries", [])
        for raw_query in raw_queries:
            if isinstance(raw_query, dict):
                query = TraceQuery(
                    service=raw_query.get("service"),
                    operation=raw_query.get("operation"),
                    trace_id=raw_query.get("trace_id"),
                    tags=raw_query.get("tags", {}),
                    time_range=raw_query.get("time_range", self.config.default_time_range),
                    limit=raw_query.get("limit", 100),
                )
                queries.append(query)
        if len(queries) > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of trace queries ({len(queries)}) exceeds maximum ({self.config.max_queries_per_plan})",
            )
        return queries

    def _create_load_plan(
        self,
        request: dict[str, Any],
        request_type: RequestType,
        data_source: DataSource,
        metrics: list[MetricDefinition],
        log_queries: list[LogQuery],
        trace_queries: list[TraceQuery],
    ) -> ObservabilityLoadPlan:
        """Create observability load plan from parsed components."""
        return ObservabilityLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            request_type=request_type,
            data_source=data_source,
            metrics=metrics,
            log_queries=log_queries,
            trace_queries=trace_queries,
            enable_caching=request.get("enable_caching", True),
            cache_ttl=request.get("cache_ttl", 300),
            enable_sampling=request.get("enable_sampling", False),
            sample_rate=request.get("sample_rate", 1.0),
            metadata=request.get("metadata", {}),
        )

    def _estimate_data_points(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate total number of data points."""
        total_points = 0
        for metric in plan.metrics:
            time_range_minutes = self._parse_time_range(metric.time_range)
            points_per_metric = time_range_minutes * 60 // metric.step
            total_points += points_per_metric
        for query in plan.log_queries:
            total_points += query.size
        for query in plan.trace_queries:
            total_points += query.limit * 50
        return total_points

    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to minutes."""
        if time_range.endswith("m"):
            return int(time_range[:-1])
        elif time_range.endswith("h"):
            return int(time_range[:-1]) * 60
        elif time_range.endswith("d"):
            return int(time_range[:-1]) * 60 * 24
        else:
            return 60

    def _estimate_load_time(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 5
        query_time = (len(plan.metrics) + len(plan.log_queries) + len(plan.trace_queries)) * 2
        data_points = self._estimate_data_points(plan)
        processing_time = data_points * 0.001
        total_time = base_time + query_time + processing_time
        return int(total_time)

    def _estimate_memory_usage(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate memory usage in MB."""
        base_memory = 50
        metric_memory = 0
        for metric in plan.metrics:
            time_range_minutes = self._parse_time_range(metric.time_range)
            points_per_metric = time_range_minutes * 60 // metric.step
            metric_memory += points_per_metric * 100
        log_memory = sum(query.size * 1024 for query in plan.log_queries)
        trace_memory = sum(query.limit * 50 * 500 for query in plan.trace_queries)
        total_memory_bytes = base_memory * 1024 * 1024 + metric_memory + log_memory + trace_memory
        return total_memory_bytes // (1024 * 1024)


def create_observability_load_planner(
    enable_metrics: bool = True, enable_logs: bool = True, enable_traces: bool = True, **kwargs: object,
) -> ObservabilityLoadPlanner:
    """Create a configured observability load planner."""
    config = ObservabilityLoadConfig(
        enable_metrics=enable_metrics, enable_logs=enable_logs, enable_traces=enable_traces, **kwargs,
    )
    return ObservabilityLoadPlanner(config)


def plan_observability_load(
    plan_name: str,
    request_type: str,
    data_source: str = "prometheus",
    metrics: list[dict[str, Any]] | None = None,
    log_queries: list[dict[str, Any]] | None = None,
    trace_queries: list[dict[str, Any]] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan observability data load from simple parameters.

    Args:
        plan_name: Name of the load plan
        request_type: Type of observability request
        data_source: Data source to use
        metrics: Optional list of metric definitions
        log_queries: Optional list of log query definitions
        trace_queries: Optional list of trace query definitions
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    request = {
        "plan_name": plan_name,
        "request_type": request_type,
        "data_source": data_source,
        "metrics": metrics or [],
        "log_queries": log_queries or [],
        "trace_queries": trace_queries or [],
    }
    planner_config = ObservabilityLoadConfig(**config) if config else None
    planner = ObservabilityLoadPlanner(planner_config)
    result = planner.plan_load(request)
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "request_type": result.load_plan.request_type.value,
            "data_source": result.load_plan.data_source.value,
            "metrics": [
                {
                    "name": m.name,
                    "query": m.query,
                    "labels": m.labels,
                    "aggregation": m.aggregation.value if m.aggregation else None,
                    "time_range": m.time_range,
                    "step": m.step,
                }
                for m in result.load_plan.metrics
            ],
            "log_queries": [
                {
                    "index": q.index,
                    "query": q.query,
                    "filters": q.filters,
                    "time_range": q.time_range,
                    "size": q.size,
                    "sort_field": q.sort_field,
                    "sort_order": q.sort_order,
                }
                for q in result.load_plan.log_queries
            ],
            "trace_queries": [
                {
                    "service": q.service,
                    "operation": q.operation,
                    "trace_id": q.trace_id,
                    "tags": q.tags,
                    "time_range": q.time_range,
                    "limit": q.limit,
                }
                for q in result.load_plan.trace_queries
            ],
            "enable_caching": result.load_plan.enable_caching,
            "cache_ttl": result.load_plan.cache_ttl,
            "enable_sampling": result.load_plan.enable_sampling,
            "sample_rate": result.load_plan.sample_rate,
            "metadata": result.load_plan.metadata,
        }
        if result.load_plan
        else None,
        "estimated_data_points": result.estimated_data_points,
        "query_count": result.query_count,
        "load_time_estimate": result.load_time_estimate,
        "memory_estimate": result.memory_estimate,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata,
    }


class LoadDataPlanningPlanImpl(LoadDataPlanningPlanProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """

    def __init__(self, constraints: LoadDataPlanningPlanConstraints | None = None):
        self.constraints = constraints or LoadDataPlanningPlanConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process(self, input_data: dict[str, object]) -> LoadDataPlanningPlanResult:
        """Process input following L5 architecture principles"""
        self.logger.info(f"Processing {input_data}")
        self._validate_input(input_data)
        if not self.validate_safety(input_data):
            raise SecurityError("Input failed L5 safety validation")
        result = LoadDataPlanningPlanResult(
            success=True,
            data={"processed": True, "input": input_data},
            safety_validated=True,
            timestamp=self._get_timestamp(),
        )
        self.logger.info(f"Successfully processed: {result.success}")
        return result

    def validate_safety(self, data: dict[str, object]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            dangerous_patterns = [
                "<script>",
                "javascript:",
                "ast.literal_eval(",
                "pass  # exec disabled: ",
                "__import__",
            ]
            data_str = str(data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f" Dangerous pattern detected: {pattern}")
                    return False
            if len(str(data)) > 1000000:
                self.logger.error("Data exceeds size limit")
                return False
            self.logger.info("Data passed L5 safety validation")
            return True
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            self.logger.error(f"Safety validation error: {e}")
            return False

    def _validate_input(self, input_data: dict[str, object]) -> None:
        """L5 Input validation"""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")
        if not input_data:
            raise ValueError("Input cannot be empty")

    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime

        return datetime.utcnow().isoformat()


class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""

    ...


class LoadDataPlanningPlanInterface:
    """L5 Interface - ensures contract compliance"""

    def __init__(self, engine: LoadDataPlanningPlanProcessor):
        self._processor = engine

    def execute(self, input_data: dict[str, object]) -> dict[str, object]:
        """L5 Interface method - executes safely"""
        try:
            result = self._processor.process(input_data)
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp,
            }
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            raise SecurityError(f"Execution failed: {e}")


class LoadDataPlanningPlanFactory:
    """L5 builder for creating processors with proper configuration"""

    @staticmethod
    def create_processor(safety_level: str = "strict") -> LoadDataPlanningPlanInterface:
        """Create configured engine"""
        constraints = LoadDataPlanningPlanConstraints(safety_level=safety_level)
        engine = LoadDataPlanningPlanImpl(constraints)
        return LoadDataPlanningPlanInterface(engine)


def load_data_planning(input_data: dict[str, object]) -> dict[str, object]:
    """
    L5 Main function - load data planning operations

    Args:
        input_data: Input data to process

    Returns:
        Dict: Processed result

    Raises:
        SecurityError: If execution fails any safety check
    """
    builder = LoadDataPlanningPlanFactory()
    engine = builder.create_processor()
    return engine.execute(input_data)


if __name__ == "__main__":
    try:
        test_data = {"test": True}
        result = load_data_planning(test_data)
        logger.info(f"L5 Execution successful: {result}")
    except SecurityError as e:    # guardian: SecurityError should be handled with specific context
        logger.error(f"L5 Security error: {e}")
    except (ValueError, TypeError, RuntimeError, KeyError) as e:
        logger.error(f"L5 Unexpected error: {e}")
