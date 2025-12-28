"""
Sovereign Core Contracts Registry – Final SSOT Import Point (Phase 2C Complete)

All schema definitions have been fully migrated to agentic_core/schemas/.
This file is now a pure, minimal registry that dynamically imports from the canonical schema modules.
No model definitions are permitted here.
"""

# 1. Base Models
from agentic_core.schemas.base import SovereignBaseModel, Territory

# 2. Messaging & Communication
from agentic_core.schemas.messaging import (
    AgentMessage,
    ResidualAgentMessage,
    MessageType,
)

# 3. Tool Arguments
from agentic_core.schemas.tool_args import (
    ReadFileArgs,
    WriteFileArgs,
    MoveFileArgs,
    ListFilesArgs,
    ExecuteCommandArgs,
    DeleteFileArgs,
    CreateDirectoryArgs,
)

# 4. Reasoning & Cognitive Core
from agentic_core.schemas.reasoning import (
    AgentThoughtProcess,
    CodeGenerationResult,
    ResearchResult,
    AgentPlan,
)

# 5. Consensus & Deliberation
from agentic_core.schemas.consensus import ConsensusVerdict, ModelOpinion

# 6. Style & Generation
from agentic_core.schemas.tone import (
    ToneType,
    StyleProfile,
    GenerationConfig,
)

# 7. Micro-Runtime & Execution
from agentic_core.schemas.runtime_micro import (
    MicroStage,
    HopState,
    RetryPolicy,
    MicroCheckpoint,
    StageTransition,
)

# 8. Governance & Injection
from agentic_core.schemas.injection import (
    InjectionType,
    InjectionScope,
    InjectionPattern,
)

# 9. Context Passport (Flattened Option A)
from agentic_core.schemas.context_passport import (
    ThermalProfile,
    ThermalConfig,
    HardState,
    SoftState,
    SignedClaim,
    SignalContext,
)

# 10. System Profiles
from agentic_core.schemas.profiles import SafetyProfile, BudgetProfile

# 11. Simulation & Metacognition
from agentic_core.schemas.simulation import SimScenario, SimOutcome
from agentic_core.schemas.metacognition import Hypothesis, MetacognitionReport

# 12. Golden State & Benchmarking
from agentic_core.schemas.golden_state import (
    GoldenStateTestCase,
    JudgeVerdict,
    EvalResult,
    GoldenCase,
    GoldenOutput,
)

# 13. Runtime Shared (Phase 2C Residuals)
from agentic_core.schemas.runtime_shared import (
    LLMResponse,
    AgentResponse,
    ResidualValidationResult,
    ReasoningConfig,
    HopStatus,
    GateDecision,
    ValidationSeverity,
    WorkflowCheckpoint,
    ThematicAnalysis,
    RAGState,
    CircuitState,
)

# 14. Legacy Registry from core_contracts.py
from agentic_core.schemas.models.core_contracts import CORE_CONTRACTS_REGISTRY

# Final Centralized SSOT Registry
FINAL_REGISTRY = {
    "SovereignBaseModel": SovereignBaseModel,
    "Territory": Territory,
    "AgentMessage": AgentMessage,
    "ResidualAgentMessage": ResidualAgentMessage,
    "MessageType": MessageType,
    "ReadFileArgs": ReadFileArgs,
    "WriteFileArgs": WriteFileArgs,
    "MoveFileArgs": MoveFileArgs,
    "ListFilesArgs": ListFilesArgs,
    "ExecuteCommandArgs": ExecuteCommandArgs,
    "DeleteFileArgs": DeleteFileArgs,
    "CreateDirectoryArgs": CreateDirectoryArgs,
    "AgentThoughtProcess": AgentThoughtProcess,
    "CodeGenerationResult": CodeGenerationResult,
    "ResearchResult": ResearchResult,
    "AgentPlan": AgentPlan,
    "ConsensusVerdict": ConsensusVerdict,
    "ModelOpinion": ModelOpinion,
    "ToneType": ToneType,
    "StyleProfile": StyleProfile,
    "GenerationConfig": GenerationConfig,
    "MicroStage": MicroStage,
    "HopState": HopState,
    "RetryPolicy": RetryPolicy,
    "MicroCheckpoint": MicroCheckpoint,
    "StageTransition": StageTransition,
    "InjectionType": InjectionType,
    "InjectionScope": InjectionScope,
    "InjectionPattern": InjectionPattern,
    "ThermalProfile": ThermalProfile,
    "HardState": HardState,
    "SoftState": SoftState,
    "ThermalConfig": ThermalConfig,
    "SignedClaim": SignedClaim,
    "SignalContext": SignalContext,
    "SafetyProfile": SafetyProfile,
    "BudgetProfile": BudgetProfile,
    "SimScenario": SimScenario,
    "SimOutcome": SimOutcome,
    "Hypothesis": Hypothesis,
    "MetacognitionReport": MetacognitionReport,
    "GoldenStateTestCase": GoldenStateTestCase,
    "JudgeVerdict": JudgeVerdict,
    "EvalResult": EvalResult,
    "GoldenCase": GoldenCase,
    "GoldenOutput": GoldenOutput,
    "LLMResponse": LLMResponse,
    "AgentResponse": AgentResponse,
    "ResidualValidationResult": ResidualValidationResult,
    "ReasoningConfig": ReasoningConfig,
    "HopStatus": HopStatus,
    "GateDecision": GateDecision,
    "ValidationSeverity": ValidationSeverity,
    "WorkflowCheckpoint": WorkflowCheckpoint,
    "ThematicAnalysis": ThematicAnalysis,
    "RAGState": RAGState,
    "CircuitState": CircuitState,
}

# Merge with legacy registry for backward compatibility
CORE_CONTRACTS_REGISTRY.update(FINAL_REGISTRY)

__all__ = ["CORE_CONTRACTS_REGISTRY"] + list(CORE_CONTRACTS_REGISTRY.keys())