"""System Learning engines — concrete implementations for ports.

Imports here are wrapped in a fail-soft block: if a transitive dependency is
missing under some test contexts (e.g., pytest collection where conftest
shims may shadow real ``agentic_core`` subpackages), the package still loads
so that v7 modules with no such dependencies (``v7_kpi_board``,
``schema_normalizer``, etc.) remain importable.
"""

# Defensive eager imports — every block is independently fail-safe so a
# missing transitive dependency in one engine does not cascade to break
# unrelated v7 engine modules that happen to share this package namespace.
try:  # Wave 1: Core Pipeline Infrastructure
    from system_learning.engines.approval_gauntlet_engine import (  # noqa: F401
        ApprovalDecision,
        ApprovalGauntletEngine,
        ApprovalGauntletResult,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass
try:
    from system_learning.engines.case_compilation_engine import (  # noqa: F401
        CaseCompilationEngine,
        CaseRecordBuilder,
        SealedOutputReader,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass

try:  # Wave 2: Evaluation Components (B, C, D)
    from system_learning.engines.g_gate_regression_checker import (  # noqa: F401
        GGateRegressionChecker,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass
try:
    from system_learning.engines.human_calibration_engine import (  # noqa: F401
        CalibrationRecord,
        HumanCalibrationEngine,
        HumanJudgment,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass

try:  # Wave 4: Control & Calibration (Components A, F)
    from system_learning.engines.live_exit_control_gate import (  # noqa: F401
        ExitControlResult,
        LiveExitControlGate,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass
try:
    from system_learning.engines.outcome_evaluation_engine import (  # noqa: F401
        ExecutionTraceReader,
        GroundednessChecker,
        OutcomeEvaluationEngine,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass

try:  # Wave 3: System Learning Pipeline (Steps 6-7)
    from system_learning.engines.rule_drafting_engine import (  # noqa: F401
        RuleDraftingEngine,
        RuleDraftingResult,
        RuleProposal,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass
try:
    from system_learning.engines.signal_aggregator_engine import (  # noqa: F401
        AggregatedSignalBundle,
        PreferenceGrade,
        SignalAggregatorEngine,
        TelemetryMetric,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass
try:
    from system_learning.engines.stage_barrier_enforcer import (  # noqa: F401
        MetaLearningStage,
        StageBarrierEnforcer,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass
try:
    from system_learning.engines.trajectory_evaluation_engine import (  # noqa: F401
        TrajectoryEvaluationEngine,
    )
except ImportError:  # guardian: allow-log-and-swallow -- transitive dep may be absent under shimmed pytest collection
    pass

__all__ = [
    # Wave 1: Core Pipeline
    "CaseCompilationEngine",
    "CaseRecordBuilder",
    "SealedOutputReader",
    "AggregatedSignalBundle",
    "PreferenceGrade",
    "SignalAggregatorEngine",
    "TelemetryMetric",
    # Wave 2: Evaluation Engines
    "GGateRegressionChecker",
    "ExecutionTraceReader",
    "GroundednessChecker",
    "OutcomeEvaluationEngine",
    "TrajectoryEvaluationEngine",
    # Wave 3: Rule Drafting & Approval
    "RuleDraftingEngine",
    "RuleDraftingResult",
    "RuleProposal",
    "ApprovalGauntletEngine",
    "ApprovalDecision",
    "ApprovalGauntletResult",
    # Wave 4: Exit Control & Calibration
    "LiveExitControlGate",
    "ExitControlResult",
    "HumanCalibrationEngine",
    "CalibrationRecord",
    "HumanJudgment",
    # Stage Barrier Enforcer
    "StageBarrierEnforcer",
    "MetaLearningStage",
]
