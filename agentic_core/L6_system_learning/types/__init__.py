"""System Learning type definitions."""

# Re-exports are done via direct imports from submodules to avoid circular imports.
# Import directly from system_learning.types.meta_learning_types, etc.

# Wave 1: Case Compilation types
from agentic_core.L6_system_learning.engines.approval_gauntlet_engine import (
    ApprovalDecision,
    ApprovalGauntletEngine,
    ApprovalGauntletResult,
)
from agentic_core.L6_system_learning.engines.human_calibration_engine import (
    CalibrationRecord,
    HumanCalibrationEngine,
    HumanJudgment,
)

# Wave 4: Exit Control and Calibration types (defined in engine modules)
from agentic_core.L6_system_learning.engines.live_exit_control_gate import (
    ExitControlResult,
    LiveExitControlGate,
)

# Wave 3: Rule Drafting types (defined in engine module)
from agentic_core.L6_system_learning.engines.rule_drafting_engine import (
    RuleDraftingEngine,
    RuleDraftingResult,
    RuleProposal,
)
from .case_compilation_types import (
    CaseCompilationResult,
    CompilationInput,
    CompilationPayload,
    CompilationStage,
    ContextLogAttachment,
    SealedOutputRef,
)

# Wave 2: Evaluation Spine types
from .evaluation_spine_types import (
    GGateValidationResult,
    MetricScore,
    OutcomeEvaluationResult,
    TrajectoryEvaluationResult,
)

__all__ = [
    # Wave 1: Case Compilation types
    "CaseCompilationResult",
    "CompilationInput",
    "CompilationPayload",
    "CompilationStage",
    "ContextLogAttachment",
    "SealedOutputRef",
    # Wave 2: Evaluation Spine types
    "GGateValidationResult",
    "MetricScore",
    "OutcomeEvaluationResult",
    "TrajectoryEvaluationResult",
    # Wave 3: Rule Drafting & Approval types
    "RuleDraftingEngine",
    "RuleDraftingResult",
    "RuleProposal",
    "ApprovalGauntletEngine",
    "ApprovalDecision",
    "ApprovalGauntletResult",
    # Wave 4: Exit Control & Calibration types
    "LiveExitControlGate",
    "ExitControlResult",
    "HumanCalibrationEngine",
    "CalibrationRecord",
    "HumanJudgment",
]


__layer__ = "L6"
__l6_chapter__ = ""  # cross-cutting (no single chapter)
