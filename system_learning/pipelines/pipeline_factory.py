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
    from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy
    from system_learning.validators.oscillation_detector import OscillationPolicy
    from system_learning.validators.shadow_evaluator import ShadowThresholds

    return PipelineConfig(
        engine_version="0.1.0",
        config_surface_version="0.1.0",
        shadow_thresholds=ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=15.0,
            max_mem_regression_pct=15.0,
            forbid_any_safety_violation_increase=True,
        ),
        cooldown_policy=CooldownPolicy(min_seconds_between_updates=3600),
        sample_policy=SampleSizePolicy(min_observations=10),
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
    from system_learning.engines.l4_state_writer import FileBackedL4StateWriter
    from system_learning.engines.rag_proposer import RAGParameterProposer
    from system_learning.pipelines.meta_learning_pipeline import PipelineDependencies
    from system_learning.stores.audit_store import FileBackedAuditStore
    from system_learning.stores.config_provider import (
        FileBackedConfigProvider,
        InMemoryBaselineMetricsProvider,
    )
    from system_learning.stores.telemetry_store import InMemoryTelemetryStore

    from .healing_backups.naming_violations.l0_threshold_tuner_2 import L0ProposerAdapter
    from .healing_backups.naming_violations.l1_model_proposer_1 import L1ModelProposer
    from .healing_backups.naming_violations.l5_policy_proposer_1 import L5PolicyProposer

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
    except ImportError:
        logger.debug("PatternAnalysisEngine not available; skipping.")

    optimizer = healing_config_optimizer
    if optimizer is None:
        try:
            from system_learning.engines.healing_config_optimizer import HealingConfigOptimizer

            optimizer = HealingConfigOptimizer()
        except ImportError:
            logger.debug("HealingConfigOptimizer not available; skipping.")

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
    )


__all__ = [
    "build_pipeline_config",
    "build_pipeline_deps",
]
