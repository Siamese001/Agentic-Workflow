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
]
