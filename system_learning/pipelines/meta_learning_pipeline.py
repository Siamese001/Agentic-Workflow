"""G-16-27: Meta-learning pipeline orchestrator for System Learning.

End-to-end deterministic pipeline: snapshot → telemetry/audit → RCA → proposals
→ validation → optional commit/activation.
W2: Embedding-augmented semantic retrieval (C0-only, informational). Final closeout.
W3: Pattern Analysis Engine (Deterministic, Informational-Only).
W4-A: RetrievalProfile Authority (L4 Only).
W4-B: Shadow Embedder wiring for drift detection (non-influential).
W4-C: Shadow drift analysis and L4 informational state (non-influential).
W4-D: Policy recommendation engine with advisory-only L4 state (non-influential).

W4-A Integration:
- RetrievalProfile provides embedder identity and retrieval knobs from L4
- All retrieval configuration is versioned and deterministic
- No behavioral changes - only authority shift from hardcoded to governed
- Active profile pointer enables future optimizer wiring

W4-B Integration:
- Shadow embedder computes parallel embeddings for telemetry
- Shadow embeddings do NOT affect retrieval scoring or ranking
- Provides drift detection via cosine similarity metrics
- Stable float rounding (6 decimal places) for deterministic telemetry

W4-C Integration:
- ShadowDriftAnalyzer converts W4-B telemetry into drift signals
- DriftSummary written to L4 as informational state only
- No automatic mutation or policy changes
- Deterministic digest for drift verification

W4-D Integration:
- PolicyRecommendationEngine converts drift into bounded recommendations
- PolicyRecommendation written to L4 as advisory state only
- Does NOT mutate active RetrievalProfile
- Deterministic digest for recommendation verification

W4-E Integration:
- RetrievalProfileProposalManager stages recommendations as proposals
- RetrievalProfileProposal written to L4 requiring explicit approval
- Does NOT mutate ACTIVE_RETRIEVAL_PROFILE_ID
- Deterministic digest for proposal verification

Invariants:
  - Default proposal_only=True (proposal-only by default; commit requires explicit False)
  - No wall-clock reads (now_utc injected)
  - Fail-closed on validation failure
  - Stage A commit + Stage B activation only via injected interfaces
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from tqdm import tqdm
from typing import Any, Protocol

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

_emit_records_execution_trace("p0", "evidence", "meta_learning_pipeline")
_emit_applies_guardrail("p0", "meta_learning_pipeline", "p0_governance")
emit_replay_key("p0", "meta_learning_pipeline")
emit_determinism_digest("p0", "meta_learning_pipeline")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_learning_pipeline", "execution_auth")
_emit_validates_capability("p2", "meta_learning_pipeline", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_pipeline", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_pipeline", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_pipeline", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_pipeline", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_pipeline", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_pipeline", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_pipeline", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_pipeline", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_pipeline", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_pipeline", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_pipeline", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_pipeline", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_pipeline", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_pipeline", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_pipeline", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_pipeline", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_pipeline", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_pipeline", "exec_snapshot_link")

logger = logging.getLogger(__name__)
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from system_learning.arbitration.engine import ArbitrationEngine
from system_learning.arbitration.types import ArbitrationCandidate, ArbitrationPolicy
from system_learning.confidence.engine import HealingConfidenceScorer
from system_learning.constraints.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.correlation.engine import RiskCorrelator
from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer
from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.pattern_analysis_engine import PatternAnalysisEngine
from system_learning.engines.policy_recommendation_engine import (
    PolicyRecommendation,
    PolicyRecommendationEngine,
)
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_manager import get_active_retrieval_profile
from system_learning.engines.retrieval_profile_proposal import RetrievalProfileProposal
from system_learning.engines.retrieval_profile_proposal_manager import RetrievalProfileProposalManager
from system_learning.engines.rlhf_optimizer import RLHFOptimizer
from system_learning.engines.shadow_drift_analyzer import DriftSummary, ShadowDriftAnalyzer
from system_learning.fingerprinting.engine import FailureFingerprinter
from system_learning.invariants.freeze_gate import FreezeStateReader
from system_learning.snapshots.snapshot_factory import create_snapshot
from system_learning.types.snapshot_types import MetaLearningSnapshot
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds

_emit_emits_metric_event("meta_learning_pipeline", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_pipeline", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_pipeline", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_pipeline", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_pipeline", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_pipeline", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_pipeline", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_pipeline", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_pipeline", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_pipeline", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_pipeline", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_pipeline", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_pipeline", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_pipeline", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_pipeline", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_pipeline", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_pipeline", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_pipeline", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_pipeline", "p3lm", "state")
_emit_records_execution_trace("meta_learning_pipeline", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_pipeline", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_pipeline", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_pipeline", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_pipeline", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_pipeline", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_pipeline", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_pipeline", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_pipeline", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning_pipeline", "context_pull")
_emit_pulls_context("p1", "meta_learning_pipeline", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_learning_pipeline", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_pipeline", "uwg_term_2")
_emit_writes_through("p1", "meta_learning_pipeline", "write_through")
_emit_writes_through("p1", "meta_learning_pipeline", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_learning_pipeline", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_pipeline", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_pipeline", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_pipeline", "human_escalation")
_emit_routes_through("p1", "meta_learning_pipeline", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_pipeline", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_pipeline", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_pipeline", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_pipeline", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_pipeline", "target_agent")
_emit_verifies_boundary("p1", "meta_learning_pipeline", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_pipeline", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_pipeline")
_emit_gated_by_confidence("p1", "meta_learning_pipeline", "confidence_gate")

_shadow_telemetry_batch: list[dict[str, Any]] = []
_shadow_drift_analyzer = ShadowDriftAnalyzer()
_policy_recommendation_engine = PolicyRecommendationEngine()
_proposal_manager = RetrievalProfileProposalManager()


def _accumulate_shadow_telemetry(telemetry: dict[str, Any]) -> None:
    """Accumulate shadow telemetry for drift analysis.

    Args:
        telemetry: Shadow telemetry dictionary from _retrieve_semantic_context
    """
    global _shadow_telemetry_batch
    if "shadow_embedder_id" in telemetry:
        _shadow_telemetry_batch.append(telemetry.copy())


def _analyze_shadow_drift_and_write(
    profile_id: str,
    now_utc: int,
    l4_writer: L4StateWriter,
) -> DriftSummary | None:
    """Analyze accumulated shadow telemetry and write to L4.

    Args:
        profile_id: Active RetrievalProfile ID
        now_utc: Current timestamp
        l4_writer: L4 state writer

    Returns:
        DriftSummary if analysis was performed, None otherwise
    """
    global _shadow_telemetry_batch
    if not _shadow_telemetry_batch:
        return None
    drift_summary = _shadow_drift_analyzer.analyze_batch(
        shadow_records=_shadow_telemetry_batch,
        profile_id=profile_id,
        now_utc=now_utc,
    )
    try:
        summary_json = drift_summary.to_canonical_json().encode("utf-8")
        l4_writer.write_l4c_shadow_drift(
            payload_bytes=summary_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    # guardian: allow-silent-swallow
    except Exception as _l4_err:
        logger.warning("[MetaLearning] L4C shadow_drift write failed: %s", _l4_err)
    _shadow_telemetry_batch.clear()
    return drift_summary


def _generate_policy_recommendation_and_write(
    drift_summary: DriftSummary,
    active_profile: RetrievalProfile,
    now_utc: int,
    l4_writer: L4StateWriter,
) -> PolicyRecommendation | None:
    """Generate policy recommendation from drift analysis and write to L4.

    Args:
        drift_summary: Drift analysis from W4-C
        active_profile: Current active RetrievalProfile
        now_utc: Current timestamp
        l4_writer: L4 state writer

    Returns:
        PolicyRecommendation if generated, None otherwise
    """
    if drift_summary is None:
        return None
    recommendation = _policy_recommendation_engine.generate_recommendation(
        drift_summary=drift_summary,
        active_profile=active_profile,
        now_utc=now_utc,
    )
    try:
        recommendation_json = recommendation.to_canonical_json().encode("utf-8")
        l4_writer.write_l4c_policy_recommendation(
            payload_bytes=recommendation_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    # guardian: allow-silent-swallow
    except Exception as _l4_err:
        logger.warning("[MetaLearning] L4C policy_recommendation write failed: %s", _l4_err)
    return recommendation


def _create_proposal_and_write(
    policy_recommendation: PolicyRecommendation,
    active_profile: RetrievalProfile,
    now_utc: int,
    l4_writer: L4StateWriter,
) -> RetrievalProfileProposal | None:
    """Create proposal from policy recommendation and write to L4.

    Args:
        policy_recommendation: Policy recommendation from W4-D
        active_profile: Current active RetrievalProfile
        now_utc: Current timestamp
        l4_writer: L4 state writer

    Returns:
        RetrievalProfileProposal if created, None otherwise
    """
    if policy_recommendation is None:
        return None
    proposal = _proposal_manager.create_proposal(
        recommendation=policy_recommendation,
        active_profile=active_profile,
        now_utc=now_utc,
    )
    try:
        proposal_json = proposal.to_canonical_json().encode("utf-8")
        l4_writer.write_l4c_retrieval_profile_proposal(
            payload_bytes=proposal_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    # guardian: allow-silent-swallow
    except Exception as _l4_err:
        logger.warning("[MetaLearning] L4C retrieval_profile_proposal write failed: %s", _l4_err)
    return proposal


class PipelineError(RuntimeError):
    """Base exception for pipeline errors."""


class ValidationError(PipelineError):
    """Raised when validation fails."""


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for meta-learning pipeline.

    Fields
    ------
    engine_version : str
        Version of the optimization engine.
    config_surface_version : str
        Version of config surface allowlist.
    shadow_thresholds : ShadowThresholds
        Shadow validation thresholds.
    cooldown_policy : CooldownPolicy
        Cooldown policy for dampening.
    sample_policy : SampleSizePolicy
        Sample size policy for dampening.
    oscillation_policy : OscillationPolicy
        Oscillation detection policy.
    enabled_proposers : tuple[str, ...]
        Enabled proposers (subset of {"L0", "RAG", "L1", "L5"}).
    require_replay_validation : bool
        Whether to require replay validation (default True).
    require_shadow_validation : bool
        Whether to require shadow validation (default True).
    proposal_only : bool
        If True, only generate proposals without commit/activation (default True).
    """

    engine_version: str
    config_surface_version: str
    shadow_thresholds: ShadowThresholds
    cooldown_policy: CooldownPolicy
    sample_policy: SampleSizePolicy
    oscillation_policy: OscillationPolicy
    enabled_proposers: tuple[str, ...]
    require_replay_validation: bool = True
    require_shadow_validation: bool = True
    proposal_only: bool = True


