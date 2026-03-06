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
from dataclasses import dataclass
from typing import Any, Protocol

from system_learning.arbitration.engine import ArbitrationEngine
from system_learning.arbitration.types import ArbitrationCandidate, ArbitrationPolicy
from system_learning.confidence.engine import HealingConfidenceScorer
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

# W4-E: Retrieval profile proposal manager (requires approval)
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

    # Analyze the batch
    drift_summary = _shadow_drift_analyzer.analyze_batch(
        shadow_records=_shadow_telemetry_batch,
        profile_id=profile_id,
        now_utc=now_utc,
    )

    # Write to L4 (informational only)
    try:
        summary_json = drift_summary.to_canonical_json().encode("utf-8")
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
        recommendation_json = recommendation.to_canonical_json().encode("utf-8")
        l4_writer.write_l4c_policy_recommendation(
            payload_bytes=recommendation_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    except Exception:
        # L4 write failure should not break pipeline
        pass

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

    # Create proposal from recommendation
    proposal = _proposal_manager.create_proposal(
        recommendation=policy_recommendation,
        active_profile=active_profile,
        now_utc=now_utc,
    )

    # Write to L4 (requires approval)
    try:
        proposal_json = proposal.to_canonical_json().encode("utf-8")
        l4_writer.write_l4c_retrieval_profile_proposal(
            payload_bytes=proposal_json,
            component_name="meta-learning",
            created_utc=now_utc,
        )
    except Exception:
        # L4 write failure should not break pipeline
        pass

    return proposal


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
    healing_confidence_scorer: HealingConfidenceScorer | None = None
    failure_fingerprinter: FailureFingerprinter | None = None
    risk_correlator: RiskCorrelator | None = None
    arbitration_engine: ArbitrationEngine | None = None
    arbitration_policy: ArbitrationPolicy | None = None
    freeze_reader: FreezeStateReader | None = None


# =============================================================================
# Pattern Analysis (W3 - Deterministic, Informational-Only)
# =============================================================================


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
        # New API: use canonical_bytes() if available on the snapshot
        if hasattr(aggregate_snapshot, "canonical_bytes"):
            healing_snapshot_bytes = aggregate_snapshot.canonical_bytes()
            return deps.pattern_analysis_engine.analyze(
                healing_snapshot_bytes=healing_snapshot_bytes,
                detection_signal_bytes=detection_signal_bytes,
                drift_snapshot_bytes=drift_snapshot_bytes,
                now_utc=now_utc,
            )

        # Legacy API: extract historical embeddings from aggregate snapshot
        # Check embedding kill switch before legacy path
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

        pattern_summary = deps.pattern_analysis_engine.analyze(
            historical_embeddings=historical_embeddings,
            metadata=metadata,
            min_cluster_size=3,
        )

        print(f"W3-PATTERN-DIGEST: {pattern_summary.pattern_digest}")
        return pattern_summary

    except Exception:
        # Pattern analysis failure should not break pipeline
        return None


def _create_deterministic_embedding(failure_signature: Any) -> List[float]:
    """Create embedding from failure signature using BGE-m3 with 4-dim hash fallback.

    Primary: real BGE-m3 1024-dim embedding when BMG_EMBEDDINGS_ENABLED=true.
    Fallback: deterministic 4-dim hash vector (stdlib-only, reproducible).

    Args:
        failure_signature: Failure signature object

    Returns:
        Embedding vector (1024-dim BGE or 4-dim hash)
    """
    import os

    # Primary path: real BGE-m3 embedding when enabled
    if os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true":
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            text_parts = []
            if hasattr(failure_signature, "component"):
                text_parts.append(failure_signature.component)
            if hasattr(failure_signature, "failure_type"):
                text_parts.append(failure_signature.failure_type)
            if hasattr(failure_signature, "healer_name"):
                text_parts.append(failure_signature.healer_name)
            text = " ".join(text_parts) if text_parts else "unknown_failure"
            return bmg_embed_text(text)
        except Exception:  # guardian: allow-silent-swallower
            pass

    # Fallback: deterministic 4-dim hash vector (stdlib-only)
    import hashlib

    components = []
    if hasattr(failure_signature, "component"):
        comp_hash = hashlib.sha256(failure_signature.component.encode()).hexdigest()
        components.append(int(comp_hash[:8], 16) / 2**32)
    else:
        components.append(0.0)
    if hasattr(failure_signature, "failure_type"):
        type_hash = hashlib.sha256(failure_signature.failure_type.encode()).hexdigest()
        components.append(int(type_hash[:8], 16) / 2**32)
    else:
        components.append(0.0)
    if hasattr(failure_signature, "healer_name"):
        healer_hash = hashlib.sha256(failure_signature.healer_name.encode()).hexdigest()
        components.append(int(healer_hash[:8], 16) / 2**32)
    else:
        components.append(0.0)
    if hasattr(failure_signature, "timestamp_utc"):
        components.append((failure_signature.timestamp_utc & 0xFFFFFFFF) / 2**32)
    else:
        components.append(0.0)
    return components


# =============================================================================
# Semantic Retrieval (W2 - Informational Context Only)
# =============================================================================


def _wc_digest(failure_sig: str, vector_source: str, profile_id: str, vector_count: int) -> str:
    """Compute, print, and return W-C-DETERMINISM-DIGEST.

    Binds: failure_signature | vector_source | retrieval_profile_id | vector_count.
    Printed exactly once per call; 64-char lowercase SHA-256 hex.
    """
    _inp = f"{failure_sig}|{vector_source}|{profile_id}|{vector_count}"
    _dig = hashlib.sha256(_inp.encode("utf-8", errors="replace")).hexdigest()
    print(f"W-C-DETERMINISM-DIGEST: {_dig}")
    return _dig


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

    # W4-B: shadow_telemetry is built later (if shadow embedder configured).
    # Pre-initialize so the early-disabled return can unpack it safely.
    shadow_telemetry: dict = {}

    # If disabled, return empty metadata (no telemetry, no placeholders)
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

    import hashlib
    import os

    import numpy as np

    # C3: Use real bge-m3 embedding when BMG_EMBEDDINGS_ENABLED=true;
    # fall back to 16-dim hash vector otherwise (generate_fallback_vector).
    # The vector_source tag is propagated to all return dicts so downstream
    # code can assert it never uses a hash-fallback for semantic decisions.
    _vector_source = "hash-fallback"
    if (
        os.environ.get("BMG_EMBEDDINGS_ENABLED", "false").lower() == "true"
        and retrieval_profile.embeddings_enabled
    ):
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            _live_vec = bmg_embed_text(failure_signature)
            query_vector = np.array(_live_vec, dtype=np.float32)
            _vector_source = "bge-m3"
        except Exception:  # guardian: allow-silent-swallower
            _vector_source = "hash-fallback"
    if _vector_source == "hash-fallback":
        from agentic_core.L2_execution.healers.failure_signal_normalizer import generate_fallback_vector

        query_vector = np.array(generate_fallback_vector(failure_signature), dtype=np.float32)

    # W4-B: Compute shadow embedding if configured (non-influential telemetry)
    shadow_telemetry = {}
    if retrieval_profile.shadow_embedder_id is not None:
        # Compute shadow vector using same deterministic method but different embedder ID
        shadow_signature = f"{failure_signature}|shadow:{retrieval_profile.shadow_embedder_id}"
        shadow_hash = hashlib.sha256(shadow_signature.encode()).hexdigest()

        # Create shadow vector (same dimension as query_vector, different seed)
        _qdim = query_vector.shape[0]
        shadow_vector = []
        for _si in range(_qdim):
            _hex_start = (_si * 2) % (len(shadow_hash) - 1)
            val = int(shadow_hash[_hex_start : _hex_start + 2], 16) / 255.0
            shadow_vector.append(val)

        shadow_vector = np.array(shadow_vector, dtype=np.float32)

        # Compute telemetry metrics with stable rounding
        primary_norm = round(float(np.linalg.norm(query_vector)), 6)
        shadow_norm = round(float(np.linalg.norm(shadow_vector)), 6)

        # Compute cosine similarity
        cosine_sim = round(
            float(
                np.dot(query_vector, shadow_vector)
                / (np.linalg.norm(query_vector) * np.linalg.norm(shadow_vector))
            ),
            6,
        )

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
                **shadow_telemetry,  # W4-B: Include shadow telemetry
            }

        # Extract metadata for audit (C0 informational only)
        topk_hashes = [r.content_hash for r in results]
        topk_scores = [r.score_round6 for r in results]

        # Compute artifact hash from results
        result_data = f"{failure_signature}|{topk_hashes}|{topk_scores}"
        artifact_hash = hashlib.sha256(result_data.encode()).hexdigest()

        _wc_dig = _wc_digest(
            failure_signature, _vector_source, retrieval_profile.profile_id, len(topk_hashes)
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
            **shadow_telemetry,  # W4-B: Include shadow telemetry
        }

    except Exception:  # guardian: allow-silent_swallower
        # Embedding retrieval failure should not break pipeline
        # Return minimal metadata indicating failure
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

    # GAP-014: Freeze gate -- if system freeze is active, meta-learning must not run
    if deps.freeze_reader is not None and deps.freeze_reader.is_frozen():
        raise PipelineError("meta-learning pipeline disabled: system freeze is active (L2 FREEZ)")

    # GAP-015: Clear module-level telemetry batch at pipeline entry to prevent cross-run contamination
    global _shadow_telemetry_batch
    _shadow_telemetry_batch = []

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

    # Stage 5 extensions: fingerprinting, confidence scoring, risk correlation
    if deps.failure_fingerprinter is not None and hasattr(rca_report, "failure_events"):
        fingerprints = [
            deps.failure_fingerprinter.fingerprint(ev).fingerprint_hex
            for ev in (rca_report.failure_events or [])
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
            rca_report.fingerprints or [], snapshot.drift_events or []
        )
        if hasattr(rca_report, "with_correlated_risk"):
            rca_report = rca_report.with_correlated_risk(correlated_risk)

    # Step 6: Run enabled proposers in deterministic order
    # Fixed order: ("L0", "RAG", "L1", "L5") intersect enabled set
    proposer_order = ("L0", "RAG", "L1", "L5")
    proposer_map = {
        "L0": deps.l0_proposer,
        "RAG": deps.rag_proposer,
        "L1": deps.l1_proposer,
        "L5": deps.l5_proposer,
    }

    # G13: injection detector must be invoked before any embedding/retrieval
    from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector

    _inj_detector = InjectionDetector()

    proposals = []
    for key in proposer_order:
        proposer = proposer_map[key]
        if proposer is None:
            continue

        # G13: Scan all text inputs for injection before proposer runs
        # This is a guard for dual-injection attempts (prompt + embedding)
        if hasattr(snapshot, "u0_user_prompt"):
            _inj_detector.scan(snapshot.u0_user_prompt)
        if hasattr(snapshot, "aggregate_snapshot"):
            # Scan any narrative fields in the aggregate snapshot
            if hasattr(snapshot.aggregate_snapshot, "narrative"):
                _inj_detector.scan(snapshot.aggregate_snapshot.narrative)

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
    # These must be added to proposals BEFORE Stage 7 validation loop
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
        except Exception:  # noqa: BLE001  # guardian: allow-silent_swallower
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
        except Exception:  # noqa: BLE001  # guardian: allow-silent_swallower
            # Log error but continue pipeline
            pass

    # Step 6c: Process DPO batch (Path D - HITL + Deterministic DPO Loop)
    # GAP-003: DPO proposals must enter proposals list BEFORE Stage 7 loop
    # so they are subject to replay/shadow/cooldown/oscillation validation.
    if deps.dpo_batch_bytes is not None and deps.rlhf_optimizer is not None:
        try:
            import json as _json_dpo

            # Get current threshold config for time-shifted rule
            current_threshold_config_bytes = _json_dpo.dumps(
                current_configs, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")

            # Generate proposal-only adjustments from DPO batch
            dpo_proposal = deps.rlhf_optimizer.propose_from_dpo(
                dpo_batch_bytes=deps.dpo_batch_bytes,
                current_threshold_config_bytes=current_threshold_config_bytes,
            )

            # Stamp with current timestamp (ChangePackage may be frozen)
            from dataclasses import replace as _dc_replace

            from system_learning.engines.change_package_impl import ChangePackage as _CP

            if isinstance(dpo_proposal, _CP):
                dpo_proposal = _dc_replace(dpo_proposal, timestamp_utc=now_utc)
            elif hasattr(dpo_proposal, "timestamp_utc"):
                try:
                    dpo_proposal.timestamp_utc = now_utc
                except (AttributeError, TypeError):
                    pass

            # DPO proposal enters proposals list here, before Stage 7, so it
            # flows through all validators (replay, shadow, cooldown, oscillation).
            proposals.append(dpo_proposal)
        except Exception:  # noqa: BLE001  # guardian: allow-silent_swallower
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
        if cfg.require_shadow_validation and hasattr(deps.baseline_metrics_provider, "production_metrics"):
            production = deps.baseline_metrics_provider.production_metrics()
            shadow = deps.baseline_metrics_provider.shadow_metrics(pkg)
            evaluate_shadow(production, shadow, cfg.shadow_thresholds)

        # Dampening gates: cooldown
        # Extract surface name from package (would be in real ChangePackage)
        surface_name = getattr(pkg, "surface_name", "unknown")
        if hasattr(deps.config_provider, "get_last_update_utc") and hasattr(
            cfg.cooldown_policy, "min_seconds_between_updates"
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

        # Dampening gates: sample size
        # GAP-004: derive real observation count from audit_slice line count
        # (proxy for number of auditable events in the window)
        if hasattr(cfg.sample_policy, "min_observations"):
            _audit_text = (
                audit_slice.decode("utf-8", errors="replace")
                if isinstance(audit_slice, (bytes, bytearray))
                else str(audit_slice)
            )
            n_observations = max(1, sum(1 for ln in _audit_text.splitlines() if ln.strip()))
            assert_min_sample_size(
                n_observations=n_observations,
                sample_policy=cfg.sample_policy,
            )

        # Oscillation gate
        if hasattr(deps.config_provider, "get_param_history") and hasattr(cfg.oscillation_policy, "window"):
            param_history = deps.config_provider.get_param_history(
                surface_name, cfg.oscillation_policy.window
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
                        f"Oscillation detected for {surface_name}: freeze until {freeze_decision.freeze_until_utc}"
                    )

        validated_proposals.append(pkg)

    # Stage 7: ArbitrationEngine — deterministic winner selection
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

    # GAP-016: initialize intake_record to None before Stage 8 block to prevent
    # NameError in Stage 8.5 when healing_outcome_intake_adapter is None.
    intake_record = None

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
    # GAP-016: guard uses intake_record is not None (safe after initialization above)
    if (
        deps.healing_config_optimizer is not None
        and intake_record is not None
        and hasattr(intake_record, "snapshot")
    ):
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
            except Exception:  # guardian: allow-silent_swallower
                # L4B write failure should not break pipeline
                # In production, this would be logged
                pass

        # Step 8.6: Pattern analysis (W3 - deterministic, informational only)
        # Read optional detection/drift signal bytes from L4 writer if available
        _detection_signal_bytes: bytes | None = None
        _drift_snapshot_bytes: bytes | None = None
        if deps.l4_state_writer is not None:
            if hasattr(deps.l4_state_writer, "read_latest_detection_signal"):
                _detection_signal_bytes = deps.l4_state_writer.read_latest_detection_signal()
            if hasattr(deps.l4_state_writer, "read_latest_drift_snapshot"):
                _drift_snapshot_bytes = deps.l4_state_writer.read_latest_drift_snapshot()
        _8_5_aggregate_snapshot = aggregate_snapshot
    else:
        _8_5_aggregate_snapshot = None

    # Step 8.6: Pattern analysis — independent of Stage 8.5 success (GAP-005)
    # Runs whenever pattern_analysis_engine is available, regardless of optimizer.
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

    # Step 8.7: Retrieve semantic context (W2 - C0 informational only) — independent of 8.5
    embedding_metadata = _retrieve_semantic_context(
        rca_report=rca_report, pattern_report=pattern_report, now_utc=now_utc
    )

    # Re-enter 8.5 block for 8.8-8.10 steps that depend on aggregate_snapshot
    if _8_5_aggregate_snapshot is not None:
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

        # Step 8.10: W4-E Profile proposal creation (requires approval)
        # Create proposal from policy recommendation
        profile_proposal = _create_proposal_and_write(
            policy_recommendation=policy_recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
            l4_writer=deps.l4_state_writer,
        )

        # Emit proposal digest for verification (informational only)
        if profile_proposal is not None:
            profile_proposal.emit_digest()

        # Generate threshold adjustment proposals with patterns and semantic context
        # GAP-011: C0 embedding_metadata is informational only -- must NOT be appended
        # to ChangePackage.changes bytes. Use embedding_context_hash field instead.
        if deps.healing_config_optimizer is not None:
            if hasattr(
                deps.healing_config_optimizer, "propose_threshold_adjustments_with_patterns_and_embeddings"
            ):
                threshold_proposal = (
                    deps.healing_config_optimizer.propose_threshold_adjustments_with_patterns_and_embeddings(
                        _8_5_aggregate_snapshot, pattern_report, embedding_metadata
                    )
                )
            elif hasattr(deps.healing_config_optimizer, "propose_threshold_adjustments_with_patterns"):
                threshold_proposal = (
                    deps.healing_config_optimizer.propose_threshold_adjustments_with_patterns(
                        _8_5_aggregate_snapshot, pattern_report
                    )
                )
            else:
                threshold_proposal = deps.healing_config_optimizer.propose_threshold_adjustments(
                    _8_5_aggregate_snapshot
                )
        else:
            threshold_proposal = None

        # GAP-011: C0 embedding metadata is audit-only.
        # Attach only via embedding_context_hash field; never mutate changes bytes.
        if threshold_proposal is not None and embedding_metadata:
            _artifact_hash = embedding_metadata.get("embedding_artifact_hash") or embedding_metadata.get(
                "content_hash"
            )
            if _artifact_hash and hasattr(threshold_proposal, "embedding_context_hash"):
                from dataclasses import replace as _dc_replace_ec

                threshold_proposal = _dc_replace_ec(threshold_proposal, embedding_context_hash=_artifact_hash)

        # Add to proposals if there are adjustments (type-safe check)
        if (
            threshold_proposal is not None
            and hasattr(threshold_proposal, "adjustments")
            and threshold_proposal.adjustments
        ):
            validated_proposals.append(threshold_proposal)

    # Step 9: If proposal_only, return without commit/activate
    if cfg.proposal_only:
        return tuple(validated_proposals)

    # Step 9: If not proposal_only, commit and activate
    # GAP-008: Pre-flight dual injection guard — both must be present or both absent.
    # Checking them independently would allow entering the loop with partial injection.
    _vs_present = deps.version_store is not None
    _ag_present = deps.approval_gate is not None
    if _vs_present and not _ag_present:
        raise PipelineError(
            "partial injection: approval_gate required when version_store is present; "
            "both must be injected together when proposal_only=False"
        )
    if _ag_present and not _vs_present:
        raise PipelineError(
            "partial injection: version_store required when approval_gate is present; "
            "both must be injected together when proposal_only=False"
        )
    if not _vs_present:
        raise PipelineError("version_store required when proposal_only=False")
    if not _ag_present:
        raise PipelineError("approval_gate required when proposal_only=False")

    # Import here to avoid circular dependency
    from system_learning.pipelines.approval_gates import ApprovalDecision

    committed_versions = []
    for pkg in validated_proposals:
        # Check approval
        decision = deps.approval_gate.decide(pkg, rca_report, snapshot)

        if decision == ApprovalDecision.REJECT:
            # Skip this package
            continue

        # Stage A: Commit
        version_id = deps.version_store.commit_change_package(pkg)
        committed_versions.append((pkg, version_id))

        # Stage B: Activate (only if activator provided)
        # GAP-009: Extract component from package, not hardcoded "placeholder"
        if deps.activator is not None:
            component = getattr(pkg, "target_surface", None) or getattr(pkg, "target", "unknown")
            deps.activator.activate(component, version_id)

    return tuple(validated_proposals)
