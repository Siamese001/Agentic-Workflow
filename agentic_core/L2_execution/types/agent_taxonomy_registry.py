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

from agentic_core.L2_execution.types.l2_execution_contract import CanonicalAgentRole

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
        implements_l2_contract=True,
        notes="Coverage analysis orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "DAGMutatorAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py",
        class_name="DAGMutatorAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="DAG mutation orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "DagEngineAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
        class_name="DagEngineAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="DAG execution engine orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "DagRuntimeInspectorAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py",
        class_name="DagRuntimeInspectorAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="DAG runtime inspection - L6 observer role. WAVE 7: Now L2 contract compliant.",
    ),
    "DomainPlannerAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py",
        class_name="DomainPlannerAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Domain planning orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "FissionManagerAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py",
        class_name="FissionManagerAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Fission management orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "GravityStateAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/GravityStateAgent.py",
        class_name="GravityStateAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Gravity state orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "NervousSystemAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
        class_name="NervousSystemAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Nervous system orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "OrchestrationHandshakeAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py",
        class_name="OrchestrationHandshakeAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Orchestration handshake coordinator. WAVE 7: Now L2 contract compliant.",
    ),
    "SemanticGatekeeperAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py",
        class_name="SemanticGatekeeperAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Semantic gatekeeper - L5 safety role. WAVE 7: Now L2 contract compliant.",
    ),
    "StateManagementAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/StateManagementAgent.py",
        class_name="StateManagementAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="State management orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "SubAtomicAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py",
        class_name="SubAtomicAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Sub-atomic orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "SubatomicHopAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
        class_name="SubatomicHopAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Sub-atomic HOP orchestrator. WAVE 7: Now L2 contract compliant.",
    ),
    "UnifiedAgent": AgentClassification(
        file_path="agentic_core/L3_orchestration/reasoning/UnifiedAgent.py",
        class_name="UnifiedAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Unified orchestration agent. WAVE 7: Now L2 contract compliant.",
    ),
    # ============================================
    # L4: STATE AGENTS
    # ============================================
    "IntelligenceLibrarianAgent": AgentClassification(
        file_path="agentic_core/L4_state/engines/IntelligenceLibrarianAgent.py",
        class_name="IntelligenceLibrarianAgent",
        current_layer="L4",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L4 state intelligence librarian observer. WAVE 7: Now L2 contract compliant.",
    ),
    # ============================================
    # APPS_LIC: Additional Agents
    "LicHealingOrchestrator": AgentClassification(
        file_path="apps_lic/reasoning/LicHealingOrchestrator.py",
        class_name="LicHealingOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC healing orchestrator agent. L2 contract compliant.",
    ),
    "LICValidationExecutor": AgentClassification(
        file_path="apps_lic/reasoning/LICValidationExecutor.py",
        class_name="LICValidationExecutor",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC validation executor agent. L2 contract compliant.",
    ),
    "LICCodeInterpreter": AgentClassification(
        file_path="apps_lic/reasoning/LicCodeInterpreter.py",
        class_name="LICCodeInterpreter",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC code interpreter tool agent. L2 contract compliant.",
    ),
    # ============================================
    "HOP1ProfileAnalysisAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop1ProfileAnalysisAgent.py",
        class_name="HOP1ProfileAnalysisAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP2ResearchAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop2ResearchAgent.py",
        class_name="HOP2ResearchAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP3SenderGroundingAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP3SenderGroundingAgent.py",
        class_name="HOP3SenderGroundingAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP4RoutingAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop4RoutingAgent.py",
        class_name="HOP4RoutingAgent",
        current_layer="L0",
        canonical_role=CanonicalAgentRole.ROUTER,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP5GenerationAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP5GenerationAgent.py",
        class_name="HOP5GenerationAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP6ValidationAgent": AgentClassification(
        file_path="apps_lic/reasoning/Hop6ValidationAgent.py",
        class_name="HOP6ValidationAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP7GateDecisionAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP7GateDecisionAgent.py",
        class_name="HOP7GateDecisionAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP8QAReportAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP8QAReportAgent.py",
        class_name="HOP8QAReportAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOP9IntegrationAgent": AgentClassification(
        file_path="apps_lic/reasoning/HOP9IntegrationAgent.py",
        class_name="HOP9IntegrationAgent",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → HOPPipelineExecutor. File removed.",
    ),
    "HOPPipelineExecutor": AgentClassification(
        file_path="apps_lic/reasoning/HOPPipelineExecutor.py",
        class_name="HOPPipelineExecutor",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Canonical HOP executor consolidating HOP1-HOP9. WAVE 6: Now L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="RG proactive task execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "HeadlineOutputAgent": AgentClassification(
        file_path="apps_rg/reasoning/HeadlineOutputAgent.py",
        class_name="HeadlineOutputAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Executive title composer (K.4). Full L2 execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "ExecutiveSummaryOutputAgent": AgentClassification(
        file_path="apps_rg/reasoning/ExecutiveSummaryOutputAgent.py",
        class_name="ExecutiveSummaryOutputAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Strategist BioWriter (K.1). Full L2 execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "ResumeAssemblyAgent": AgentClassification(
        file_path="apps_rg/reasoning/ResumeAssemblyAgent.py",
        class_name="ResumeAssemblyAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Resume assembly execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "SectionBalanceAgent": AgentClassification(
        file_path="apps_rg/reasoning/SectionBalanceAgent.py",
        class_name="SectionBalanceAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → RGValidationExecutor. File removed.",
    ),
    "ContentQualityAgent": AgentClassification(
        file_path="apps_rg/reasoning/ContentQualityAgent.py",
        class_name="ContentQualityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Content quality execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "DispatchResumeToolsAgent": AgentClassification(
        file_path="apps_rg/reasoning/DispatchResumeToolsAgent.py",
        class_name="DispatchResumeToolsAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Tool dispatch execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "RgReflectionAgent": AgentClassification(
        file_path="apps_rg/reasoning/RgReflectionAgent.py",
        class_name="RgReflectionAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="RG reflection/observation agent (L6). WAVE 8: Now L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="Template optimization execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    # APPS_RG: Additional Orchestrator Agents
    "RGStrategyExecutor": AgentClassification(
        file_path="apps_rg/reasoning/RGStrategyExecutor.py",
        class_name="RGStrategyExecutor",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="RG strategy executor agent. L2 contract compliant.",
    ),
    "RGValidationExecutor": AgentClassification(
        file_path="apps_rg/reasoning/RGValidationExecutor.py",
        class_name="RGValidationExecutor",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="RG validation executor agent. L2 contract compliant.",
    ),
    "ResumeOrchestrator": AgentClassification(
        file_path="apps_rg/reasoning/ResumeOrchestrator.py",
        class_name="ResumeOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Resume orchestrator agent. L2 contract compliant.",
    ),
    "RgResumeOrchestrator": AgentClassification(
        file_path="apps_rg/reasoning/RgResumeOrchestrator.py",
        class_name="RgResumeOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="RG resume orchestrator agent. L2 contract compliant.",
    ),
    "ResumeEnhancementOrchestrator": AgentClassification(
        file_path="apps_rg/reasoning/ResumeEnhancementOrchestrator.py",
        class_name="ResumeEnhancementOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Resume enhancement orchestrator agent. L2 contract compliant.",
    ),
    "RgHealingOrchestrator": AgentClassification(
        file_path="apps_rg/reasoning/RgHealingOrchestrator.py",
        class_name="RgHealingOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="RG healing orchestrator agent. L2 contract compliant.",
    ),
    "FactCheckAgent": AgentClassification(
        file_path="apps_rg/reasoning/FactCheckAgent.py",
        class_name="FactCheckAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → RGValidationExecutor. File removed.",
    ),
    "ATSCompatibilityAgent": AgentClassification(
        file_path="apps_rg/reasoning/ATSCompatibilityAgent.py",
        class_name="ATSCompatibilityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → RGValidationExecutor. File removed.",
    ),
    "BrandComplianceAgent": AgentClassification(
        file_path="apps_rg/reasoning/BrandComplianceAgent.py",
        class_name="BrandComplianceAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → RGValidationExecutor. File removed.",
    ),
    "CampaignPlannerAgent": AgentClassification(
        file_path="apps_rg/reasoning/CampaignPlannerAgent.py",
        class_name="CampaignPlannerAgent",
        current_layer="L1",
        canonical_role=CanonicalAgentRole.PLANNER,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was RETIRED/EMPTY shim. File removed.",
    ),
    # APPS_EVAL: Additional Orchestrator Agents
    "EvalOrchestrator": AgentClassification(
        file_path="apps_eval/reasoning/EvalOrchestrator.py",
        class_name="EvalOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Evaluation orchestrator agent. L2 contract compliant.",
    ),
    "EnterpriseEvalOrchestrator": AgentClassification(
        file_path="apps_eval/reasoning/enterprise_eval_orchestrator.py",
        class_name="EnterpriseEvalOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Enterprise evaluation orchestrator agent. L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="Test discovery and cataloging agent (L6 observation). WAVE 8: Now L2 contract compliant.",
    ),
    "QualityGateAgent": AgentClassification(
        file_path="apps_eval/reasoning/QualityGateAgent.py",
        class_name="QualityGateAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Quality gate safety agent (L5). WAVE 8: Now L2 contract compliant.",
    ),
    "ScenarioGenerationAgent": AgentClassification(
        file_path="apps_eval/reasoning/ScenarioGenerationAgent.py",
        class_name="ScenarioGenerationAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Test scenario generation execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    # APPS_EXEC: Additional Orchestrator Agents
    "ExecOrchestrator": AgentClassification(
        file_path="apps_exec/reasoning/ExecOrchestrator.py",
        class_name="ExecOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Executive briefing orchestrator agent. L2 contract compliant.",
    ),
    "EnterpriseBriefOrchestrator": AgentClassification(
        file_path="apps_exec/reasoning/enterprise_brief_orchestrator.py",
        class_name="EnterpriseBriefOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Enterprise brief orchestrator agent. L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="Executive brief assembly execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "SourceIngestionAgent": AgentClassification(
        file_path="apps_exec/reasoning/SourceIngestionAgent.py",
        class_name="SourceIngestionAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Source ingestion execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "StyleComplianceAgent": AgentClassification(
        file_path="apps_exec/reasoning/StyleComplianceAgent.py",
        class_name="StyleComplianceAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Style compliance safety agent (L5). WAVE 8: Now L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="L5 governance safety agent - can emit heal_blocked signals. WAVE 8: Now L2 contract compliant.",
    ),
    "CodeJanitorAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/CodeJanitorAgent.py",
        class_name="CodeJanitorAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L5 code janitor/healer safety agent. WAVE 8: Now L2 contract compliant.",
    ),
    "PascalSovereigntyAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py",
        class_name="PascalSovereigntyAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L5 Pascal naming sovereignty enforcer. WAVE 8: Now L2 contract compliant.",
    ),
    "HygieneGuardianAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py",
        class_name="HygieneGuardianAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L5 code hygiene guardian safety agent. WAVE 8: Now L2 contract compliant.",
    ),
    "PreCommitSovereignAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py",
        class_name="PreCommitSovereignAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L5 pre-commit safety enforcement agent. WAVE 8: Now L2 contract compliant.",
    ),
    "RedTeamAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/RedTeamAgent.py",
        class_name="RedTeamAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L5 adversarial red team safety agent. WAVE 8: Now L2 contract compliant.",
    ),
    "ConstitutionalReviewerAgent": AgentClassification(
        file_path="agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py",
        class_name="ConstitutionalReviewerAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="L5 constitutional compliance reviewer. WAVE 8: Now L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="L6 performance analysis observer agent. WAVE 8: Now L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="LIC governance shield safety agent. WAVE 8: Now L2 contract compliant.",
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
        implements_l2_contract=True,
        notes="LIC reflection/observation agent (L6). WAVE 8: Now L2 contract compliant.",
    ),
    "LeadQualityAgent": AgentClassification(
        file_path="apps_lic/reasoning/LeadQualityAgent.py",
        class_name="LeadQualityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was RETIRED/EMPTY. File removed.",
    ),
    "DeliverabilityAgent": AgentClassification(
        file_path="apps_lic/reasoning/DeliverabilityAgent.py",
        class_name="DeliverabilityAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → LICValidationExecutor. File removed.",
    ),
    "CampaignBalanceAgent": AgentClassification(
        file_path="apps_lic/reasoning/CampaignBalanceAgent.py",
        class_name="CampaignBalanceAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → LICValidationExecutor. File removed.",
    ),
    "OutreachMessageAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachMessageAgent.py",
        class_name="OutreachMessageAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC outreach message execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "MessageComplianceAgent": AgentClassification(
        file_path="apps_lic/reasoning/MessageComplianceAgent.py",
        class_name="MessageComplianceAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC message compliance safety agent (L5). WAVE 8: Now L2 contract compliant.",
    ),
    "MessageArchitectAgent": AgentClassification(
        file_path="apps_lic/reasoning/MessageArchitectAgent.py",
        class_name="MessageArchitectAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC message architect execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "OutreachValidationExecutorAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachValidationExecutorAgent.py",
        class_name="OutreachValidationExecutorAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC outreach validation executor. WAVE 6: Now L2 contract compliant.",
    ),
    "OutreachProactiveAgent": AgentClassification(
        file_path="apps_lic/reasoning/OutreachProactiveAgent.py",
        class_name="OutreachProactiveAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC outreach proactive execution agent. WAVE 6: Now L2 contract compliant.",
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
        notes="LIC outreach learning planner (L1).",
    ),
    "LicTemplateOptimizerAgent": AgentClassification(
        file_path="apps_lic/reasoning/LicTemplateOptimizerAgent.py",
        class_name="LicTemplateOptimizerAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC template optimizer execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "DispatchOutreachToolsAgent": AgentClassification(
        file_path="apps_lic/reasoning/DispatchOutreachToolsAgent.py",
        class_name="DispatchOutreachToolsAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Tool dispatch execution agent. WAVE 6: Now L2 contract compliant.",
    ),
    "ValidatorAgent": AgentClassification(
        file_path="apps_lic/reasoning/ValidatorAgent.py",
        class_name="ValidatorAgent",
        current_layer="L5",
        canonical_role=CanonicalAgentRole.SAFETY,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="LIC validation safety agent (L5). WAVE 8: Now L2 contract compliant.",
    ),
    # ============================================
    # APPS_SHARED: Shared Infrastructure Agents
    # ============================================
    "BaseDispatchAgent": AgentClassification(
        file_path="apps_shared/reasoning/BaseDispatchAgent.py",
        class_name="BaseDispatchAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Shared base dispatch agent. L2 contract compliant.",
    ),
    "BaseProactiveAgent": AgentClassification(
        file_path="apps_shared/reasoning/BaseProactiveAgent.py",
        class_name="BaseProactiveAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Shared base proactive agent. L2 contract compliant.",
    ),
    "BaseReflectionAgent": AgentClassification(
        file_path="apps_shared/reasoning/BaseReflectionAgent.py",
        class_name="BaseReflectionAgent",
        current_layer="L6",
        canonical_role=CanonicalAgentRole.OBSERVER,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Shared base reflection agent. L2 contract compliant.",
    ),
    "BaseHealingOrchestrator": AgentClassification(
        file_path="apps_shared/reasoning/BaseHealingOrchestrator.py",
        class_name="BaseHealingOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Shared base healing orchestrator agent. L2 contract compliant.",
    ),
    "ParameterizedValidator": AgentClassification(
        file_path="apps_shared/reasoning/ParameterizedValidator.py",
        class_name="ParameterizedValidator",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Shared parameterized validator base agent. L2 contract compliant.",
    ),
    "InfrastructureOrchestrator": AgentClassification(
        file_path="apps_shared/reasoning/InfrastructureOrchestrator.py",
        class_name="InfrastructureOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Shared infrastructure orchestrator agent. L2 contract compliant.",
    ),
    "InfrastructureUpgradesOrchestrator": AgentClassification(
        file_path="apps_shared/reasoning/InfrastructureUpgradesOrchestrator.py",
        class_name="InfrastructureUpgradesOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Infrastructure upgrades orchestrator agent. L2 contract compliant.",
    ),
    "PilotOrchestrator": AgentClassification(
        file_path="apps_shared/reasoning/PilotOrchestrator.py",
        class_name="PilotOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Pilot orchestrator agent. L2 contract compliant.",
    ),
    # ============================================
    # APPS_RESEARCH: Research Agents
    # ============================================
    "ResearchOrchestrator": AgentClassification(
        file_path="apps_research/reasoning/ResearchOrchestrator.py",
        class_name="ResearchOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Research orchestrator agent. L2 contract compliant.",
    ),
    "InsightExtractionAgent": AgentClassification(
        file_path="apps_research/reasoning/InsightExtractionAgent.py",
        class_name="InsightExtractionAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Insight extraction agent. L2 contract compliant.",
    ),
    "KnowledgeSynthesisAgent": AgentClassification(
        file_path="apps_research/reasoning/KnowledgeSynthesisAgent.py",
        class_name="KnowledgeSynthesisAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Knowledge synthesis agent. L2 contract compliant.",
    ),
    "SourceDiscoveryAgent": AgentClassification(
        file_path="apps_research/reasoning/SourceDiscoveryAgent.py",
        class_name="SourceDiscoveryAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Source discovery agent. L2 contract compliant.",
    ),
    "EnterpriseResearchOrchestrator": AgentClassification(
        file_path="apps_research/reasoning/enterprise_research_orchestrator.py",
        class_name="EnterpriseResearchOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Enterprise research orchestrator agent. L2 contract compliant.",
    ),
    # ============================================
    # APPS_RFP: RFP Agents
    # ============================================
    "RfpOrchestrator": AgentClassification(
        file_path="apps_rfp/reasoning/RfpOrchestrator.py",
        class_name="RfpOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="RFP orchestrator agent. L2 contract compliant.",
    ),
    "ComplianceMappingAgent": AgentClassification(
        file_path="apps_rfp/reasoning/ComplianceMappingAgent.py",
        class_name="ComplianceMappingAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Compliance mapping agent. L2 contract compliant.",
    ),
    "RequirementAnalysisAgent": AgentClassification(
        file_path="apps_rfp/reasoning/RequirementAnalysisAgent.py",
        class_name="RequirementAnalysisAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Requirement analysis agent. L2 contract compliant.",
    ),
    "EnterpriseRfpOrchestrator": AgentClassification(
        file_path="apps_rfp/reasoning/enterprise_orchestrator.py",
        class_name="EnterpriseRfpOrchestrator",
        current_layer="L3",
        canonical_role=CanonicalAgentRole.ORCHESTRATOR,
        status=AgentStatus.ACTIVE,
        is_shim=False,
        implements_l2_contract=True,
        notes="Enterprise RFP orchestrator agent. L2 contract compliant.",
    ),
    # APPS_LIC Shims
    "ArchetypeIndicatorsAgent": AgentClassification(
        file_path="apps_lic/reasoning/ArchetypeIndicatorsAgent.py",
        class_name="ArchetypeIndicatorsAgent",
        current_layer="L2",
        canonical_role=CanonicalAgentRole.EXECUTION,
        status=AgentStatus.OBSOLETE,
        is_shim=True,
        implements_l2_contract=False,
        notes="DELETED WAVE 10: Was SHIM → apps_lic.config.archetype_indicator_config. File removed.",
    ),
}

def get_taxonomy_registry() -> AgentTaxonomyRegistry:
    """Get the populated taxonomy registry."""
    registry = AgentTaxonomyRegistry()
    for classification in AGENT_TAXONOMY_MAP.values():
        registry.register(classification)
    return registry
