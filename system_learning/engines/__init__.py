"""System Learning engines — concrete implementations for ports."""

# Wave 1: Core Pipeline Infrastructure
from system_learning.engines.case_compilation_engine import (
    CaseCompilationEngine,
    CaseRecordBuilder,
    SealedOutputReader,
)
from system_learning.engines.signal_aggregator_engine import (
    AggregatedSignalBundle,
    PreferenceGrade,
    SignalAggregatorEngine,
    TelemetryMetric,
)

# Wave 2: Evaluation Components (B, C, D)
from system_learning.engines.g_gate_regression_checker import GGateRegressionChecker
from system_learning.engines.outcome_evaluation_engine import (
    ExecutionTraceReader,
    GroundednessChecker,
    OutcomeEvaluationEngine,
)
from system_learning.engines.trajectory_evaluation_engine import TrajectoryEvaluationEngine

# Wave 3: System Learning Pipeline (Steps 6-7)
from system_learning.engines.rule_drafting_engine import (
    RuleDraftingEngine,
    RuleDraftingResult,
    RuleProposal,
)
from system_learning.engines.approval_gauntlet_engine import (
    ApprovalGauntletEngine,
    ApprovalDecision,
    ApprovalGauntletResult,
)

# Wave 4: Control & Calibration (Components A, F)
from system_learning.engines.live_exit_control_gate import (
    LiveExitControlGate,
    ExitControlResult,
)
from system_learning.engines.human_calibration_engine import (
    HumanCalibrationEngine,
    CalibrationRecord,
    HumanJudgment,
)
from system_learning.engines.stage_barrier_enforcer import (
    StageBarrierEnforcer,
    MetaLearningStage,
)

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
