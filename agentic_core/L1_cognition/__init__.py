"""Sovereign Layer: L1_cognition"""

from typing import Any, Dict, List, Optional, Protocol

from agentic_core.L1_cognition.identity.spiffe_manager_impl import SPIFFEManager
from agentic_core.L1_cognition.identity.spiffe_manager_types import (
    AgentIdentity,
    IdentityType,
    IdentityVerificationResult,
    TrustDomain,
)
from agentic_core.L1_cognition.inference.inference_engine import (
    AnthropicClientWrapper,
    GenericOpenAICompatibleClientWrapper,
    GoogleClientWrapper,
    HardStateProtocol,
    InferenceEngine,
    InferenceMode,
    InferenceRequest,
    InferenceResult,
    OpenAIClientWrapper,
    Provider,
    SignalContextProtocol,
    ThermostatMiddleware,
)
from agentic_core.L1_cognition.inference.signal_anchoring import (
    ClaimExtractor,
    ClaimType,
    ExtractedClaim,
    HardState,
    SignalAnchor,
    SignalContext,
    SignedClaim,
    SourceMetadata,
    SourceType,
)
from agentic_core.L1_cognition.P1_interfaces.config import (
    ActionConfig,
    CognitiveConfig,
    OrchestratorConfig,
)
from agentic_core.L1_cognition.P1_interfaces.execution import (
    ExecutionContext,
    ExecutionPhase,
    ExecutionResult,
)
from agentic_core.L1_cognition.P1_interfaces.governance import (
    ArchitectureGovernor,
    DependencyGraph,
)
from agentic_core.L1_cognition.P1_interfaces.planes import (
    IActionPlane,
    ICognitivePlane,
    IOrchestrator,
)
from agentic_core.L1_cognition.P1_interfaces.requests import (
    ActionRequest,
    ActionResult,
    PlanningRequest,
    PlanningResult,
)
from agentic_core.L1_cognition.P2_domain.context import (
    BudgetManager,
    DependencyGraph,
    ValidationContext,
)
from agentic_core.L1_cognition.P5_meta.reflection_agent import ReflectionAgent
from agentic_core.L1_cognition.planning.capability_analyzer_impl import (
    CapabilityAnalyzer,
)
from agentic_core.L1_cognition.planning.capability_analyzer_types import (
    AnalysisReport,
    CapabilityGap,
    CapabilityGapType,
    Recommendation,
    RecommendationType,
)
from agentic_core.L1_cognition.planning.deprecated_full_workflow import (
    TestEndToEndWorkflow,
    TestWorkflowConfiguration,
    TestWorkflowPerformance,
)
from agentic_core.L1_cognition.planning.deprecated_integration_security import (
    TestBasicSecurityIntegration,
    TestEndToEndSecurityFlow,
)
from agentic_core.L1_cognition.planning.l5_injection_detection import (
    TestInjectionDetector,
    TestInjectionSafetyPolicy,
    TestIntegrationWithOtherLayers,
)
from agentic_core.L1_cognition.planning.metacognition_hypothesis_generation import (
    DummyAgentCard,
    DummyRAG,
)
from agentic_core.L1_cognition.thought_engine.agent_registry_enums import (
    AgentCapability,
    AgentStatus,
)

__all__ = ['AgentCapability', 'AgentStatus', 'SPIFFEManager', 'IdentityType', 'TrustDomain', 'AgentIdentity', 'IdentityVerificationResult', 'HardStateProtocol', 'SignalContextProtocol', 'Provider', 'OpenAIClientWrapper', 'AnthropicClientWrapper', 'GoogleClientWrapper', 'GenericOpenAICompatibleClientWrapper', 'InferenceMode', 'InferenceRequest', 'InferenceResult', 'ThermostatMiddleware', 'InferenceEngine', 'SignedClaim', 'HardState', 'SignalContext', 'ClaimType', 'SourceType', 'SourceMetadata', 'ExtractedClaim', 'ClaimExtractor', 'SignalAnchor', 'OrchestratorConfig', 'CognitiveConfig', 'ActionConfig', 'ExecutionPhase', 'ExecutionContext', 'ExecutionResult', 'DependencyGraph', 'ArchitectureGovernor', 'ICognitivePlane', 'IActionPlane', 'IOrchestrator', 'ActionRequest', 'ActionResult', 'PlanningRequest', 'PlanningResult', 'DependencyGraph', 'BudgetManager', 'ValidationContext', 'ReflectionAgent', 'CapabilityAnalyzer', 'CapabilityGapType', 'RecommendationType', 'CapabilityGap', 'Recommendation', 'AnalysisReport', 'TestEndToEndWorkflow', 'TestWorkflowConfiguration', 'TestWorkflowPerformance', 'TestBasicSecurityIntegration', 'TestEndToEndSecurityFlow', 'TestInjectionDetector', 'TestInjectionSafetyPolicy', 'TestIntegrationWithOtherLayers', 'DummyRAG', 'DummyAgentCard']