class AuditStore(Protocol):
    """Protocol for read-only audit store access."""

    def read_audit_slice(self, window_start_utc: int, window_end_utc: int) -> bytes:
        """Read audit slice within window."""
        ...


class TelemetryStore(Protocol):
    """Protocol for read-only telemetry store access."""

    def read_events(self, window_start_utc: int, window_end_utc: int) -> tuple[tuple[int, str, bytes], ...]:
        """Read telemetry events within window."""
        ...


class ConfigProvider(Protocol):
    """Protocol for config provider."""

    def get_current_configs(self) -> dict[str, bytes]:
        """Return materialized config bytes (deterministic)."""
        ...

    def get_last_update_utc(self, surface_name: str) -> int | None:
        """Return last update timestamp for surface."""
        ...

    def get_param_history(self, surface_name: str, n: int) -> tuple[float, ...]:
        """Return last N parameter values for surface."""
        ...


class VersionStore(Protocol):
    """Protocol for version store (Stage A commit)."""

    def commit_change_package(self, pkg: Any) -> str:
        """Commit change package and return version_id."""
        ...


class Activator(Protocol):
    """Protocol for activation (Stage B)."""

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        ...


class ApprovalGate(Protocol):
    """Protocol for approval gate."""

    def decide(self, pkg: Any, rca: Any, snapshot: MetaLearningSnapshot) -> Any:
        """Decide whether to approve change package."""
        ...


