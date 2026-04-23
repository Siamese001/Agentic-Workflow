"""ADG Runtime package — indexed query engine, cache loader, and runtime graph infrastructure."""

from pathlib import Path

from agentic_core.adg.runtime.antipattern_registry import (
    AntipatternCategory,
    AntipatternRecord,
    AntipatternRegistry,
    AntipatternRegistryReport,
    AntipatternSeverity,
)
from agentic_core.adg.runtime.boundary_verifier import (
    BoundaryPacket,
    BoundaryVerificationResult,
    BoundaryVerifierReport,
    CapabilityChokepoint,
    L2BoundaryVerifier,
    VerificationOutcome,
)
from agentic_core.adg.runtime.cache_loader import invalidate_cache, load_or_scan
from agentic_core.adg.runtime.capability_budget import (
    BudgetEvent,
    BudgetExceededError,
    BudgetGovernorReport,
    BudgetStatus,
    ResourceGovernor,
    ResourceGrant,
    ToolBudget,
)
from agentic_core.adg.runtime.config_governance import (
    ConfigGovernanceReport,
    ConfigGovernor,
    ConfigReadEvent,
    ConfigReadOutcome,
    ConfigSchemaStatus,
)
from agentic_core.adg.runtime.determinism_control import (
    DeterminismController,
    DeterminismControlReport,
    DeterminismDigest,
    DeterminismViolation,
    DeterminismViolationType,
    ReplayGuard,
    ReplayPatchRecord,
    SemanticClock,
    SemanticClockReading,
)
from agentic_core.adg.runtime.dynamic_invocation import (
    DynamicInvocationKind,
    DynamicInvocationRecord,
    DynamicInvocationReport,
    DynamicInvocationRisk,
    DynamicInvocationTracker,
)
from agentic_core.adg.runtime.eval_spine import (
    DPOBatch,
    DriftAlert,
    EvalMetricResult,
    EvalSpine,
    EvalSpineReport,
    OptimizationProposal,
    OptimizationStage,
    PreferencePair,
)
from agentic_core.adg.runtime.event_graph import (
    AgentLoopRecorder,
    HealerLoopRecorder,
    HealerPhase,
    RuntimeEdge,
    RuntimeEvent,
    RuntimeGraph,
    RuntimeGraphCollector,
    RuntimePhase,
)
from agentic_core.adg.runtime.execution_proof import (
    ExecutionProofRecorder,
    ExecutionProofReport,
    ExecutionTrace,
    ProofComparison,
    ProofComparisonOutcome,
    ReplayKey,
)
from agentic_core.adg.runtime.healing_orchestrator import (
    HealingOrchestrator,
    HealingOrchestratorReport,
    HealingRun,
    HealingRunPhase,
    HealingTrigger,
    OrchestrationStep,
)
from agentic_core.adg.runtime.hitl_graph import (
    HITLCheckpoint,
    HITLDecisionType,
    HITLGraph,
    HITLRuntimeRecorder,
    HumanDecision,
)
from agentic_core.adg.runtime.io_interception import (
    InterceptionOutcome,
    IOInterceptionEvent,
    IOInterceptionReport,
    IOInterceptor,
    NetworkTranscript,
)
from agentic_core.adg.runtime.jit_context import (
    ContextSnapshot,
    FreezeBoundary,
    FreezeState,
    JITContextSession,
    JITContextSynchronizer,
)
from agentic_core.adg.runtime.mcp_drift_recorder import (
    MCPConfigSnapshot,
    MCPDriftEvent,
    MCPDriftRecorder,
    MCPDriftReport,
    MCPDriftSeverity,
    MCPDriftType,
    MCPServerState,
)
from agentic_core.adg.runtime.mutation_transport import (
    CommitPhase,
    MutationPacket,
    MutationTransport,
    MutationTransportReport,
    RFC6902Patch,
)
from agentic_core.adg.runtime.path_control import (
    ExecutionPath,
    ExecutionPathController,
    PathControlReport,
    PathTransition,
    PathTransitionReason,
)
from agentic_core.adg.runtime.policy_state_observer import (
    PolicyStateObserver,
    StateObservationEvent,
    StateObservationKind,
    StateObservationReport,
    StateReadOutcome,
)
from agentic_core.adg.runtime.query_engine import (
    ADGRuntimeQueryEngine,
    AgentCapability,
    DependencyPath,
    get_runtime_query_engine,
)
from agentic_core.adg.runtime.safety_observer import (
    GuardrailExecution,
    PolicyHashVerification,
    RuntimeSafetyObserver,
    RuntimeSafetyReport,
    SafetyViolation,
)
# sandbox_airlock archived to archives/adg_dead_code/2026-04-23/ (wave D, 2026-04-23).
# Zero external consumers of AirlockPhase / AirlockSession / CapabilityToken /
# SandboxAirlockRecorder / SandboxEnvelope / WorkContract from this module.
# (SandboxEnvelope consumers import from
#  agentic_core.L2_execution.types.sandbox_envelope_types — a different class.)
from agentic_core.adg.runtime.secret_access import (
    SecretAccessEvent,
    SecretAccessOutcome,
    SecretAccessRecorder,
    SecretAccessReport,
    SecretKind,
)

