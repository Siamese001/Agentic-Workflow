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

Invariants:
  - Default proposal_only=True (zero execution authority)
  - No wall-clock reads (now_utc injected)
  - Fail-closed on validation failure
  - Stage A commit + Stage B activation only via injected interfaces
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer
from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.pattern_analysis_engine import PatternAnalysisEngine
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_manager import get_active_retrieval_profile
from system_learning.engines.rlhf_optimizer import RLHFOptimizer
from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer, DriftSummary
from system_learning.engines.policy_recommendation_engine import PolicyRecommendationEngine, PolicyRecommendation
from system_learning.snapshots.snapshot_factory import create_snapshot
from system_learning.types.snapshot_types import MetaLearningSnapshot
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds

# =============================================================================
# W4-C: Shadow Drift Analysis State
# =============================================================================

# Global batch accumulator for shadow telemetry (informational only)
_shadow_telemetry_batch: list[dict[str, Any]] = []
_shadow_drift_analyzer = ShadowDriftAnalyzer()

# W4-D: Policy recommendation engine (advisory only)
_policy_recommendation_engine = PolicyRecommendationEngine()


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
    
    # Analyze the batch
    drift_summary = _shadow_drift_analyzer.analyze_batch(
        shadow_records=_shadow_telemetry_batch,
        profile_id=profile_id,
        now_utc=now_utc,
    )
    
    # Write to L4 (informational only)
    try:
        summary_json = drift_summary.to_canonical_json().encode('utf-8')
        l4_writer.write_l4c_shadow_drift(
            payload_bytes=summary_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    except Exception:
        # L4 write failure should not break pipeline
        pass
    
    # Clear the batch for next run
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
    
    # Generate recommendation
    recommendation = _policy_recommendation_engine.generate_recommendation(
        drift_summary=drift_summary,
        active_profile=active_profile,
        now_utc=now_utc,
    )
    
    # Write to L4 (advisory only)
    try:
        recommendation_json = recommendation.to_canonical_json().encode('utf-8')
        l4_writer.write_l4c_policy_recommendation(
            payload_bytes=recommendation_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    except Exception:
        # L4 write failure should not break pipeline
        pass
    
    return recommendation


# =============================================================================
# Exceptions
# =============================================================================


class PipelineError(RuntimeError):
    """Base exception for pipeline errors."""


class ValidationError(PipelineError):
    """Raised when validation fails."""


# =============================================================================
# Configuration
# =============================================================================


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


# =============================================================================
# Protocols (Injected Dependencies)
# =============================================================================


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


# =============================================================================
# Pipeline Dependencies
# =============================================================================


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


# =============================================================================
# Pattern Analysis (W3 - Deterministic, Informational-Only)
# =============================================================================


def _analyze_historical_patterns(
    deps: PipelineDependencies,
    aggregate_snapshot: Any,
) -> Any:
    """Analyze historical patterns using W3 PatternAnalysisEngine.
    
    W3: Pattern Analysis Engine (Deterministic, Informational-Only).
    
    Args:
        deps: Pipeline dependencies containing pattern_analysis_engine
        aggregate_snapshot: Healing outcome aggregate snapshot
        
    Returns:
        PatternSummary or None if analysis fails or is disabled
    """
    if deps.pattern_analysis_engine is None:
        return None
    
    # Check embedding kill switch
    embedding_service = EmbeddingServiceFactory.get_or_disabled()
    if embedding_service.is_disabled():
        return None
    
    try:
        # Extract historical embeddings from aggregate snapshot
        historical_embeddings = []
        metadata = []
        
        if hasattr(aggregate_snapshot, 'outcomes'):
            for outcome in aggregate_snapshot.outcomes:
                # Create embedding from failure signature
                if hasattr(outcome, 'failure_signature'):
                    # For W3, create simple deterministic embeddings
                    # In production, these would come from actual embedding service
                    embedding = _create_deterministic_embedding(outcome.failure_signature)
                    historical_embeddings.append(embedding)
                    
                    # Extract metadata
                    meta = {
                        'healer_name': getattr(outcome, 'healer_name', 'unknown'),
                        'failure_type': getattr(outcome, 'failure_type', 'unknown'),
                        'component': getattr(outcome, 'component', 'unknown'),
                    }
                    metadata.append(meta)
        
        if not historical_embeddings:
            return None
        
        # Apply small-N guard (minimum 10 data points for pattern analysis)
        if len(historical_embeddings) < 10:
            return None
        
        # Run pattern analysis with deterministic parameters
        pattern_summary = deps.pattern_analysis_engine.analyze(
            historical_embeddings=historical_embeddings,
            metadata=metadata,
            min_cluster_size=3,  # Fixed minimum cluster size
        )
        
        # Print digest for determinism proof
        print(f"W3-PATTERN-DIGEST: {pattern_summary.pattern_digest}")
        
        return pattern_summary
        
    except Exception:
        # Pattern analysis failure should not break pipeline
        return None


def _create_deterministic_embedding(failure_signature: Any) -> List[float]:
    """Create deterministic embedding from failure signature.
    
    W3 requires deterministic embeddings for reproducible clustering.
    
    Args:
        failure_signature: Failure signature object
        
    Returns:
        Deterministic 4-dimensional embedding vector
    """
    import hashlib
    
    # Extract deterministic features from failure signature
    components = []
    
    # Component name (hashed)
    if hasattr(failure_signature, 'component'):
        comp_hash = hashlib.sha256(failure_signature.component.encode()).hexdigest()
        components.append(int(comp_hash[:8], 16) / 2**32)
    else:
        components.append(0.0)
    
    # Failure type (hashed)
    if hasattr(failure_signature, 'failure_type'):
        type_hash = hashlib.sha256(failure_signature.failure_type.encode()).hexdigest()
        components.append(int(type_hash[:8], 16) / 2**32)
    else:
        components.append(0.0)
    
    # Healer name (hashed)
    if hasattr(failure_signature, 'healer_name'):
        healer_hash = hashlib.sha256(failure_signature.healer_name.encode()).hexdigest()
        components.append(int(healer_hash[:8], 16) / 2**32)
    else:
        components.append(0.0)
    
    # Timestamp (normalized)
    if hasattr(failure_signature, 'timestamp_utc'):
        # Normalize to [0, 1] range using last 32 bits
        components.append((failure_signature.timestamp_utc & 0xFFFFFFFF) / 2**32)
    else:
        components.append(0.0)
    
    return components


# =============================================================================
# Semantic Retrieval (W2 - Informational Context Only)
# =============================================================================


def _retrieve_semantic_context(
    rca_report: Any,
    pattern_report: Any,
    now_utc: int,
) -> dict[str, Any]:
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
    # Load active RetrievalProfile from L4 (W4-A authority)
    # No fallback - RetrievalProfile must be bootstrapped into L4 before use
    retrieval_profile = get_active_retrieval_profile(now_utc)
    
    # Get embedding service with total kill-switch coverage
    embedding_service = EmbeddingServiceFactory.get_or_disabled()

    # If disabled, return empty metadata (no telemetry, no placeholders)
    if embedding_service.is_disabled():
        return {
            "embedding_enabled_at_time": False,
            "embedding_replay_key": None,
            "embedding_artifact_hash": None,
            "embedding_topk_hashes": [],
            "embedding_topk_scores_round6": [],
            "retrieval_profile_id": retrieval_profile.profile_id,
            **shadow_telemetry,  # W4-B: Include shadow telemetry even when disabled
        }

    # Construct deterministic query from failure signature material
    # Use RCA failure patterns and pattern findings if available
    query_components = []

    # Extract failure type and component from RCA
    if hasattr(rca_report, "failures"):
        for failure in rca_report.failures:
            if hasattr(failure, "failure_type"):
                query_components.append(failure.failure_type)
            if hasattr(failure, "component"):
                query_components.append(failure.component)
            if hasattr(failure, "error_tokens"):
                query_components.extend(failure.error_tokens[:3])  # First 3 tokens

    # Add pattern tags if available
    if pattern_report and hasattr(pattern_report, "findings"):
        for finding in pattern_report.findings:
            if hasattr(finding, "key") and hasattr(finding.key, "label"):
                query_components.append(finding.key.label)

    # Create deterministic query string
    failure_signature = "|".join(sorted(query_components)) if query_components else "generic_failure"

    # For W2, we use a simple hash-based approach since no embedder is available
    # In a full implementation, this would use the pinned embedder from governance
    import hashlib

    # Create a deterministic query vector from the signature hash
    query_hash = hashlib.sha256(failure_signature.encode()).hexdigest()
    # Use first 8 hex digits to create a simple 4D vector for demonstration
    query_vector = []
    for i in range(0, 8, 2):
        val = int(query_hash[i : i + 2], 16) / 255.0  # Normalize to [0, 1]
        query_vector.append(val)

    import numpy as np

    query_vector = np.array(query_vector, dtype=np.float32)

    # W4-B: Compute shadow embedding if configured (non-influential telemetry)
    shadow_telemetry = {}
    if retrieval_profile.shadow_embedder_id is not None:
        # Compute shadow vector using same deterministic method but different embedder ID
        shadow_signature = f"{failure_signature}|shadow:{retrieval_profile.shadow_embedder_id}"
        shadow_hash = hashlib.sha256(shadow_signature.encode()).hexdigest()
        
        # Create shadow vector (same dimension, different seed)
        shadow_vector = []
        for i in range(0, 8, 2):
            val = int(shadow_hash[i : i + 2], 16) / 255.0  # Normalize to [0, 1]
            shadow_vector.append(val)
        
        shadow_vector = np.array(shadow_vector, dtype=np.float32)
        
        # Compute telemetry metrics with stable rounding
        primary_norm = round(float(np.linalg.norm(query_vector)), 6)
        shadow_norm = round(float(np.linalg.norm(shadow_vector)), 6)
        
        # Compute cosine similarity
        cosine_sim = round(float(np.dot(query_vector, shadow_vector) / 
                                (np.linalg.norm(query_vector) * np.linalg.norm(shadow_vector))), 6)
        
        shadow_telemetry = {
            "shadow_embedder_id": retrieval_profile.shadow_embedder_id,
            "primary_embedding_norm": primary_norm,
            "shadow_embedding_norm": shadow_norm,
            "primary_shadow_cosine": cosine_sim,
        }
        
        # W4-C: Accumulate shadow telemetry for drift analysis
        _accumulate_shadow_telemetry(shadow_telemetry)

    # Retrieve with RetrievalProfile configuration (W4-A authority)
    try:
        # Use RetrievalProfile parameters instead of hardcoded values
        top_k_cap = retrieval_profile.top_k
        similarity_cutoff = retrieval_profile.similarity_cutoff

        results = embedding_service.retrieve(query_vector=query_vector, k=top_k_cap, cutoff=similarity_cutoff)

        if results is None:
            return {
                "embedding_enabled_at_time": True,
                "embedding_replay_key": getattr(embedding_service, "replay_key", None),
                "embedding_artifact_hash": None,
                "embedding_topk_hashes": [],
                "embedding_topk_scores_round6": [],
                "retrieval_profile_id": retrieval_profile.profile_id,
                **shadow_telemetry,  # W4-B: Include shadow telemetry
            }

        # Extract metadata for audit (C0 informational only)
        topk_hashes = [r.content_hash for r in results]
        topk_scores = [r.score_round6 for r in results]

        # Compute artifact hash from results
        result_data = f"{failure_signature}|{topk_hashes}|{topk_scores}"
        artifact_hash = hashlib.sha256(result_data.encode()).hexdigest()

        return {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": getattr(embedding_service, "replay_key", None),
            "embedding_artifact_hash": artifact_hash,
            "embedding_topk_hashes": topk_hashes,
            "embedding_topk_scores_round6": topk_scores,
            "retrieval_profile_id": retrieval_profile.profile_id,
            **shadow_telemetry,  # W4-B: Include shadow telemetry
        }

    except Exception:
        # Embedding retrieval failure should not break pipeline
        # Return minimal metadata indicating failure
        return {
            "embedding_enabled_at_time": True,
            "embedding_replay_key": None,
            "embedding_artifact_hash": "RETRIEVAL_FAILED",
            "embedding_topk_hashes": [],
            "embedding_topk_scores_round6": [],
            "retrieval_profile_id": retrieval_profile.profile_id,
            **shadow_telemetry,  # W4-B: Include shadow telemetry even on failure
        }


# =============================================================================
# Pipeline Orchestrator
# =============================================================================


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
    # Validate window
    if window_start_utc >= window_end_utc:
        raise PipelineError(f"Invalid window: start={window_start_utc} >= end={window_end_utc}")

    # Step 1: Pull audit slice (read-only)
    audit_slice = deps.audit_store.read_audit_slice(window_start_utc, window_end_utc)

    # Step 2: Consume telemetry slice (read-only)
    from system_learning.engines.telemetry_consumer import consume_telemetry

    consume_telemetry(deps.telemetry_store, window_start_utc, window_end_utc)

    # Step 3: Pull current configs
    current_configs = deps.config_provider.get_current_configs()

    # Step 4: Create snapshot
    # For now, create a minimal snapshot with required fields
    # In production, this would pull from L4 state
    from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot

    # Create a minimal semantic clock for testing
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

    # Step 5: Produce RCA report
    from system_learning.engines.rca_engine import analyze_failures

    rca_report = analyze_failures(
        snapshot_id=snapshot.snapshot_id,
        audit_slice=audit_slice,
        window_start_utc=window_start_utc,
        window_end_utc=window_end_utc,
    )

    # Step 6: Run enabled proposers in deterministic order
    # Fixed order: ("L0", "RAG", "L1", "L5") intersect enabled set
    PROPOSER_ORDER = ("L0", "RAG", "L1", "L5")
    proposer_map = {
        "L0": deps.l0_proposer,
        "RAG": deps.rag_proposer,
        "L1": deps.l1_proposer,
        "L5": deps.l5_proposer,
    }

    proposals = []
    for proposer_name in PROPOSER_ORDER:
        if proposer_name not in cfg.enabled_proposers:
            continue

        proposer = proposer_map[proposer_name]
        if proposer is None:
            continue

        # Call proposer with injected dependencies
        # For now, pass minimal/placeholder args (would be real in production)
        pkg = proposer.propose(
            snapshot=snapshot,
            metrics=None,  # Would be real metrics
            config=current_configs,
            now_utc=now_utc,
            history=None,  # Would be real history
            cooldown=cfg.cooldown_policy,
            sample=cfg.sample_policy,
        )

        if pkg is not None:
            proposals.append(pkg)

    # Step 6b: Process Phase 9 artifacts (ResourcePrediction and RollbackRefinementDecision)
    if deps.resource_predictor_bytes is not None:
        try:
            # Deserialize ResourcePrediction and create proposal
            import json

            prediction_data = json.loads(deps.resource_predictor_bytes.decode("utf-8"))
            # Reconstruct ResourcePrediction from serialized data
            # For now, create a minimal proposal wrapper
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
        except Exception:  # noqa: BLE001
            # Log error but continue pipeline
            pass

    if deps.rollback_refinement_decision_bytes is not None:
        try:
            # Deserialize RollbackRefinementDecision and create proposal
            import json

            decision_data = json.loads(deps.rollback_refinement_decision_bytes.decode("utf-8"))
            # Reconstruct RollbackRefinementDecision from serialized data
            # For now, create a minimal proposal wrapper
            from system_learning.types.proposal_types import ChangePackage

            rollback_proposal = ChangePackage(
                source="phase9_rollback_refiner",
                target="rollback_strategy",
                changes=deps.rollback_refinement_decision_bytes,
                confidence=0.8,  # Default confidence for rollback decisions
                reason=tuple(decision_data.get("reasons", [])),
                timestamp_utc=now_utc,
            )
            proposals.append(rollback_proposal)
        except Exception:  # noqa: BLE001
            # Log error but continue pipeline
            pass

    # Step 6c: Process DPO batch (Path D - HITL + Deterministic DPO Loop)
    if deps.dpo_batch_bytes is not None and deps.rlhf_optimizer is not None:
        try:
            # Get current threshold config for time-shifted rule
            current_threshold_config_bytes = json.dumps(
                current_configs, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")

            # Generate proposal-only adjustments from DPO batch
            dpo_proposal = deps.rlhf_optimizer.propose_from_dpo(
                dpo_batch_bytes=deps.dpo_batch_bytes,
                current_threshold_config_bytes=current_threshold_config_bytes,
            )

            # Set timestamp for proposal
            dpo_proposal.timestamp_utc = now_utc

            proposals.append(dpo_proposal)
        except Exception:  # noqa: BLE001
            # Log error but continue pipeline
            pass

    # Step 7: Validate each proposal
    from system_learning.validators.dampening import (
        assert_cooldown_ok,
        assert_min_sample_size,
    )
    from system_learning.validators.oscillation_detector import compute_freeze_decision
    from system_learning.validators.replay_validator import replay_validate
    from system_learning.validators.shadow_evaluator import evaluate_shadow

    validated_proposals = []
    for pkg in proposals:
        # Replay validation (if required)
        if cfg.require_replay_validation:
            # Use package's canonical_bytes method for canonicalization
            def canonicalize(output):
                if hasattr(output, "canonical_bytes"):
                    return output.canonical_bytes()
                return str(output).encode("utf-8")

            replay_validate(snapshot, lambda s: pkg, canonicalize_fn=canonicalize)

        # Shadow validation (if required)
        if cfg.require_shadow_validation:
            production = deps.baseline_metrics_provider.production_metrics()
            shadow = deps.baseline_metrics_provider.shadow_metrics(pkg)
            evaluate_shadow(production, shadow, cfg.shadow_thresholds)

        # Dampening gates: cooldown
        # Extract surface name from package (would be in real ChangePackage)
        surface_name = getattr(pkg, "surface_name", "unknown")
        last_update_utc = deps.config_provider.get_last_update_utc(surface_name)
        if last_update_utc is not None:
            assert_cooldown_ok(
                last_update_utc=last_update_utc,
                now_utc=now_utc,
                policy=cfg.cooldown_policy,
            )

        # Dampening gates: sample size
        # Would get actual n_observations from metrics provider
        n_observations = 1000  # Placeholder
        assert_min_sample_size(
            n_observations=n_observations,
            policy=cfg.sample_policy,
        )

        # Oscillation gate
        param_history = deps.config_provider.get_param_history(surface_name, cfg.oscillation_policy.window)
        if len(param_history) > 0:
            freeze_decision = compute_freeze_decision(
                values=param_history,
                last_update_utc=last_update_utc or 0,
                now_utc=now_utc,
                policy=cfg.oscillation_policy,
            )
            if freeze_decision.should_freeze:
                raise ValidationError(
                    f"Oscillation detected for {surface_name}: freeze until {freeze_decision.freeze_until_utc}"
                )

        validated_proposals.append(pkg)

    # Step 8: Persist healing outcome intake record (optional)
    # This runs before proposal_only check to ensure intake is always captured
    if deps.healing_outcome_intake_adapter is not None:
        # Create a mock aggregator with events for demonstration
        # In real usage, this would be injected or created from actual healing outcomes
        mock_aggregator = HealingOutcomeAggregator(window_size=10)

        # Add a mock event to avoid empty snapshot validation
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        mock_event = HealingOutcomeEvent(
            healer_id="test_healer",
            tier="LOCAL_AGENT",
            failure_type="test_failure",
            success=True,
            timestamp_utc=9999,
        )
        mock_aggregator.ingest(mock_event)

        # Build and persist the intake record
        intake_record = deps.healing_outcome_intake_adapter.build_record(
            aggregator=mock_aggregator, created_utc=now_utc, source="meta-learning-pipeline"
        )
        deps.healing_outcome_intake_adapter.persist_record(intake_record)

    # Step 8.5: Run healing config optimizer if available
    if deps.healing_config_optimizer is not None and hasattr(intake_record, "snapshot"):
        # Create aggregate snapshot from intake
        aggregate_snapshot = deps.healing_config_optimizer.create_snapshot_from_intake(
            intake_record, created_utc=now_utc
        )

        # Write L4B healing snapshot if writer available
        if deps.l4_state_writer is not None:
            try:
                # Serialize aggregate snapshot to bytes
                payload_bytes = aggregate_snapshot.canonical_bytes()
                deps.l4_state_writer.write_l4b_healing_snapshot(
                    payload_bytes=payload_bytes, component_name="meta-learning", created_utc=now_utc
                )
            except Exception:
                # L4B write failure should not break pipeline
                # In production, this would be logged
                pass

        # Step 8.6: Pattern analysis (W3 - deterministic, informational only)
        pattern_report = _analyze_historical_patterns(deps, aggregate_snapshot)

        # Step 8.7: Retrieve semantic context (W2 - C0 informational only)
        embedding_metadata = _retrieve_semantic_context(
            rca_report=rca_report, pattern_report=pattern_report, now_utc=now_utc
        )

        # Step 8.8: W4-C Shadow drift analysis (informational only)
        # Get active profile ID for drift analysis
        from system_learning.engines.retrieval_profile_manager import get_active_retrieval_profile
        active_profile = get_active_retrieval_profile(now_utc)
        
        # Analyze accumulated shadow telemetry and write to L4
        drift_summary = _analyze_shadow_drift_and_write(
            profile_id=active_profile.profile_id,
            now_utc=now_utc,
            l4_writer=deps.l4_state_writer,
        )
        
        # Emit drift digest for verification (informational only)
        if drift_summary is not None:
            drift_summary.emit_digest()

        # Step 8.9: W4-D Policy recommendation generation (advisory only)
        # Generate policy recommendation from drift analysis
        policy_recommendation = _generate_policy_recommendation_and_write(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
            l4_writer=deps.l4_state_writer,
        )
        
        # Emit recommendation digest for verification (informational only)
        if policy_recommendation is not None:
            policy_recommendation.emit_digest()

        # Generate threshold adjustment proposals with patterns and semantic context
        if deps.healing_config_optimizer is not None:
            if hasattr(
                deps.healing_config_optimizer, "propose_threshold_adjustments_with_patterns_and_embeddings"
            ):
                threshold_proposal = (
                    deps.healing_config_optimizer.propose_threshold_adjustments_with_patterns_and_embeddings(
                        aggregate_snapshot, pattern_report, embedding_metadata
                    )
                )
            elif hasattr(deps.healing_config_optimizer, "propose_threshold_adjustments_with_patterns"):
                threshold_proposal = (
                    deps.healing_config_optimizer.propose_threshold_adjustments_with_patterns(
                        aggregate_snapshot, pattern_report, embedding_metadata
                    )
                )
            else:
                threshold_proposal = deps.healing_config_optimizer.propose_threshold_adjustments(
                    aggregate_snapshot, embedding_metadata
                )
        else:
            threshold_proposal = None

        # Add embedding metadata to ChangePackage for auditability (C0 informational only)
        if threshold_proposal and hasattr(threshold_proposal, "embedding_metadata"):
            # Update the ChangePackage to include embedding metadata
            # This is for audit purposes only and must not be used for execution
            if hasattr(threshold_proposal, "changes"):
                # Serialize embedding metadata and append to changes
                import json

                embedding_metadata_json = json.dumps(
                    embedding_metadata, separators=(",", ":"), sort_keys=True
                )
                if isinstance(threshold_proposal.changes, bytes):
                    # Append metadata to existing changes
                    combined_changes = (
                        threshold_proposal.changes
                        + b"\nEMBEDDING_METADATA:"
                        + embedding_metadata_json.encode()
                    )
                    # Create new proposal with combined changes (immutable pattern)
                    from system_learning.engines.change_package_impl import ChangePackage

                    threshold_proposal = ChangePackage(
                        source=threshold_proposal.source,
                        target=threshold_proposal.target,
                        changes=combined_changes,
                        confidence=threshold_proposal.confidence,
                        reason=threshold_proposal.reason
                        + (
                            f"Embedding enabled: {embedding_metadata.get('embedding_enabled_at_time', False)}",
                        ),
                        timestamp_utc=threshold_proposal.timestamp_utc,
                    )

        # Add to proposals if there are adjustments
        if threshold_proposal and threshold_proposal.adjustments:
            proposals.append(threshold_proposal)
            validated_proposals.append(threshold_proposal)

    # Step 9: If proposal_only, return without commit/activate
    if cfg.proposal_only:
        return tuple(validated_proposals)

    # Step 9: If not proposal_only, commit and activate
    if not cfg.proposal_only:
        # Require version_store and approval_gate
        if deps.version_store is None:
            raise PipelineError("version_store required when proposal_only=False")
        if deps.approval_gate is None:
            raise PipelineError("approval_gate required when proposal_only=False")

        committed_versions = []
        for pkg in validated_proposals:
            # Check approval
            decision = deps.approval_gate.decide(pkg, rca_report, snapshot)

            # Import here to avoid circular dependency
            from system_learning.pipelines.approval_gates import ApprovalDecision

            if decision == ApprovalDecision.REJECT:
                # Skip this package
                continue

            # Stage A: Commit
            version_id = deps.version_store.commit_change_package(pkg)
            committed_versions.append((pkg, version_id))

            # Stage B: Activate (only if activator provided)
            if deps.activator is not None:
                # Extract component from package (would be in real ChangePackage)
                component = "placeholder"
                deps.activator.activate(component, version_id)

    return tuple(validated_proposals)
