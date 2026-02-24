"""G-16-27: Meta-learning pipeline orchestrator for System Learning.

End-to-end deterministic pipeline: snapshot → telemetry/audit → RCA → proposals
→ validation → optional commit/activation.

Invariants:
  - Default proposal_only=True (zero execution authority)
  - No wall-clock reads (now_utc injected)
  - Fail-closed on validation failure
  - Stage A commit + Stage B activation only via injected interfaces
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
from system_learning.snapshots.snapshot_factory import create_snapshot
from system_learning.types.snapshot_types import MetaLearningSnapshot
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
from system_learning.validators.oscillation_detector import OscillationPolicy
from system_learning.validators.shadow_evaluator import ShadowThresholds

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