__all__ = [
    # Query engine
    "ADGRuntimeQueryEngine",
    "AgentCapability",
    "DependencyPath",
    "get_runtime_query_engine",
    "load_or_scan",
    "invalidate_cache",
    # G1 (gap): Runtime event graph
    "RuntimePhase",
    "HealerPhase",
    "RuntimeEvent",
    "RuntimeEdge",
    "RuntimeGraph",
    "RuntimeGraphCollector",
    "AgentLoopRecorder",
    "HealerLoopRecorder",
    # G4 (gap): HITL graph
    "HITLDecisionType",
    "HITLCheckpoint",
    "HumanDecision",
    "HITLGraph",
    "HITLRuntimeRecorder",
    # G5 (gap): Safety observer
    "GuardrailExecution",
    "PolicyHashVerification",
    "SafetyViolation",
    "RuntimeSafetyReport",
    "RuntimeSafetyObserver",
    # G7 (gap): Sandbox airlock / work-contract — module archived wave D 2026-04-23
    # G8 (gap): Capability-token / tool-budget
    "BudgetEvent",
    "BudgetExceededError",
    "BudgetGovernorReport",
    "BudgetStatus",
    "ResourceGovernor",
    "ResourceGrant",
    "ToolBudget",
    # G9 (gap): JIT context sync / freeze
    "ContextSnapshot",
    "FreezeBoundary",
    "FreezeState",
    "JITContextSession",
    "JITContextSynchronizer",
    # G10 (gap): Boundary verification
    "BoundaryPacket",
    "BoundaryVerificationResult",
    "BoundaryVerifierReport",
    "CapabilityChokepoint",
    "L2BoundaryVerifier",
    "VerificationOutcome",
    # G11 (gap): Determinism control
    "DeterminismControlReport",
    "DeterminismController",
    "DeterminismDigest",
    "DeterminismViolation",
    "DeterminismViolationType",
    "ReplayGuard",
    "ReplayPatchRecord",
    "SemanticClock",
    "SemanticClockReading",
    # G12 (gap): IO interception
    "IOInterceptionEvent",
    "IOInterceptionReport",
    "IOInterceptor",
    "InterceptionOutcome",
    "NetworkTranscript",
    # G13 (gap): Mutation transport
    "CommitPhase",
    "MutationPacket",
    "MutationTransport",
    "MutationTransportReport",
    "RFC6902Patch",
    # G14 (gap): Execution proof
    "ExecutionProofRecorder",
    "ExecutionProofReport",
    "ExecutionTrace",
    "ProofComparison",
    "ProofComparisonOutcome",
    "ReplayKey",
    # G15 (gap): Path control
    "ExecutionPath",
    "ExecutionPathController",
    "PathControlReport",
    "PathTransition",
    "PathTransitionReason",
    # G16 (gap): Evaluation spine
    "DPOBatch",
    "DriftAlert",
    "EvalMetricResult",
    "EvalSpine",
    "EvalSpineReport",
    "OptimizationProposal",
    "OptimizationStage",
    "PreferencePair",
    # G17 (gap): Secret / credential access
    "SecretAccessEvent",
    "SecretAccessOutcome",
    "SecretAccessRecorder",
    "SecretAccessReport",
    "SecretKind",
    # G18 (gap): Config governance
    "ConfigGovernanceReport",
    "ConfigGovernor",
    "ConfigReadEvent",
    "ConfigReadOutcome",
    "ConfigSchemaStatus",
    # G19 (gap): Dynamic invocation
    "DynamicInvocationKind",
    "DynamicInvocationRecord",
    "DynamicInvocationReport",
    "DynamicInvocationRisk",
    "DynamicInvocationTracker",
    # G20 (gap): Policy state observation
    "PolicyStateObserver",
    "StateObservationEvent",
    "StateObservationKind",
    "StateObservationReport",
    "StateReadOutcome",
    # G21 (gap): Anti-pattern registry
    "AntipatternCategory",
    "AntipatternRecord",
    "AntipatternRegistry",
    "AntipatternRegistryReport",
    "AntipatternSeverity",
    # G23 (gap): MCP drift detection
    "MCPConfigSnapshot",
    "MCPDriftEvent",
    "MCPDriftRecorder",
    "MCPDriftReport",
    "MCPDriftSeverity",
    "MCPDriftType",
    "MCPServerState",
    # G22 (gap): Healing orchestrator
    "HealingOrchestrator",
    "HealingOrchestratorReport",
    "HealingRun",
    "HealingRunPhase",
    "HealingTrigger",
    "OrchestrationStep",
]
