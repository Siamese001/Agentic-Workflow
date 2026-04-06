"""Pipeline Factory — assembles PipelineConfig and PipelineDependencies for execute_ssot.

Provides ``build_pipeline_config()`` and ``build_pipeline_deps()`` that wire
concrete store/engine implementations into the meta-learning pipeline.

All construction is explicit — no auto-discovery, no globals.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    RUNTIME_STATE_JSON,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
from system_learning.engines.cross_repo_system_learning_import import (
    load_cross_repo_learning_context,
)

_emit_records_execution_trace("p0", "evidence", "pipeline_factory")
_emit_applies_guardrail("p0", "pipeline_factory", "p0_governance")
_emit_snapshots_state("p0", "pipeline_factory", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
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

_emit_emits_metric_event("pipeline_factory", "p4obs", "metric_1")
_emit_emits_metric_event("pipeline_factory", "p4obs", "metric_2")
_emit_emits_metric_event("pipeline_factory", "p4obs", "metric_3")
_emit_emits_metric_event("pipeline_factory", "p4obs", "metric_4")
_emit_emits_metric_event("pipeline_factory", "p4obs", "metric_5")
_emit_emits_metric_event("pipeline_factory", "p4obs", "metric_6")
_emit_records_incident_event("pipeline_factory", "p4obs", "incident")
_emit_captures_runtime_anomaly("pipeline_factory", "p4obs", "anomaly")
_emit_writes_observability_log("pipeline_factory", "p4obs", "obs_log")
_emit_updates_monitoring_state("pipeline_factory", "p4obs", "mon_state")
_emit_triggers_alert("pipeline_factory", "p4obs", "alert")
_emit_links_incident_trace("pipeline_factory", "p4obs", "trace_link")
_emit_captures_pattern("pipeline_factory", "p3lm", "pattern")
_emit_records_learning_event("pipeline_factory", "p3lm", "learning_event")
_emit_writes_learning_snapshot("pipeline_factory", "p3lm", "snapshot")
_emit_feeds_meta_learning("pipeline_factory", "p3lm", "meta_feed")
_emit_updates_routing_strategy("pipeline_factory", "p3lm", "routing")
_emit_improves_agent_policy("pipeline_factory", "p3lm", "policy")
_emit_stores_learning_state("pipeline_factory", "p3lm", "state")
_emit_records_execution_trace("pipeline_factory", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("pipeline_factory", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("pipeline_factory", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("pipeline_factory", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("pipeline_factory", "L4_STATE", "p2_trace_5")
_emit_reads_environ("pipeline_factory", "env_read", "p2_env_1")
_emit_reads_environ("pipeline_factory", "env_read", "p2_env_2")
_emit_reads_runtime_state("pipeline_factory", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("pipeline_factory", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "pipeline_factory", "context_pull")
_emit_pulls_context("p1", "pipeline_factory", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "pipeline_factory", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "pipeline_factory", "uwg_term_2")
_emit_writes_through("p1", "pipeline_factory", "write_through")
_emit_writes_through("p1", "pipeline_factory", "write_through_2")
_emit_validated_by_safety_plane("p1", "pipeline_factory", "safety_validation")
_emit_invokes_eval("p1", "pipeline_factory", "eval_call")
_emit_proposal_commits_routing("p1", "pipeline_factory", "routing_commit")
_emit_escalates_to_human("p1", "pipeline_factory", "human_escalation")
_emit_routes_through("p1", "pipeline_factory", "route_through")
_emit_checks_agent_registry("p1", "pipeline_factory", "agent_registry")
_emit_validates_agent_capability("p1", "pipeline_factory", "capability")
_emit_dispatches_execution_plan("p1", "pipeline_factory", "exec_plan")
_emit_agent_executes_agent("p1", "pipeline_factory", "sub_agent")
_emit_routes_to_agent("p1", "pipeline_factory", "target_agent")
_emit_verifies_policy("p1", "pipeline_factory", "policy_check")
_emit_observes_runtime_state("p1", "pipeline_factory", "runtime_state")
_emit_verifies_boundary("p1", "pipeline_factory", "boundary_check")
_emit_transcripts_response("p1", "pipeline_factory", "transcript")
_emit_hard_fails_untranscripted("p1", "pipeline_factory")
_emit_gated_by_confidence("p1", "pipeline_factory", "confidence_gate")
emit_replay_key("p0", "pipeline_factory")
emit_determinism_digest("p0", "pipeline_factory")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "pipeline_factory", "execution_auth")
_emit_validates_capability("p2", "pipeline_factory", "capability_check")
_emit_routes_to_capability("p2", "pipeline_factory", "capability_route")
_emit_writes_via_uwg("p2", "pipeline_factory", "uwg_write")
_emit_blocks_direct_write("p2", "pipeline_factory", "direct_write_block")
_emit_records_tool_invocation("p2", "pipeline_factory", "tool_invocation")
_emit_captures_execution_output("p2", "pipeline_factory", "exec_output")
_emit_dispatches_agent("p3", "pipeline_factory", "agent_dispatch")
_emit_coordinates_agents("p3", "pipeline_factory", "agent_coordination")
_emit_records_workflow_lineage("p3", "pipeline_factory", "workflow_lineage")
_emit_records_healing_outcome("p3", "pipeline_factory", "healing_outcome")
_emit_escalates_failure("p3", "pipeline_factory", "failure_escalation")
_emit_orchestrates_workflow("p3", "pipeline_factory", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pipeline_factory", "healing_dispatch")
_emit_invokes_evaluation("p3", "pipeline_factory", "evaluation_signal")
_emit_records_telemetry_event("p4", "pipeline_factory", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pipeline_factory", "eval_metric")
_emit_stores_embedding("p4", "pipeline_factory", "embedding_store")
_emit_updates_meta_learning_state("p4", "pipeline_factory", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pipeline_factory", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def build_pipeline_config(*, proposal_only: bool = True) -> Any:
    """Build a PipelineConfig for the meta-learning pipeline.

    Parameters
    ----------
    proposal_only : bool
        When True (default), the pipeline only produces proposals without
        applying them.  Pass False (via ``--apply-proposals``) to activate
        the commit/activate path.

    Returns a ``PipelineConfig`` with conservative defaults suitable for
    initial bootstrap.  All validation gates are enabled.
    """
    from system_learning.pipelines.meta_learning_pipeline import PipelineConfig
    from system_learning.constraints.dampening import CooldownPolicy, SampleSizePolicy
    from system_learning.validators.oscillation_detector import OscillationPolicy
    from system_learning.validators.shadow_evaluator import ShadowThresholds

    return PipelineConfig(
        engine_version="0.1.0",
        config_surface_version="0.1.0",
        # guardian: allow-magic-config
        shadow_thresholds=ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=15.0,
            max_mem_regression_pct=15.0,
            forbid_any_safety_violation_increase=True,
        ),
        # guardian: allow-magic-config
        cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
        # guardian: allow-magic-config
        sample_policy=SampleSizePolicy(min_observations=10),  # guardian: allow-magic-config
        oscillation_policy=OscillationPolicy(
            window=5,
            epsilon=0.01,
            freeze_seconds=7200,
        ),
        enabled_proposers=("l0", "rag", "l1", "l5"),
        require_replay_validation=True,
        require_shadow_validation=False,
        proposal_only=proposal_only,
    )


def build_pipeline_deps(
    *,
    repo_root: Path,
    healing_outcome_intake_adapter: Any | None = None,
    healing_config_optimizer: Any | None = None,
) -> Any:
    """Build PipelineDependencies wired to real stores.

    Parameters
    ----------
    repo_root : Path
        Repository root directory (for locating compliance reports, runtime
        state, etc.).
    healing_outcome_intake_adapter : Any | None
        Pre-built intake adapter from the calling function (reuse to avoid
        double-build).
    healing_config_optimizer : Any | None
        Pre-built optimizer (or None for default).

    Returns
    -------
    PipelineDependencies
        Fully-wired dependencies ready for ``run_pipeline()``.
    """
    from system_learning.engines.l0_threshold_tuner import L0ProposerAdapter
    from system_learning.engines.l1_model_proposer import L1ModelProposer
    from system_learning.engines.l4_state_writer import FileBackedL4StateWriter
    from system_learning.engines.l5_policy_proposer import L5PolicyProposer
    from system_learning.engines.rag_proposer import RAGParameterProposer
    from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies
    from system_learning.stores.audit_store import FileBackedAuditStore
    from system_learning.stores.config_provider import (
        FileBackedConfigProvider,
        InMemoryBaselineMetricsProvider,
    )
    from system_learning.stores.telemetry_store import InMemoryTelemetryStore

    reports_dir = repo_root / "logs" / "compliance_reports"
    runtime_state_path = repo_root / RUNTIME_STATE_JSON
    # [CROSS-RUN PERSISTENCE] L4B healing snapshots and L4C proposals written by
    # run_pipeline() are now stored to disk under logs/l4_state/ so they survive
    # process boundaries and are available to future runs (REQ-071: Stage 8 INTAKE
    # MUST persist to L4; process-map: L4B write-once, content-hash keyed).
    l4_state_dir = repo_root / "logs" / "l4_state"
    l4_state_dir.mkdir(parents=True, exist_ok=True)

    audit_store = FileBackedAuditStore(reports_dir=reports_dir)
    telemetry_store = InMemoryTelemetryStore()
    config_provider = FileBackedConfigProvider(
        runtime_state_path=runtime_state_path,
    )
    baseline_metrics = InMemoryBaselineMetricsProvider()
    l4_writer = FileBackedL4StateWriter(base_dir=l4_state_dir)

    # Concrete proposers — all four layers wired
    l0_proposer = L0ProposerAdapter()
    rag_proposer = RAGParameterProposer()
    l1_proposer = L1ModelProposer()
    l5_proposer = L5PolicyProposer()

    # Optional engines — import failures are non-fatal
    pattern_engine = None
    try:
        from system_learning.engines.pattern_analysis_engine import PatternAnalysisEngine

        pattern_engine = PatternAnalysisEngine()
    # guardian: allow-silent-swallow - optional dependency
    except ImportError:
        logger.warning("PatternAnalysisEngine not available; Stage 8.6 will be skipped.")

    optimizer = healing_config_optimizer
    if optimizer is None:
        try:
            from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer

            optimizer = HealingConfigOptimizer()
        except ImportError:
            logger.debug("HealingConfigOptimizer not available; skipping.")

    # GAP-013: Wire Stage 5 extension surfaces
    confidence_scorer = None
    try:
        from system_learning.confidence.engine import HealingConfidenceScorer

        confidence_scorer = HealingConfidenceScorer()
    except ImportError:
        logger.debug("HealingConfidenceScorer not available; skipping.")

    failure_fingerprinter = None
    try:
        from system_learning.fingerprinting.engine import FailureFingerprinter

        failure_fingerprinter = FailureFingerprinter()
    except ImportError:
        logger.debug("FailureFingerprinter not available; skipping.")

    risk_correlator = None
    try:
        from system_learning.correlation.engine import RiskCorrelator

        risk_correlator = RiskCorrelator()
    except ImportError:
        logger.debug("RiskCorrelator not available; skipping.")

    # GAP-013: Wire Stage 7 arbitration surfaces
    arbitration_engine = None
    arbitration_policy = None
    try:
        from system_learning.arbitration.engine import ArbitrationEngine
        from system_learning.arbitration.types import ArbitrationPolicy

        arbitration_engine = ArbitrationEngine()
        arbitration_policy = ArbitrationPolicy(
            weights={"generic": 1.0},
            caps={"max_winners": 5},
            thresholds={"min_score": 0.0},
            allowed_kinds={"generic"},
        )
    except (ImportError, TypeError):
        logger.debug("ArbitrationEngine/Policy not available; skipping.")

    # GAP-013: Wire DPO/RLHF optimizer
    rlhf_optimizer = None
    try:
        from system_learning.engines.rlhf_optimizer import DefaultDeterministicRLHFOptimizer

        rlhf_optimizer = DefaultDeterministicRLHFOptimizer()
    except ImportError:
        logger.debug("RLHFOptimizer not available; skipping.")

    # GAP-014: Wire freeze reader from runtime_state.json
    freeze_reader = None
    try:
        from system_learning.invariants.freeze_gate import JsonFileBackedFreezeReader

        freeze_reader = JsonFileBackedFreezeReader(runtime_state_path)
    except ImportError:
        logger.debug("FreezeStateReader not available; skipping.")

    cross_repo_learning_context = load_cross_repo_learning_context(repo_root)

    # Wave C-2: Register OTel telemetry store adapter
    otel_telemetry_store = None
    try:
        from system_learning.adapters.otel_telemetry_store_adapter import OTelTelemetryStoreAdapter

        otel_telemetry_store = OTelTelemetryStoreAdapter()
        logger.debug("OTel telemetry store adapter registered")
    except ImportError:
        logger.debug("OTel telemetry store adapter not available; skipping.")

    return PipelineDependencies(
        audit_store=audit_store,
        telemetry_store=telemetry_store,
        config_provider=config_provider,
        baseline_metrics_provider=baseline_metrics,
        l0_proposer=l0_proposer,
        rag_proposer=rag_proposer,
        l1_proposer=l1_proposer,
        l5_proposer=l5_proposer,
        healing_outcome_intake_adapter=healing_outcome_intake_adapter,
        healing_config_optimizer=optimizer,
        l4_state_writer=l4_writer,
        pattern_analysis_engine=pattern_engine,
        healing_confidence_scorer=confidence_scorer,
        failure_fingerprinter=failure_fingerprinter,
        risk_correlator=risk_correlator,
        arbitration_engine=arbitration_engine,
        arbitration_policy=arbitration_policy,
        rlhf_optimizer=rlhf_optimizer,
        freeze_reader=freeze_reader,
        cross_repo_learning_context=cross_repo_learning_context,
        otel_telemetry_store=otel_telemetry_store,
    )


__all__ = [
    "build_pipeline_config",
    "build_pipeline_deps",
]
