
# TODO: GRAVITY VIOLATION AUTO-HEALED
# Downstream imports removed — move shared logic to apps_shared or sovereign utils
# Original violation: GRAVITY VIOLATION: Upstream 'agentic_core' imports downstream roots: ['apps_rg']. Move shared logic to apps_shared or sovereign utils.
# Removed: apps_rg.engines.tone


# TODO: GRAVITY VIOLATION AUTO-HEALED
# Downstream imports removed — move shared logic to apps_shared or sovereign utils
# Original violation: GRAVITY VIOLATION: Upstream 'agentic_core' imports downstream roots: ['apps_lic']. Move shared logic to apps_shared or sovereign utils.
# Removed: apps_lic.engines.runtime_shared


# TODO: GRAVITY VIOLATION AUTO-HEALED
# Downstream imports removed — move shared logic to apps_shared or sovereign utils
# Original violation: GRAVITY VIOLATION: Upstream 'agentic_core' imports downstream roots: ['apps_lic']. Move shared logic to apps_shared or sovereign utils.
# Removed: apps_lic.engines.profiles


# TODO: GRAVITY VIOLATION AUTO-HEALED
# Downstream imports removed — move shared logic to apps_shared or sovereign utils
# Original violation: GRAVITY VIOLATION: Upstream 'agentic_core' imports downstream roots: ['apps_lic']. Move shared logic to apps_shared or sovereign utils.
# Removed: apps_lic.engines.messaging

from __future__ import annotations
"""
Sovereign Core Contracts Registry – Final SSOT Import Point (Phase 2C Complete)

All schema definitions have been fully migrated to agentic_core/schemas/.
This file is now a pure, minimal registry that dynamically imports from the canonical schema modules.
No model definitions are permitted here.
"""

# 1. Base Models
from agentic_core.schemas.models.base import SovereignBaseModel, Territory

# 5. Consensus & Deliberation
from agentic_core.schemas.models.consensus import ConsensusVerdict, ModelOpinion

# 9. Context Passport (Flattened Option A)
from agentic_core.schemas.models.context_passport import (
    HardState,
    SignalContext,
    SignedClaim,
    SoftState,
    ThermalConfig,
    ThermalProfile,
)

# 14. Legacy Registry from core_contracts.py

# 12. Golden State & Benchmarking
from agentic_core.schemas.models.golden_state import (
    EvalResult,
    GoldenCase,
    GoldenOutput,
    GoldenStateTestCase,
    JudgeVerdict,
)

# 8. Governance & Injection
from agentic_core.schemas.models.injection import (
    InjectionPattern,
    InjectionScope,
    InjectionType,
)

# 2. Messaging & Communication
    AgentMessage,
    MessageType,
    ResidualAgentMessage,
)
from agentic_core.schemas.models.metacognition import Hypothesis, MetacognitionReport

# 10. System Profiles

# 4. Reasoning & Cognitive Core
from agentic_core.schemas.models.reasoning import (
    AgentPlan,
    AgentThoughtProcess,
    CodeGenerationResult,
    ResearchResult,
)

# 7. Micro-Runtime & Execution
from agentic_core.L4_state.ValidationContext.runtime_micro import (
    HopState,
    MicroCheckpoint,
    MicroStage,
    RetryPolicy,
    StageTransition,
)

# 13. Runtime Shared (Phase 2C Residuals)
    AgentResponse,
    CircuitState,
    GateDecision,
    HopStatus,
    LLMResponse,
    RAGState,
    ReasoningConfig,
    ResidualValidationResult,
    ThematicAnalysis,
    ValidationSeverity,
    WorkflowCheckpoint,
)

# 11. Simulation & Metacognition
from agentic_core.schemas.models.simulation import SimOutcome, SimScenario

# 6. Style & Generation
    GenerationConfig,
    StyleProfile,
    ToneType,
)

# 3. Tool Arguments
from agentic_core.schemas.models.tool_args import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ExecuteCommandArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)

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