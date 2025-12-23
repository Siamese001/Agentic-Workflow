"""Sovereign Layer: L1_cognition"""

from typing import Any, Optional, Protocol, Dict, List
from agentic_core.L1_cognition.discovery.agent_registry_enums import AgentCapability, AgentStatus
from agentic_core.L1_cognition.identity.spiffe_manager_impl import SPIFFEManager
from agentic_core.L1_cognition.identity.spiffe_manager_types import IdentityType, TrustDomain, AgentIdentity, IdentityVerificationResult
from agentic_core.L1_cognition.inference.inference_engine import HardStateProtocol, SignalContextProtocol, Provider, OpenAIClientWrapper, AnthropicClientWrapper, GoogleClientWrapper, GenericOpenAICompatibleClientWrapper, InferenceMode, InferenceRequest, InferenceResult, ThermostatMiddleware, InferenceEngine
from agentic_core.L1_cognition.inference.signal_anchoring import SignedClaim, HardState, SignalContext, ClaimType, SourceType, SourceMetadata, ExtractedClaim, ClaimExtractor, SignalAnchor
from agentic_core.L1_cognition.P1_interfaces.config import OrchestratorConfig, CognitiveConfig, ActionConfig
from agentic_core.L1_cognition.P1_interfaces.execution import ExecutionPhase, ExecutionContext, ExecutionResult
from agentic_core.L1_cognition.P1_interfaces.governance import DependencyGraph, ArchitectureGovernor
from agentic_core.L1_cognition.P1_interfaces.planes import ICognitivePlane, IActionPlane, IOrchestrator
from agentic_core.L1_cognition.P1_interfaces.requests import ActionRequest, ActionResult, PlanningRequest, PlanningResult
from agentic_core.L1_cognition.P2_domain.context import DependencyGraph, BudgetManager, ValidationContext
from agentic_core.L1_cognition.P5_meta.reflection_agent import ReflectionAgent
from agentic_core.L1_cognition.planning.capability_analyzer_impl import CapabilityAnalyzer
from agentic_core.L1_cognition.planning.capability_analyzer_types import CapabilityGapType, RecommendationType, CapabilityGap, Recommendation, AnalysisReport
from agentic_core.L1_cognition.planning.deprecated_full_workflow import TestEndToEndWorkflow, TestWorkflowConfiguration, TestWorkflowPerformance
from agentic_core.L1_cognition.planning.deprecated_integration_security import TestBasicSecurityIntegration, TestEndToEndSecurityFlow
from agentic_core.L1_cognition.planning.l5_injection_detection import TestInjectionDetector, TestInjectionSafetyPolicy, TestIntegrationWithOtherLayers
from agentic_core.L1_cognition.planning.metacognition_hypothesis_generation import DummyRAG, DummyAgentCard

__all__ = ['AgentCapability', 'AgentStatus', 'SPIFFEManager', 'IdentityType', 'TrustDomain', 'AgentIdentity', 'IdentityVerificationResult', 'HardStateProtocol', 'SignalContextProtocol', 'Provider', 'OpenAIClientWrapper', 'AnthropicClientWrapper', 'GoogleClientWrapper', 'GenericOpenAICompatibleClientWrapper', 'InferenceMode', 'InferenceRequest', 'InferenceResult', 'ThermostatMiddleware', 'InferenceEngine', 'SignedClaim', 'HardState', 'SignalContext', 'ClaimType', 'SourceType', 'SourceMetadata', 'ExtractedClaim', 'ClaimExtractor', 'SignalAnchor', 'OrchestratorConfig', 'CognitiveConfig', 'ActionConfig', 'ExecutionPhase', 'ExecutionContext', 'ExecutionResult', 'DependencyGraph', 'ArchitectureGovernor', 'ICognitivePlane', 'IActionPlane', 'IOrchestrator', 'ActionRequest', 'ActionResult', 'PlanningRequest', 'PlanningResult', 'DependencyGraph', 'BudgetManager', 'ValidationContext', 'ReflectionAgent', 'CapabilityAnalyzer', 'CapabilityGapType', 'RecommendationType', 'CapabilityGap', 'Recommendation', 'AnalysisReport', 'TestEndToEndWorkflow', 'TestWorkflowConfiguration', 'TestWorkflowPerformance', 'TestBasicSecurityIntegration', 'TestEndToEndSecurityFlow', 'TestInjectionDetector', 'TestInjectionSafetyPolicy', 'TestIntegrationWithOtherLayers', 'DummyRAG', 'DummyAgentCard']