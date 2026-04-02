"""
Agent Taxonomy Registry - Canonical classification of all agents.

This module maintains the canonical taxonomy mapping for all agents
in the system, ensuring every agent is classified into one of the
seven canonical roles.

Generated: Wave 1 of Agent Taxonomy & Healing Standardization Hardening
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L2_execution.contracts.l2_execution_contract import CanonicalAgentRole

__all__ = [
    "AgentClassification",
    "AgentTaxonomyRegistry",
    "AGENT_TAXONOMY_MAP",
]


class AgentStatus(Enum):
    """Status of an agent in the taxonomy."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SHIM = "shim"
    PLANNED = "planned"
    OBSOLETE = "obsolete"


@dataclass(frozen=True, slots=True)
class AgentClassification:
    """Canonical classification for a single agent."""

    file_path: str
    class_name: str
    current_layer: str
    canonical_role: CanonicalAgentRole
    status: AgentStatus
    is_shim: bool
    implements_l2_contract: bool
    notes: str = ""


class AgentTaxonomyRegistry:
    """Registry maintaining canonical taxonomy for all agents."""

    def __init__(self):
        self._agents: dict[str, AgentClassification] = {}

    def register(self, classification: AgentClassification) -> None:
        """Register an agent classification."""
        key = f"{classification.file_path}:{classification.class_name}"
        self._agents[key] = classification

    def get_by_path(self, file_path: str) -> list[AgentClassification]:
        """Get all agent classifications for a file path."""
        return [a for a in self._agents.values() if a.file_path == file_path]

    def get_by_role(self, role: CanonicalAgentRole) -> list[AgentClassification]:
        """Get all agents with a specific canonical role."""
        return [a for a in self._agents.values() if a.canonical_role == role]

    def get_by_layer(self, layer: str) -> list[AgentClassification]:
        """Get all agents in a specific layer."""
        return [a for a in self._agents.values() if a.current_layer == layer]

    def get_shims(self) -> list[AgentClassification]:
        """Get all shim agents marked for deprecation."""
        return [a for a in self._agents.values() if a.is_shim or a.status == AgentStatus.SHIM]

    def get_l2_noncompliant(self) -> list[AgentClassification]:
        """Get all L2 agents not yet implementing the L2 contract."""
        return [
            a
            for a in self._agents.values()
            if a.current_layer == "L2"
            and a.canonical_role == CanonicalAgentRole.EXECUTION
            and not a.implements_l2_contract
        ]

    def count_by_role(self) -> dict[CanonicalAgentRole, int]:
        """Count agents by canonical role."""
        counts: dict[CanonicalAgentRole, int] = dict.fromkeys(CanonicalAgentRole, 0)
        for agent in self._agents.values():
            counts[agent.canonical_role] += 1
        return counts

    def generate_report(self) -> dict[str, Any]:
        """Generate a comprehensive taxonomy report."""
        by_role = self.count_by_role()
        total = len(self._agents)
        shims = len(self.get_shims())
        l2_noncompliant = len(self.get_l2_noncompliant())

        return {
            "total_agents": total,
            "by_canonical_role": {r.value: c for r, c in by_role.items()},
            "shim_count": shims,
            "l2_noncompliant": l2_noncompliant,
            "wave_1_pilot_agents": len(
                [a for a in self._agents.values() if a.file_path.startswith("agentic_core/base_agents")]
            ),
            "wave_2_hop_agents": len(
                [a for a in self._agents.values() if "Hop" in a.class_name or "HOP" in a.class_name]
            ),
        }


# Wave 1: Canonical Taxonomy Mapping
# This map contains the authoritative classification for all agents
# as determined by architectural analysis of the codebase.