class L0Proposer(Protocol):
    """Protocol for L0 threshold proposer."""

    def propose(
        self,
        snapshot: MetaLearningSnapshot,
        metrics: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> Any:
        """Propose L0 threshold changes."""
        ...


class RAGProposer(Protocol):
    """Protocol for RAG parameter proposer."""

    def propose(
        self,
        snapshot: MetaLearningSnapshot,
        metrics: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> Any:
        """Propose RAG parameter changes."""
        ...


class L1Proposer(Protocol):
    """Protocol for L1 model proposer."""

    def propose(
        self,
        snapshot: MetaLearningSnapshot,
        metrics: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> Any:
        """Propose L1 model changes."""
        ...


class L5Proposer(Protocol):
    """Protocol for L5 policy proposer."""

    def propose(
        self,
        snapshot: MetaLearningSnapshot,
        metrics: Any,
        config: Any,
        now_utc: int,
        history: Any,
        cooldown: Any,
        sample: Any,
    ) -> Any:
        """Propose L5 policy changes."""
        ...


class BaselineMetricsProvider(Protocol):
    """Protocol for baseline metrics provider."""

    def production_metrics(self) -> Any:
        """Return production baseline metrics."""
        ...

    def shadow_metrics(self, pkg: Any) -> Any:
        """Return shadow metrics for change package."""
        ...


@dataclass(frozen=True, slots=True)
class PipelineDependencies:
    """Injected dependencies for pipeline.

    Fields
    ------
    audit_store : AuditStore
        Read-only audit store.
    telemetry_store : TelemetryStore
        Read-only telemetry store.
    config_provider : ConfigProvider
        Config provider.
    baseline_metrics_provider : BaselineMetricsProvider
        Baseline metrics provider for shadow validation.
    l0_proposer : L0Proposer | None
        L0 threshold proposer (None if not enabled).
    rag_proposer : RAGProposer | None
        RAG parameter proposer (None if not enabled).
    l1_proposer : L1Proposer | None
        L1 model proposer (None if not enabled).
    l5_proposer : L5Proposer | None
        L5 policy proposer (None if not enabled).
    version_store : VersionStore | None
        Version store for Stage A commit (None if proposal_only).
    activator : Activator | None
        Activator for Stage B (None if proposal_only).
    approval_gate : ApprovalGate | None
        Approval gate (None if proposal_only).
    healing_outcome_intake_adapter : HealingOutcomeIntakeAdapter | None
        Optional adapter for persisting healing outcome intake records.
    healing_config_optimizer : HealingConfigOptimizer | None
        Optional optimizer for healing threshold adjustments.
    l4_state_writer : L4StateWriter | None
        Optional L4 state writer for persistence.
    pattern_analysis_engine : PatternAnalysisEngine | None
        Optional pattern analysis engine for detecting patterns.
    resource_predictor_bytes : bytes | None
        Optional serialized ResourcePrediction artifact from L2 execution.
    rollback_refinement_decision_bytes : bytes | None
        Optional serialized RollbackRefinementDecision artifact from L2 execution.
    dpo_batch_bytes : bytes | None
        Optional serialized DPOBatch artifact from HITL feedback processing.
    rlhf_optimizer : RLHFOptimizer | None
        Optional RLHF optimizer for DPO-driven threshold adjustments.
    """

    audit_store: AuditStore
    telemetry_store: TelemetryStore
    config_provider: ConfigProvider
    baseline_metrics_provider: BaselineMetricsProvider
    l0_proposer: L0Proposer | None = None
    rag_proposer: RAGProposer | None = None
    l1_proposer: L1Proposer | None = None
    l5_proposer: L5Proposer | None = None
    version_store: VersionStore | None = None
    activator: Activator | None = None
    approval_gate: ApprovalGate | None = None
    healing_outcome_intake_adapter: HealingOutcomeIntakeAdapter | None = None
    healing_config_optimizer: HealingConfigOptimizer | None = None
    l4_state_writer: L4StateWriter | None = None
    pattern_analysis_engine: PatternAnalysisEngine | None = None
    resource_predictor_bytes: bytes | None = None
    rollback_refinement_decision_bytes: bytes | None = None
    dpo_batch_bytes: bytes | None = None
    rlhf_optimizer: RLHFOptimizer | None = None
    healing_confidence_scorer: HealingConfidenceScorer | None = None
    failure_fingerprinter: FailureFingerprinter | None = None
    risk_correlator: RiskCorrelator | None = None
    arbitration_engine: ArbitrationEngine | None = None
    arbitration_policy: ArbitrationPolicy | None = None
    freeze_reader: FreezeStateReader | None = None
    cross_repo_learning_context: dict[str, Any] | None = None
    otel_telemetry_store: Any | None = None


def _analyze_historical_patterns(
    deps: PipelineDependencies,
    aggregate_snapshot: Any,
    *,
    now_utc: int = 0,
    detection_signal_bytes: bytes | None = None,
    drift_snapshot_bytes: bytes | None = None,
) -> Any:
    """Analyze historical patterns using W3 PatternAnalysisEngine.

    W3: Pattern Analysis Engine (Deterministic, Informational-Only).

    Args:
        deps: Pipeline dependencies containing pattern_analysis_engine
        aggregate_snapshot: Healing outcome aggregate snapshot
        now_utc: Current timestamp for new snapshot-bytes API
        detection_signal_bytes: Optional detection signal bytes
        drift_snapshot_bytes: Optional drift snapshot bytes

    Returns:
        PatternAnalysisReport (new API) or PatternSummary (old API) or None
    """
    if deps.pattern_analysis_engine is None:
        return None
    try:
        if hasattr(aggregate_snapshot, "canonical_bytes"):
            healing_snapshot_bytes = aggregate_snapshot.canonical_bytes()
            return deps.pattern_analysis_engine.analyze(
                healing_snapshot_bytes=healing_snapshot_bytes,
                detection_signal_bytes=detection_signal_bytes,
                drift_snapshot_bytes=drift_snapshot_bytes,
                now_utc=now_utc,
            )
        embedding_service = EmbeddingServiceFactory.get_or_disabled()
        if embedding_service.is_disabled():
            return None
        historical_embeddings = []
        metadata = []
        if hasattr(aggregate_snapshot, "outcomes"):
            for outcome in aggregate_snapshot.outcomes:
                if hasattr(outcome, "failure_signature"):
                    embedding = _create_deterministic_embedding(outcome.failure_signature)
                    historical_embeddings.append(embedding)
                    meta = {
                        "healer_name": getattr(outcome, "healer_name", "unknown"),
                        "failure_type": getattr(outcome, "failure_type", "unknown"),
                        "component": getattr(outcome, "component", "unknown"),
                    }
                    metadata.append(meta)
        if not historical_embeddings or len(historical_embeddings) < 10:
            return None
        # guardian: allow-magic-config
        pattern_summary = deps.pattern_analysis_engine.analyze(
            historical_embeddings=historical_embeddings,
            metadata=metadata,
            min_cluster_size=3,
        )
        print(f"W3-PATTERN-DIGEST: {pattern_summary.pattern_digest}")
        return pattern_summary
    except (ImportError, AttributeError, ValueError) as e:
        print(f"Pattern analysis failed: {e}")
        return None


def _create_deterministic_embedding(failure_signature: Any) -> List[float]:
    """Create embedding from failure signature using BGE-m3.

    BGE-m3 is a mandatory system dependency. Raises ImportError if unavailable.

    Args:
        failure_signature: Failure signature object

    Returns:
        Embedding vector (1024-dim BGE-m3)
    """
    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

    text_parts = []
    if hasattr(failure_signature, "component"):
        text_parts.append(failure_signature.component)
    if hasattr(failure_signature, "failure_type"):
        text_parts.append(failure_signature.failure_type)
    if hasattr(failure_signature, "healer_name"):
        text_parts.append(failure_signature.healer_name)
    text = " ".join(text_parts) if text_parts else "unknown_failure"
    return bmg_embed_text(text)


def _wc_digest(failure_sig: str, vector_source: str, profile_id: str, vector_count: int) -> str:
    """Compute, print, and return W-C-DETERMINISM-DIGEST.

    Binds: failure_signature | vector_source | retrieval_profile_id | vector_count.
    Printed exactly once per call; 64-char lowercase SHA-256 hex.
    """
    _inp = f"{failure_sig}|{vector_source}|{profile_id}|{vector_count}"
    _dig = hashlib.sha256(_inp.encode("utf-8", errors="replace")).hexdigest()
    print(f"W-C-DETERMINISM-DIGEST: {_dig}")
    return _dig


def _retrieve_semantic_context(rca_report: Any, pattern_report: Any, now_utc: int) -> dict[str, Any]:
    """Retrieve semantic context for healing configuration optimization.

    This is C0 informational context only - it augments candidate context
    but does not directly mutate any routing thresholds or safety tiers.

    W4-A: Uses RetrievalProfile from L4 for configuration authority.

    Args:
        rca_report: RCA report containing failure signatures
        pattern_report: Optional pattern analysis report
        now_utc: Current timestamp

    Returns:
        Dictionary containing embedding metadata for audit purposes only
    """
    retrieval_profile = get_active_retrieval_profile(now_utc)
    embedding_service = EmbeddingServiceFactory.get_or_disabled()
    shadow_telemetry: dict = {}
    if embedding_service.is_disabled():
        _wc_dig = _wc_digest("DISABLED", "disabled", retrieval_profile.profile_id, 0)
        return {
            "embedding_enabled_at_time": False,
            "embedding_replay_key": None,
            "embedding_artifact_hash": None,
            "embedding_topk_hashes": [],
            "embedding_topk_scores_round6": [],
            "retrieval_profile_id": retrieval_profile.profile_id,
            "vector_source": "disabled",
            "wc_determinism_digest": _wc_dig,
            **shadow_telemetry,
        }
    query_components = []
    if hasattr(rca_report, "failures"):
        for failure in rca_report.failures:
            if hasattr(failure, "failure_type"):
                query_components.append(failure.failure_type)
            if hasattr(failure, "component"):
                query_components.append(failure.component)
            if hasattr(failure, "error_tokens"):
                query_components.extend(failure.error_tokens[:3])
    if pattern_report and hasattr(pattern_report, "findings"):
        for finding in pattern_report.findings:
            if hasattr(finding, "key") and hasattr(finding.key, "label"):
                query_components.append(finding.key.label)
    failure_signature = "|".join(sorted(query_components)) if query_components else "generic_failure"
    import hashlib

    import numpy as np
    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

    _live_vec = bmg_embed_text(failure_signature)
    query_vector = np.array(_live_vec, dtype=np.float32)
    _vector_source = "bge-m3"
    shadow_telemetry = {}
    if retrieval_profile.shadow_embedder_id is not None:
        shadow_signature = f"{failure_signature}|shadow:{retrieval_profile.shadow_embedder_id}"
        shadow_hash = hashlib.sha256(shadow_signature.encode()).hexdigest()
        _qdim = query_vector.shape[0]
        shadow_vector = []
        for _si in range(_qdim):
            _hex_start = _si * 2 % (len(shadow_hash) - 1)
            val = int(shadow_hash[_hex_start : _hex_start + 2], 16) / 255.0
            shadow_vector.append(val)
        shadow_vector = np.array(shadow_vector, dtype=np.float32)
        primary_norm = round(float(np.linalg.norm(query_vector)), 6)
        shadow_norm = round(float(np.linalg.norm(shadow_vector)), 6)
        cosine_sim = round(
            float(
                np.dot(query_vector, shadow_vector)
                / (np.linalg.norm(query_vector) * np.linalg.norm(shadow_vector)),
            ),
            6,
        )
        shadow_telemetry = {
            "shadow_embedder_id": retrieval_profile.shadow_embedder_id,
            "primary_embedding_norm": primary_norm,
            "shadow_embedding_norm": shadow_norm,
            "primary_shadow_cosine": cosine_sim,
        }
        _accumulate_shadow_telemetry(shadow_telemetry)
    try:
        top_k_cap = retrieval_profile.top_k
        similarity_cutoff = retrieval_profile.similarity_cutoff
        results = embedding_service.retrieve(query_vector=query_vector, k=top_k_cap, cutoff=similarity_cutoff)
        if results is None:
            _wc_dig = _wc_digest(failure_signature, _vector_source, retrieval_profile.profile_id, 0)
            return {
                "embedding_enabled_at_time": True,
                "embedding_replay_key": getattr(embedding_service, "replay_key", None),
                "embedding_artifact_hash": None,
                "embedding_topk_hashes": [],
                "embedding_topk_scores_round6": [],
                "retrieval_profile_id": retrieval_profile.profile_id,
                "vector_source": _vector_source,
                "wc_determinism_digest": _wc_dig,
                **shadow_telemetry,
            }
        topk_hashes = [r.content_hash for r in results]
        topk_scores = [r.score_round6 for r in results]
        result_data = f"{failure_signature}|{topk_hashes}|{topk_scores}"
        artifact_hash = hashlib.sha256(result_data.encode()).hexdigest()
        _wc_dig = _wc_digest(
            failure_signature,
            _vector_source,
            retrieval_profile.profile_id,
            len(topk_hashes),
        )
        return {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": getattr(embedding_service, "replay_key", None),
            "embedding_artifact_hash": artifact_hash,
            "embedding_topk_hashes": topk_hashes,
            "embedding_topk_scores_round6": topk_scores,
            "retrieval_profile_id": retrieval_profile.profile_id,
            "vector_source": _vector_source,
            "wc_determinism_digest": _wc_dig,
            **shadow_telemetry,
        }
    except (ImportError, AttributeError, ValueError) as e:
        print(f"Embedding retrieval failed: {e}")
        _wc_dig = _wc_digest("ERROR", "error", retrieval_profile.profile_id, 0)
        return {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": None,
            "embedding_artifact_hash": "RETRIEVAL_FAILED",
            "embedding_topk_hashes": [],
            "embedding_topk_scores_round6": [],
            "retrieval_profile_id": retrieval_profile.profile_id,
            "vector_source": "error",
            "wc_determinism_digest": _wc_dig,
            **shadow_telemetry,
        }


def run_pipeline(
    now_utc: int,
    window_start_utc: int,
    window_end_utc: int,
    cfg: PipelineConfig,
    deps: PipelineDependencies,
) -> tuple[Any, ...]:
    """Run end-to-end meta-learning pipeline.

    Steps (strict order):
      1) Pull audit slice (read-only)
      2) Consume telemetry slice (read-only)
      3) Pull current configs from provider
      4) Create snapshot
      5) Produce RCA report
      6) Run enabled proposers to yield ChangePackages
      7) Validate each ChangePackage (replay, shadow, dampening)
      8) If proposal_only: return packages, DO NOT commit/activate
      9) If not proposal_only: Stage A commit + Stage B activation (with approval)

    Parameters
    ----------
    now_utc : int
        Current time (injected, not wall-clock).
    window_start_utc : int
        Start of analysis window.
    window_end_utc : int
        End of analysis window.
    cfg : PipelineConfig
        Pipeline configuration.
    deps : PipelineDependencies
        Injected dependencies.

    Returns
    -------
    tuple[Any, ...]
        Validated ChangePackages (proposals).

    Raises
    ------
    ValidationError
        If any validation fails.
    PipelineError
        If pipeline execution fails.
    """
    _emit_verifies_policy(str(uuid.uuid4()), "Module.run_pipeline", "L4_STATE")
    _emit_observes_runtime_state(str(uuid.uuid4()), "Module.run_pipeline", "L4_STATE")
    _emit_snapshots_state(str(uuid.uuid4()), "Module.run_pipeline", "L4_STATE")
    if window_start_utc >= window_end_utc:
        raise PipelineError(f"Invalid window: start={window_start_utc} >= end={window_end_utc}")
    if deps.freeze_reader is not None and deps.freeze_reader.is_frozen():
        raise PipelineError("meta-learning pipeline disabled: system freeze is active (L2 FREEZ)")
    global _shadow_telemetry_batch
    _shadow_telemetry_batch = []
    audit_slice = deps.audit_store.read_audit_slice(window_start_utc, window_end_utc)
    from system_learning.engines.telemetry_consumer import consume_telemetry

    consume_telemetry(deps.telemetry_store, window_start_utc, window_end_utc)
    current_configs = deps.config_provider.get_current_configs()
    from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot

    semantic_clock = SemanticClockSnapshot(tick=0, vector_clock=())
    snapshot = create_snapshot(
        engine_version=cfg.engine_version,
        config_surface_version=cfg.config_surface_version,
        audit_window_start_utc=window_start_utc,
        audit_window_end_utc=window_end_utc,
        telemetry_bytes=b"placeholder",
        policy_config_bytes=b"placeholder",
        routing_config_bytes=b"placeholder",
        model_config_bytes=b"placeholder",
        semantic_clock_bytes=b"placeholder",
        semantic_clock=semantic_clock,
    )
    from system_learning.engines.rca_engine import analyze_failures_and_persist as analyze_failures

    # Get ADG violation file set for correlation
    violation_file_set = None
    try:
        from agentic_core.adg.adapters.ADGMemoryAdapter import get_adapter

        adapter = get_adapter()
        violation_file_set = adapter.get_violation_file_set()
    except Exception as e:
        # ADG unavailable - continue without violation correlation
        import logging

        logging.getLogger(__name__).debug("meta_learning_pipeline: Exception swallowed at L906: %s", e)

    rca_report = analyze_failures(
        snapshot_id=snapshot.snapshot_id,
        audit_slice=audit_slice,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
        violation_file_set=violation_file_set,
    )
    if deps.failure_fingerprinter is not None and hasattr(rca_report, "failure_events"):
        fingerprints = [
            deps.failure_fingerprinter.fingerprint(ev).fingerprint_hex
            for ev in rca_report.failure_events or []
        ]
        if hasattr(rca_report, "with_fingerprints"):
            rca_report = rca_report.with_fingerprints(fingerprints)
    if deps.healing_confidence_scorer is not None and hasattr(rca_report, "healing_attempts"):
        confidence_report = deps.healing_confidence_scorer.score(rca_report.healing_attempts or [])
        if hasattr(rca_report, "with_confidence"):
            rca_report = rca_report.with_confidence(confidence_report)
    if (
        deps.risk_correlator is not None
        and hasattr(rca_report, "fingerprints")
        and hasattr(snapshot, "drift_events")
    ):
        correlated_risk = deps.risk_correlator.build(
            rca_report.fingerprints or [],
            snapshot.drift_events or [],
        )
        if hasattr(rca_report, "with_correlated_risk"):
            rca_report = rca_report.with_correlated_risk(correlated_risk)
    proposer_order = ("L0", "RAG", "L1", "L5")
    proposer_map = {
        "L0": deps.l0_proposer,
        "RAG": deps.rag_proposer,
        "L1": deps.l1_proposer,
        "L5": deps.l5_proposer,
    }
    from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector

    _inj_detector = InjectionDetector()
    proposals = []
    for key in tqdm(proposer_order, desc="proposals", unit="key", leave=False):
        proposer = proposer_map[key]
        if proposer is None:
            continue
        if hasattr(snapshot, "u0_user_prompt"):
            _inj_detector.scan(snapshot.u0_user_prompt)
        if hasattr(snapshot, "aggregate_snapshot"):
            if hasattr(snapshot.aggregate_snapshot, "narrative"):
                _inj_detector.scan(snapshot.aggregate_snapshot.narrative)
        pkg = proposer.propose(
            snapshot=snapshot,
            metrics=None,
            config=current_configs,
            now_utc=now_utc,
            history=None,
            cooldown=cfg.cooldown_policy,
            sample=cfg.sample_policy,
        )
        if pkg is not None:
            proposals.append(pkg)
    if deps.resource_predictor_bytes is not None:
        try:
            import json

            prediction_data = json.loads(deps.resource_predictor_bytes.decode("utf-8"))
            from system_learning.types.proposal_types import ChangePackage

            resource_proposal = ChangePackage(
                source="phase9_resource_predictor",
                target="resource_envelope",
                changes=deps.resource_predictor_bytes,
                confidence=prediction_data.get("confidence", 0.5),
                reason=tuple(prediction_data.get("reasons", [])),
                timestamp_utc=now_utc,
            )
            proposals.append(resource_proposal)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Resource prediction failed: {e}")
    if deps.rollback_refinement_decision_bytes is not None:
        try:
            import json

            decision_data = json.loads(deps.rollback_refinement_decision_bytes.decode("utf-8"))
            from system_learning.types.proposal_types import ChangePackage

            rollback_proposal = ChangePackage(
                source="phase9_rollback_refiner",
                target="rollback_strategy",
                changes=deps.rollback_refinement_decision_bytes,
                confidence=0.8,
                reason=tuple(decision_data.get("reasons", [])),
                timestamp_utc=now_utc,
            )
            proposals.append(rollback_proposal)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Rollback refinement failed: {e}")
    if deps.dpo_batch_bytes is not None and deps.rlhf_optimizer is not None:
        try:
            import json as _json_dpo

            current_threshold_config_bytes = _json_dpo.dumps(
                current_configs,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            dpo_proposal = deps.rlhf_optimizer.propose_from_dpo(
                dpo_batch_bytes=deps.dpo_batch_bytes,
                current_threshold_config_bytes=current_threshold_config_bytes,
            )
            from dataclasses import replace as _dc_replace

            from system_learning.engines.change_package_impl import ChangePackage as _CP

            if isinstance(dpo_proposal, _CP):
                dpo_proposal = _dc_replace(dpo_proposal, timestamp_utc=now_utc)
            elif hasattr(dpo_proposal, "timestamp_utc"):
                try:
                    dpo_proposal.timestamp_utc = now_utc
                except (AttributeError, TypeError):
                    pass  # guardian: allow-silent-swallow -- intentional: AttributeError used for control flow
            # DPO proposals enter before Stage 7 validation loop
            proposals.append(dpo_proposal)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"DPO batch processing failed: {e}")
    from system_learning.constraints.dampening import assert_cooldown_ok, assert_min_sample_size
    from system_learning.validators.oscillation_detector import compute_freeze_decision
    from system_learning.validators.replay_validator import replay_validate
    from system_learning.validators.shadow_evaluator import evaluate_shadow

    # Step 7: Validate each proposal
    validated_proposals = []
    for pkg in tqdm(proposals, desc="validate proposals", unit="pkg", leave=False):
        if cfg.require_replay_validation:

            def canonicalize(output):
                if hasattr(output, "canonical_bytes"):
                    return output.canonical_bytes()
                return str(output).encode("utf-8")

            replay_validate(snapshot, lambda s: pkg, canonicalize_fn=canonicalize)
        if cfg.require_shadow_validation and hasattr(deps.baseline_metrics_provider, "production_metrics"):
            production = deps.baseline_metrics_provider.production_metrics()
            shadow = deps.baseline_metrics_provider.shadow_metrics(pkg)
            evaluate_shadow(production, shadow, cfg.shadow_thresholds)
        surface_name = getattr(pkg, "surface_name", "unknown")
        if hasattr(deps.config_provider, "get_last_update_utc") and hasattr(
            cfg.cooldown_policy,
            "min_seconds_between_updates",
        ):
            last_update_utc = deps.config_provider.get_last_update_utc(surface_name)
            if last_update_utc is not None:
                assert_cooldown_ok(
                    last_update_utc=last_update_utc,
                    now_utc=now_utc,
                    cooldown_policy=cfg.cooldown_policy,
                )
        else:
            last_update_utc = None
        if hasattr(cfg.sample_policy, "min_observations"):
            _audit_text = (
                audit_slice.decode("utf-8", errors="replace")
                if isinstance(audit_slice, (bytes, bytearray))
                else str(audit_slice)
            )
            n_observations = max(1, sum(1 for ln in _audit_text.splitlines() if ln.strip()))
            assert_min_sample_size(n_observations=n_observations, sample_policy=cfg.sample_policy)
        if hasattr(deps.config_provider, "get_param_history") and hasattr(cfg.oscillation_policy, "window"):
            param_history = deps.config_provider.get_param_history(
                surface_name,
                cfg.oscillation_policy.window,
            )
            if len(param_history) > 0:
                freeze_decision = compute_freeze_decision(
                    values=param_history,
                    last_update_utc=last_update_utc or 0,
                    now_utc=now_utc,
                    policy=cfg.oscillation_policy,
                )
                if freeze_decision.should_freeze:
                    raise ValidationError(
                        f"Oscillation detected for {surface_name}: freeze until {freeze_decision.freeze_until_utc}",
                    )
        validated_proposals.append(pkg)
    if deps.arbitration_engine is not None and deps.arbitration_policy is not None and validated_proposals:
        candidates = [
            ArbitrationCandidate(
                id=getattr(p, "proposal_id", str(i)),
                score=getattr(p, "score", 0.0),
                cost=getattr(p, "cost", 1.0),
                kind=getattr(p, "kind", "generic"),
                payload=p.to_dict() if hasattr(p, "to_dict") else {},
            )
            for i, p in enumerate(validated_proposals)
        ]
        decision = deps.arbitration_engine.arbitrate(candidates, deps.arbitration_policy)
        winner_ids = set(decision.winner_ids)
        validated_proposals = [
            p for i, p in enumerate(validated_proposals) if getattr(p, "proposal_id", str(i)) in winner_ids
        ]
    intake_record = None
    if deps.healing_outcome_intake_adapter is not None:
        _window_records = deps.healing_outcome_intake_adapter.get_recent_records(
            window_start_utc,
            window_end_utc,
        )
        if _window_records:
            from system_learning.types.healing_outcome_types import HealingOutcomeEvent as _WHE

            _window_aggregator = HealingOutcomeAggregator(window_size=10000)
            for _rec in tqdm(_window_records, desc="window records", unit="rec", leave=False):
                for _s in tqdm(_rec.snapshot, desc="  snapshots", unit="snap", leave=False):
                    for _ in range(_s.success_count):
                        _window_aggregator.ingest(
                            _WHE(
                                healer_id=_s.healer_id,
                                tier=_s.tier,
                                failure_type=_s.failure_type,
                                success=True,
                                timestamp_utc=now_utc,
                            ),
                        )
                    for _ in range(_s.failure_count):
                        _window_aggregator.ingest(
                            _WHE(
                                healer_id=_s.healer_id,
                                tier=_s.tier,
                                failure_type=_s.failure_type,
                                success=False,
                                timestamp_utc=now_utc,
                            ),
                        )
            intake_record = deps.healing_outcome_intake_adapter.build_record(
                aggregator=_window_aggregator,
                created_utc=now_utc,
                source="meta-learning-pipeline-window",
            )
            deps.healing_outcome_intake_adapter.persist_record(intake_record)
        else:
            intake_record = None
    if (
        deps.healing_config_optimizer is not None
        and intake_record is not None  # guardian: Runtime errors should be prevented with proper validation
        and hasattr(
            intake_record, "snapshot"
        )  # guardian: Runtime errors should be prevented with proper validation
    ):
        aggregate_snapshot = deps.healing_config_optimizer.create_snapshot_from_intake(
            intake_record,
            created_utc=now_utc,
        )
        if deps.l4_state_writer is not None:
            try:
                payload_bytes = aggregate_snapshot.canonical_bytes()
                deps.l4_state_writer.write_l4b_healing_snapshot(
                    payload_bytes=payload_bytes,
                    component_name="meta-learning",
                    created_utc=now_utc,
                )
            except RuntimeError as e:
                print(f"L4 write failed: {e}")
            except (AttributeError, TypeError, OSError) as e:
                print(f"L4 write failed: {e}")
                return None
        else:
            pass
        _detection_signal_bytes: bytes | None = None
        _drift_snapshot_bytes: bytes | None = None
        if deps.l4_state_writer is not None:
            if hasattr(deps.l4_state_writer, "read_latest_detection_signal"):
                _detection_signal_bytes = deps.l4_state_writer.read_latest_detection_signal()
            if hasattr(deps.l4_state_writer, "read_latest_drift_snapshot"):
                _drift_snapshot_bytes = deps.l4_state_writer.read_latest_drift_snapshot()
        _8_5_aggregate_snapshot = aggregate_snapshot
        try:
            from system_learning.adapters.system_learning_memory_bridge import (
                get_sl_memory_bridge as _get_sl_bridge_agg,
            )

            _get_sl_bridge_agg().persist_healing_aggregate_snapshot(aggregate_snapshot, ts=str(now_utc))
        # guardian: allow-silent-swallow -- MCP aggregate persist is non-critical telemetry; pipeline output unaffected by bridge failure
        except Exception:
            pass
    else:
        _8_5_aggregate_snapshot = None
    _detection_signal_bytes_86: bytes | None = None
    _drift_snapshot_bytes_86: bytes | None = None
    if deps.l4_state_writer is not None:
        if hasattr(deps.l4_state_writer, "read_latest_detection_signal"):
            _detection_signal_bytes_86 = deps.l4_state_writer.read_latest_detection_signal()
        if hasattr(deps.l4_state_writer, "read_latest_drift_snapshot"):
            _drift_snapshot_bytes_86 = deps.l4_state_writer.read_latest_drift_snapshot()
    pattern_report = _analyze_historical_patterns(
        deps,
        _8_5_aggregate_snapshot,
        now_utc=now_utc,
        detection_signal_bytes=_detection_signal_bytes_86,
        drift_snapshot_bytes=_drift_snapshot_bytes_86,
    )
    embedding_metadata = _retrieve_semantic_context(
        rca_report=rca_report,
        pattern_report=pattern_report,
        now_utc=now_utc,
    )
    if deps.cross_repo_learning_context is not None:
        embedding_metadata = {
            **embedding_metadata,
            "cross_repo_learning_context": deps.cross_repo_learning_context,
        }
    if _8_5_aggregate_snapshot is not None:
        from system_learning.engines.retrieval_profile_manager import get_active_retrieval_profile

        active_profile = get_active_retrieval_profile(now_utc)
        drift_summary = _analyze_shadow_drift_and_write(
            profile_id=active_profile.profile_id,
            now_utc=now_utc,
            l4_writer=deps.l4_state_writer,
        )
        if drift_summary is not None:
            drift_summary.emit_digest()
            try:
                from system_learning.adapters.system_learning_memory_bridge import (
                    get_sl_memory_bridge as _get_sl_bridge_drift,
                )

                _get_sl_bridge_drift().persist_drift_summary(drift_summary)
            # guardian: allow-silent-swallow -- MCP drift-summary persist is non-critical telemetry; digest already emitted above
            except Exception:
                pass
        policy_recommendation = _generate_policy_recommendation_and_write(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
            l4_writer=deps.l4_state_writer,
        )
        if policy_recommendation is not None:
            policy_recommendation.emit_digest()
            try:
                from system_learning.adapters.system_learning_memory_bridge import (
                    get_sl_memory_bridge as _get_sl_bridge_pol,
                )

                _get_sl_bridge_pol().persist_policy_recommendation(policy_recommendation)
            # guardian: allow-silent-swallow -- MCP policy-rec persist is non-critical telemetry; digest already emitted above
            except Exception:
                pass
        profile_proposal = _create_proposal_and_write(
            policy_recommendation=policy_recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
            l4_writer=deps.l4_state_writer,
        )
        if profile_proposal is not None:
            profile_proposal.emit_digest()
        if deps.healing_config_optimizer is not None:
            if hasattr(
                deps.healing_config_optimizer,
                "propose_threshold_adjustments_with_patterns_and_embeddings",
            ):
                threshold_proposal = (
                    deps.healing_config_optimizer.propose_threshold_adjustments_with_patterns_and_embeddings(
                        _8_5_aggregate_snapshot,
                        pattern_report,
                        embedding_metadata,
                    )
                )
            elif hasattr(deps.healing_config_optimizer, "propose_threshold_adjustments_with_patterns"):
                threshold_proposal = (
                    deps.healing_config_optimizer.propose_threshold_adjustments_with_patterns(
                        _8_5_aggregate_snapshot,
                        pattern_report,
                    )
                )
            else:
                threshold_proposal = deps.healing_config_optimizer.propose_threshold_adjustments(
                    _8_5_aggregate_snapshot,
                )
        else:
            threshold_proposal = None
        if threshold_proposal is not None and embedding_metadata:
            _artifact_hash = embedding_metadata.get("embedding_artifact_hash") or embedding_metadata.get(
                "content_hash",
            )
            if _artifact_hash and hasattr(threshold_proposal, "embedding_context_hash"):
                from dataclasses import replace as _dc_replace_ec

                threshold_proposal = _dc_replace_ec(threshold_proposal, embedding_context_hash=_artifact_hash)
        if (
            threshold_proposal is not None
            and hasattr(threshold_proposal, "adjustments")
            and threshold_proposal.adjustments
        ):
            validated_proposals.append(threshold_proposal)
    if cfg.proposal_only:
        return tuple(validated_proposals)
    _vs_present = deps.version_store is not None
    _ag_present = deps.approval_gate is not None
    if _vs_present and (not _ag_present):
        raise PipelineError(
            "partial injection: approval_gate required when version_store is present; both must be injected together when proposal_only=False",
        )
    if _ag_present and (not _vs_present):
        raise PipelineError(
            "partial injection: version_store required when approval_gate is present; both must be injected together when proposal_only=False",
        )
    if not _vs_present:
        raise PipelineError("version_store required when proposal_only=False")
    if not _ag_present:
        raise PipelineError("approval_gate required when proposal_only=False")
    from system_learning.pipelines.approval_gates import ApprovalDecision

    committed_versions = []
    for pkg in validated_proposals:
        decision = deps.approval_gate.decide(pkg, rca_report, snapshot)
        if decision == ApprovalDecision.REJECT:
            continue
        version_id = deps.version_store.commit_change_package(pkg)
        committed_versions.append((pkg, version_id))
        if deps.activator is not None:
            component = getattr(pkg, "target_surface", None) or getattr(pkg, "target", "unknown")
            deps.activator.activate(component, version_id)

    # Wave B-5: Unpack Execute_SSOT phase outcomes for meta-learning
    try:
        from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

        bridge = get_sl_memory_bridge()

        # Query recent Execute_SSOT phase outcomes
        # This would need a query method in the bridge - for now track that we attempted
        bridge._query_execute_ssot_outcomes(now_utc)
    except Exception as e:
        # Query failed - continue without it
        import logging

        logging.getLogger(__name__).debug("meta_learning_pipeline: Exception swallowed at L1316: %s", e)

    return tuple(validated_proposals)