AGENT_TAXONOMY_MAP: dict[str, AgentClassification] = {
    # ============================================
    # L0: ROUTING AGENTS
    # ============================================
    "RootCustomsAgent": AgentClassification(
        file_path="agentic_core/L0_routing/reasoning/RootCustomsAgent.py",
        class_name="RootCustomsAgent",
        current_layer="L0",
        canonical_role=CanonicalAgentRole.ROUTER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Root routing agent for L0 customs/validation",
    ),
    "SSOTFolderCleanupAgent": AgentClassification(
        file_path="agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py",
        class_name="SSOTFolderCleanupAgent",
        current_layer="L0",
        canonical_role=CanonicalAgentRole.ROUTER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Folder cleanup routing agent",
    ),
    # ============================================
    # L1: PLANNER AGENTS
    # ============================================
    "ASTValidatorAgent": AgentClassification(
        file_path="agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py",
        class_name="ASTValidatorAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="AST-based validation planner",
    ),
    "MetaLearningAgent": AgentClassification(
        file_path="agentic_core/L1_cognition/reasoning/MetaLearningAgent.py",
        class_name="MetaLearningAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Meta-learning strategy planner",
    ),
    "StrategicRecommendationAgent": AgentClassification(
        file_path="agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py",
        class_name="StrategicRecommendationAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Strategic recommendation planner",
    ),
    # ============================================
    # L2: EXECUTION AGENTS (Core)
    # ============================================
    "StructuredEngineAgent": AgentClassification(
        file_path="agentic_core/L2_execution/reasoning/StructuredEngineAgent.py",
        class_name="StructuredEngineAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Core structured execution engine. WAVE 5: L2 contract compliant.",
    ),
    "SovereignMCPGatewayAgent": AgentClassification(
        file_path="agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py",
        class_name="SovereignMCPGatewayAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="MCP gateway execution agent. WAVE 5: L2 contract compliant.",
    ),
    "RedisSovereignAgent": AgentClassification(
        file_path="agentic_core/L2_execution/reasoning/RedisSovereignAgent.py",
        class_name="RedisSovereignAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Redis execution agent. WAVE 5: L2 contract compliant.",
    ),
    "EmbeddingSovereignAgent": AgentClassification(
        file_path="agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
        class_name="EmbeddingSovereignAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Embedding execution agent. WAVE 5: L2 contract compliant.",
    ),
    "SubAtomicRegistryAgent": AgentClassification(
        file_path="agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py",
        class_name="SubAtomicRegistryAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Registry execution agent. WAVE 5: L2 contract compliant.",
    ),
    "ToolsmithAgent": AgentClassification(
        file_path="agentic_core/L2_execution/reasoning/ToolsmithAgent.py",
        class_name="ToolsmithAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Tool management execution agent. WAVE 5: L2 contract compliant.",
    ),
    # ============================================
    # L3: ORCHESTRATOR AGENTS
    # ============================================
    "CoverageAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/CoverageAgent.py",
        class_name="CoverageAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Coverage analysis orchestrator",
    ),
    "DAGMutatorAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py",
        class_name="DAGMutatorAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="DAG mutation orchestrator",
    ),
    "DagEngineAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
        class_name="DagEngineAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="DAG execution engine orchestrator",
    ),
    "DagRuntimeInspectorAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py",
        class_name="DagRuntimeInspectorAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="DAG runtime inspection - L6 observer role",
    ),
    "DomainPlannerAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py",
        class_name="DomainPlannerAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Domain planning orchestrator",
    ),
    "FissionManagerAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py",
        class_name="FissionManagerAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Fission management orchestrator",
    ),
    "GravityStateAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/GravityStateAgent.py",
        class_name="GravityStateAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Gravity state orchestrator",
    ),
    "NervousSystemAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
        class_name="NervousSystemAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Nervous system orchestrator",
    ),
    "OrchestrationHandshakeAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py",
        class_name="OrchestrationHandshakeAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Orchestration handshake coordinator",
    ),
    "SemanticGatekeeperAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py",
        class_name="SemanticGatekeeperAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Semantic gatekeeper - L5 safety role",
    ),
    "StateManagementAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/StateManagementAgent.py",
        class_name="StateManagementAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="State management orchestrator",
    ),
    "SubAtomicAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
        class_name="SubAtomicAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Sub-atomic orchestrator",
    ),
    "SubatomicHopAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
        class_name="SubatomicHopAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Sub-atomic HOP orchestrator",
    ),
    "UnifiedAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
        class_name="UnifiedAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Unified orchestration agent",
    ),
    # ============================================
    # APPS_LIC: HOP PIPELINE AGENTS (All Shims → HOPPipelineExecutor)
    # ============================================
    "HOP1ProfileAnalysisAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop1ProfileAnalysisAgent.py",
        class_name="HOP1ProfileAnalysisAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 1: Profile analysis/planning",
    ),
    "HOP2ResearchAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop2ResearchAgent.py",
        class_name="HOP2ResearchAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 2: Research execution",
    ),
    "HOP3SenderGroundingAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP3SenderGroundingAgent.py",
        class_name="HOP3SenderGroundingAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 3: Sender grounding execution",
    ),
    "HOP4RoutingAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop4RoutingAgent.py",
        class_name="HOP4RoutingAgent",
        current_layer="L0",
        canonical_role=CanonicalAgentRole.ROUTER,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 4: Routing",
    ),
    "HOP5GenerationAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP5GenerationAgent.py",
        class_name="HOP5GenerationAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 5: Content generation execution",
    ),
    "HOP6ValidationAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop6ValidationAgent.py",
        class_name="HOP6ValidationAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 6: Validation/safety check",
    ),
    "HOP7GateDecisionAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP7GateDecisionAgent.py",
        class_name="HOP7GateDecisionAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 7: Gate decision/safety",
    ),
    "HOP8QAReportAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP8QAReportAgent.py",
        class_name="HOP8QAReportAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 8: QA reporting/observation",
    ),
    "HOP9IntegrationAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP9IntegrationAgent.py",
        class_name="HOP9IntegrationAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → HOPPipelineExecutor. Stage 9: Integration orchestration",
    ),
    "HOPPipelineExecutor": AgentClassification(
        file_path="apps_lic/reasoning/HOPPipelineExecutor.py",
        class_name="HOPPipelineExecutor",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Canonical HOP executor consolidating HOP1-HOP9. WAVE 2 TARGET for L2 contract",
    ),
    # ============================================
    # APPS_RG: RESUME GENERATOR AGENTS
    # ============================================
    "ProactiveAgent": AgentClassification(
        file_path="apps_rg/reasoning/ProactiveAgent.py",
        class_name="ProactiveAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="RG proactive task execution agent. Subclasses BaseProactiveAgent.",
    ),
    "HeadlineOutputAgent": AgentClassification(
        file_path="apps_rg/reasoning/HeadlineOutputAgent.py",
        class_name="HeadlineOutputAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Executive title composer (K.4). Full L2 execution agent.",
    ),
    "ExecutiveSummaryOutputAgent": AgentClassification(
        file_path="apps_rg/reasoning/ExecutiveSummaryOutputAgent.py",
        class_name="ExecutiveSummaryOutputAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Strategist BioWriter (K.1). Full L2 execution agent.",
    ),
    "ResumeAssemblyAgent": AgentClassification(
        file_path="apps_rg/reasoning/ResumeAssemblyAgent.py",
        class_name="ResumeAssemblyAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Resume assembly execution agent.",
    ),
    "SectionBalanceAgent": AgentClassification(
        file_path="apps_rg/reasoning/SectionBalanceAgent.py",
        class_name="SectionBalanceAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Section balance execution agent.",
    ),
    "ContentQualityAgent": AgentClassification(
        file_path="apps_rg/reasoning/ContentQualityAgent.py",
        class_name="ContentQualityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Content quality execution agent.",
    ),
    "DispatchResumeToolsAgent": AgentClassification(
        file_path="apps_rg/reasoning/DispatchResumeToolsAgent.py",
        class_name="DispatchResumeToolsAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Tool dispatch execution agent.",
    ),
    "RgReflectionAgent": AgentClassification(
        file_path="apps_rg/reasoning/RgReflectionAgent.py",
        class_name="RgReflectionAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="RG reflection/observation agent (L6).",
    ),
    "RgStrategicPlannerAgent": AgentClassification(
        file_path="apps_rg/reasoning/RgStrategicPlannerAgent.py",
        class_name="RgStrategicPlannerAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="RG strategic planning agent (L1).",
    ),
    "RgTemplateOptimizerAgent": AgentClassification(
        file_path="apps_rg/reasoning/RgTemplateOptimizerAgent.py",
        class_name="RgTemplateOptimizerAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Template optimization execution agent.",
    ),
    # RG Shims
    "FactCheckAgent": AgentClassification(
        file_path="apps_rg/reasoning/FactCheckAgent.py",
        class_name="FactCheckAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → RGValidationExecutor. Use canonical executor directly.",
    ),
    "ATSCompatibilityAgent": AgentClassification(
        file_path="apps_rg/reasoning/ATSCompatibilityAgent.py",
        class_name="ATSCompatibilityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → RGValidationExecutor. Use canonical executor directly.",
    ),
    "BrandComplianceAgent": AgentClassification(
        file_path="apps_rg/reasoning/BrandComplianceAgent.py",
        class_name="BrandComplianceAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → RGValidationExecutor. Use canonical executor directly.",
    ),
    "CampaignPlannerAgent": AgentClassification(
        file_path="apps_rg/reasoning/CampaignPlannerAgent.py",
        class_name="CampaignPlannerAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="RETIRED/EMPTY. Consolidated out of active agent pool (2026-02-08).",
    ),
    # ============================================
    # APPS_EVAL: EVALUATION AGENTS
    # ============================================
    "TestDiscoveryAgent": AgentClassification(
        file_path="apps_eval/reasoning/TestDiscoveryAgent.py",
        class_name="TestDiscoveryAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Test discovery and cataloging agent (L6 observation).",
    ),
    "QualityGateAgent": AgentClassification(
        file_path="apps_eval/reasoning/QualityGateAgent.py",
        class_name="QualityGateAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Quality gate safety agent (L5).",
    ),
    "ScenarioGenerationAgent": AgentClassification(
        file_path="apps_eval/reasoning/ScenarioGenerationAgent.py",
        class_name="ScenarioGenerationAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Test scenario generation execution agent.",
    ),
    # ============================================
    # APPS_EXEC: EXECUTIVE BRIEFING AGENTS
    # ============================================
    "BriefAssemblyAgent": AgentClassification(
        file_path="apps_exec/reasoning/BriefAssemblyAgent.py",
        class_name="BriefAssemblyAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Executive brief assembly execution agent.",
    ),
    "SourceIngestionAgent": AgentClassification(
        file_path="apps_exec/reasoning/SourceIngestionAgent.py",
        class_name="SourceIngestionAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Source ingestion execution agent.",
    ),
    "StyleComplianceAgent": AgentClassification(
        file_path="apps_exec/reasoning/StyleComplianceAgent.py",
        class_name="StyleComplianceAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="Style compliance safety agent (L5).",
    ),
    # ============================================
    # L5 SAFETY AGENTS (Key Agents)
    # ============================================
    "GovernanceAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/GovernanceAgent.py",
        class_name="GovernanceAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 governance safety agent - can emit heal_blocked signals.",
    ),
    "CodeJanitorAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/CodeJanitorAgent.py",
        class_name="CodeJanitorAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 code janitor/healer safety agent.",
    ),
    "PascalSovereigntyAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py",
        class_name="PascalSovereigntyAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 Pascal naming sovereignty enforcer.",
    ),
    "HygieneGuardianAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py",
        class_name="HygieneGuardianAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 code hygiene guardian safety agent.",
    ),
    "PreCommitSovereignAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py",
        class_name="PreCommitSovereignAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 pre-commit safety enforcement agent.",
    ),
    "RedTeamAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/RedTeamAgent.py",
        class_name="RedTeamAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 adversarial red team safety agent.",
    ),
    "ConstitutionalReviewerAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py",
        class_name="ConstitutionalReviewerAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L5 constitutional compliance reviewer.",
    ),
    # ============================================
    # L6 OBSERVABILITY AGENTS
    # ============================================
    "PerformanceAnalystAgentSimple": AgentClassification(
        file_path="agentic_core/L6_observability/engines/PerformanceAnalystAgentSimple.py",
        class_name="PerformanceAnalystAgentSimple",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="L6 performance analysis observer agent.",
    ),
    # ============================================
    # APPS_LIC: REMAINING LIC AGENTS
    # ============================================
    "GovernanceShieldAgent": AgentClassification(
        file_path="apps_lic/reasoning/GovernanceShieldAgent.py",
        class_name="GovernanceShieldAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC governance shield safety agent.",
    ),
    "ExecutiveStrategyAgent": AgentClassification(
        file_path="apps_lic/reasoning/ExecutiveStrategyAgent.py",
        class_name="ExecutiveStrategyAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC executive strategy planner agent (L1).",
    ),
    "LicReflectionAgent": AgentClassification(
        file_path="apps_lic/reasoning/LicReflectionAgent.py",
        class_name="LicReflectionAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC reflection/observation agent (L6).",
    ),
    "LeadQualityAgent": AgentClassification(
        file_path="apps_lic/reasoning/LeadQualityAgent.py",
        class_name="LeadQualityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC lead quality execution agent.",
    ),
    "DeliverabilityAgent": AgentClassification(
        file_path="apps_lic/reasoning/DeliverabilityAgent.py",
        class_name="DeliverabilityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC deliverability execution agent.",
    ),
    "CampaignBalanceAgent": AgentClassification(
        file_path="apps_lic/reasoning/CampaignBalanceAgent.py",
        class_name="CampaignBalanceAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC campaign balance execution agent.",
    ),
    "OutreachMessageAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachMessageAgent.py",
        class_name="OutreachMessageAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC outreach message execution agent.",
    ),
    "MessageComplianceAgent": AgentClassification(
        file_path="apps_lic/reasoning/MessageComplianceAgent.py",
        class_name="MessageComplianceAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC message compliance safety agent (L5).",
    ),
    "MessageArchitectAgent": AgentClassification(
        file_path="apps_lic/reasoning/MessageArchitectAgent.py",
        class_name="MessageArchitectAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC message architect execution agent.",
    ),
    "OutreachValidationExecutorAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachValidationExecutorAgent.py",
        class_name="OutreachValidationExecutorAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC outreach validation executor.",
    ),
    "OutreachProactiveAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachProactiveAgent.py",
        class_name="OutreachProactiveAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC outreach proactive execution agent.",
    ),
    "OutreachSignalRouterAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachSignalRouterAgent.py",
        class_name="OutreachSignalRouterAgent",
        current_layer="L0",
        canonical_role=CanonicalAgentRole.ROUTER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC outreach signal router (L0).",
    ),
    "OutreachLearningAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachLearningAgent.py",
        class_name="OutreachLearningAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC outreach learning/planning agent (L1).",
    ),
    "IntelligenceLibrarianAgent": AgentClassification(
        file_path="apps_lic/reasoning/IntelligenceLibrarianAgent.py",
        class_name="IntelligenceLibrarianAgent",
        current_layer="L4",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC intelligence librarian state observer (L4).",
    ),
    "LicTemplateOptimizerAgent": AgentClassification(
        file_path="apps_lic/reasoning/LicTemplateOptimizerAgent.py",
        class_name="LicTemplateOptimizerAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC template optimizer execution agent.",
    ),
    "DispatchOutreachToolsAgent": AgentClassification(
        file_path="apps_lic/reasoning/DispatchOutreachToolsAgent.py",
        class_name="DispatchOutreachToolsAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC outreach tool dispatch execution agent.",
    ),
    "ValidatorAgent": AgentClassification(
        file_path="apps_lic/reasoning/ValidatorAgent.py",
        class_name="ValidatorAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=False,
        notes="LIC validation safety agent (L5).",
    ),
    # APPS_LIC Shims
    "ArchetypeIndicatorsAgent": AgentClassification(
        file_path="apps_lic/reasoning/ArchetypeIndicatorsAgent.py",
        class_name="ArchetypeIndicatorsAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.SHIM,
        is_shim=True,
        implements_l2_contract=False,
        notes="SHIM → apps_lic.config.archetype_indicator_config. Config-only now.",
    ),
}

def get_taxonomy_registry() -> AgentTaxonomyRegistry:
    """Get the populated taxonomy registry."""
    registry = AgentTaxonomyRegistry()
    for classification in AGENT_TAXONOMY_MAP.values():
        registry.register(classification)
    return registry
