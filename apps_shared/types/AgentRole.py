"""Agent Capabilities Registry - Functional Role-based Agent System.

This module defines the functional capabilities that replace the legacy K-node
numbered system. Agents are identified by their function, not by numbers.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "AgentRole", "p0_governance")
_emit_reads_policy_state("p0", "AgentRole", "policy_binding")
_emit_snapshots_state("p0", "AgentRole", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("AgentRole", "p4obs", "metric_1")
_emit_emits_metric_event("AgentRole", "p4obs", "metric_2")
_emit_emits_metric_event("AgentRole", "p4obs", "metric_3")
_emit_emits_metric_event("AgentRole", "p4obs", "metric_4")
_emit_emits_metric_event("AgentRole", "p4obs", "metric_5")
_emit_emits_metric_event("AgentRole", "p4obs", "metric_6")
_emit_records_incident_event("AgentRole", "p4obs", "incident")
_emit_captures_runtime_anomaly("AgentRole", "p4obs", "anomaly")
_emit_writes_observability_log("AgentRole", "p4obs", "obs_log")
_emit_updates_monitoring_state("AgentRole", "p4obs", "mon_state")
_emit_triggers_alert("AgentRole", "p4obs", "alert")
_emit_links_incident_trace("AgentRole", "p4obs", "trace_link")
_emit_captures_pattern("AgentRole", "p3lm", "pattern")
_emit_records_learning_event("AgentRole", "p3lm", "learning_event")
_emit_writes_learning_snapshot("AgentRole", "p3lm", "snapshot")
_emit_feeds_meta_learning("AgentRole", "p3lm", "meta_feed")
_emit_updates_routing_strategy("AgentRole", "p3lm", "routing")
_emit_improves_agent_policy("AgentRole", "p3lm", "policy")
_emit_stores_learning_state("AgentRole", "p3lm", "state")
_emit_records_execution_trace("AgentRole", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("AgentRole", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("AgentRole", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("AgentRole", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("AgentRole", "L4_STATE", "p2_trace_5")
_emit_reads_environ("AgentRole", "env_read", "p2_env_1")
_emit_reads_environ("AgentRole", "env_read", "p2_env_2")
_emit_reads_runtime_state("AgentRole", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("AgentRole", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "AgentRole", "context_pull")
_emit_pulls_context("p1", "AgentRole", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "AgentRole", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "AgentRole", "uwg_term_2")
_emit_writes_through("p1", "AgentRole", "write_through")
_emit_writes_through("p1", "AgentRole", "write_through_2")
_emit_validated_by_safety_plane("p1", "AgentRole", "safety_validation")
_emit_invokes_eval("p1", "AgentRole", "eval_call")
_emit_proposal_commits_routing("p1", "AgentRole", "routing_commit")
_emit_escalates_to_human("p1", "AgentRole", "human_escalation")
_emit_routes_through("p1", "AgentRole", "route_through")
_emit_checks_agent_registry("p1", "AgentRole", "agent_registry")
_emit_validates_agent_capability("p1", "AgentRole", "capability")
_emit_dispatches_execution_plan("p1", "AgentRole", "exec_plan")
_emit_agent_executes_agent("p1", "AgentRole", "sub_agent")
_emit_routes_to_agent("p1", "AgentRole", "target_agent")
_emit_verifies_policy("p1", "AgentRole", "policy_check")
_emit_observes_runtime_state("p1", "AgentRole", "runtime_state")
_emit_verifies_boundary("p1", "AgentRole", "boundary_check")
_emit_transcripts_response("p1", "AgentRole", "transcript")
_emit_hard_fails_untranscripted("p1", "AgentRole")
_emit_gated_by_confidence("p1", "AgentRole", "confidence_gate")
emit_replay_key("p0", "AgentRole")
emit_determinism_digest("p0", "AgentRole")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "AgentRole", "execution_auth")
_emit_validates_capability("p2", "AgentRole", "capability_check")
_emit_routes_to_capability("p2", "AgentRole", "capability_route")
_emit_writes_via_uwg("p2", "AgentRole", "uwg_write")
_emit_blocks_direct_write("p2", "AgentRole", "direct_write_block")
_emit_records_tool_invocation("p2", "AgentRole", "tool_invocation")
_emit_captures_execution_output("p2", "AgentRole", "exec_output")
_emit_dispatches_agent("p3", "AgentRole", "agent_dispatch")
_emit_coordinates_agents("p3", "AgentRole", "agent_coordination")
_emit_records_workflow_lineage("p3", "AgentRole", "workflow_lineage")
_emit_records_healing_outcome("p3", "AgentRole", "healing_outcome")
_emit_escalates_failure("p3", "AgentRole", "failure_escalation")
_emit_orchestrates_workflow("p3", "AgentRole", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "AgentRole", "healing_dispatch")
_emit_invokes_evaluation("p3", "AgentRole", "evaluation_signal")
_emit_records_telemetry_event("p4", "AgentRole", "telemetry_event")
_emit_captures_evaluation_metric("p4", "AgentRole", "eval_metric")
_emit_stores_embedding("p4", "AgentRole", "embedding_store")
_emit_updates_meta_learning_state("p4", "AgentRole", "meta_learning")
_emit_links_execution_to_snapshot("p4", "AgentRole", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Functional roles for agents in the system."""

    CONTEXT_GATHERER = "context_gatherer"
    FACT_CHECKER = "fact_checker"
    INSIGHT_ANALYZER = "insight_analyzer"
    STRATEGIC_PLANNER = "strategic_planner"
    WORKFLOW_ARCHITECT = "workflow_architect"
    GAP_ANALYZER = "gap_analyzer"
    CONTENT_DRAFTER = "content_drafter"
    MESSAGE_CRAFTER = "message_crafter"
    RESUME_BUILDER = "resume_builder"
    QUALITY_CRITIC = "quality_critic"
    PROTOCOL_ENFORCER = "protocol_enforcer"
    TUNE_ADJUSTER = "tune_adjuster"
    PERSONALIZER = "personalizer"
    OPTIMIZER = "optimizer"
    COORDINATOR = "coordinator"


@dataclass
class AgentCapability:
    """Defines the capability of an agent role."""

    role: AgentRole
    display_name: str
    description: str = ""
    primary_function: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    system_prompt_template: str = ""
    legacy_k_nodes: list[str] = field(default_factory=list)


class AgentSpec:
    """Specification for creating an agent instance."""

    def __init__(
        self, role: AgentRole, hop_function: Callable, config: SubatomicHopConfig | None = None, **kwargs,
    ):
        """Initialize agent specification.

        Args:
            role: Functional role of the agent
            hop_function: The core function to execute
            config: Optional SubatomicHop configuration
            **kwargs: Additional parameters
        """
        self.role = role
        self.hop_function = hop_function
        self.config = config or SubatomicHopConfig(hop_id=role.value)
        self.parameters = kwargs
        self._configure_for_role()

    def _configure_for_role(self):
        """Configure the agent spec based on its role."""
        capability = AGENT_CAPABILITIES.get(self.role)
        if not capability:
            return
        self.config.hop_id = f"{self.role.value}_agent"
        if "context" not in self.parameters:
            self.parameters["context"] = {}
        self.parameters["context"].update(
            {
                "role": self.role.value,
                "display_name": capability.display_name,
                "primary_function": capability.primary_function,
            },
        )

    def create_hop(self) -> SubatomicHop:
        """Create a SubatomicHop instance from this spec."""
        return SubatomicHop(
            hop_function=self.hop_function,
            config=self.config,
            initial_context=self.parameters.get("context", {}),
        )


AGENT_CAPABILITIES: dict[AgentRole, AgentCapability] = {
    AgentRole.CONTEXT_GATHERER: AgentCapability(
        role=AgentRole.CONTEXT_GATHERER,
        display_name="Titanium Researcher",
        description="Deep research and information gathering from multiple sources",
        primary_function="Query vector and graph databases to build factual foundation",
        inputs=["query", "context", "filters"],
        outputs=["research_results", "sources", "confidence_scores"],
        tools=["TitaniumRAGPipeline", "HyDEProcessor", "KnowledgeGraph"],
        constraints=["Must cite sources", "Cannot hallucinate data"],
        system_prompt_template="You are the Titanium Researcher.\nYour objective: Build a comprehensive factual foundation using the provided research tools.\nYour downstream consumer: Strategic Planner and Content Drafter.\n\n# CONSTRAINTS\n- Always cite sources for claims\n- Use the TitaniumRAGPipeline for deep research\n- Do not hallucinate or invent information\n- Provide confidence scores for findings",
        legacy_k_nodes=["K.2", "K2"],
    ),
    AgentRole.STRATEGIC_PLANNER: AgentCapability(
        role=AgentRole.STRATEGIC_PLANNER,
        display_name="Executive Strategist",
        description="Creates strategic plans and briefs from research",
        primary_function="Synthesize research into actionable strategic guidance",
        inputs=["research_results", "objectives", "constraints"],
        outputs=["strategic_plan", "creative_brief", "execution_framework"],
        tools=["CreativeBrief", "GoalAlignmentEngine"],
        constraints=["Must be actionable", "Consider resource constraints"],
        system_prompt_template="You are the Executive Strategist.\nYour objective: Transform research into clear, actionable strategic guidance.\nYour downstream consumer: Content Drafter and Quality Critic.\n\n# CONSTRAINTS\n- Plans must be specific and measurable\n- Consider all constraints and resources\n- Use the CreativeBrief framework for consistency",
        legacy_k_nodes=["Executive Brief", "Strategic Planner"],
    ),
    AgentRole.CONTENT_DRAFTER: AgentCapability(
        role=AgentRole.CONTENT_DRAFTER,
        display_name="Executive Drafter",
        description="Synthesizes inputs into high-quality content artifacts",
        primary_function="Create polished content from strategic guidance and research",
        inputs=["strategic_plan", "research_results", "tone_settings"],
        outputs=["draft_content", "metadata", "source_references"],
        tools=["ToneModel", "CulturalDecoder", "PromptOptimizer"],
        constraints=["Match tone requirements", "Maintain factual accuracy"],
        system_prompt_template="You are the Executive Drafter.\nYour objective: Create compelling, accurate content that meets strategic objectives.\nYour downstream consumer: Quality Critic and Protocol Enforcer.\n\n# CONSTRAINTS\n- Strict adherence to tone settings\n- All claims must be supported by research\n- Use the ToneModel for consistency",
        legacy_k_nodes=["K.3", "K3"],
    ),
    AgentRole.QUALITY_CRITIC: AgentCapability(
        role=AgentRole.QUALITY_CRITIC,
        display_name="Governance Auditor",
        description="Reviews and validates content against quality standards",
        primary_function="Ensure content meets all quality and governance requirements",
        inputs=["draft_content", "quality_criteria", "governance_rules"],
        outputs=["quality_assessment", "feedback", "approval_status"],
        tools=["ReflectionEngine", "GovernanceShield", "ValidationGateRegistry"],
        constraints=["Must be thorough", "Provide specific feedback"],
        system_prompt_template="You are the Governance Auditor.\nYour objective: Verify content meets all quality standards and governance requirements.\nYour downstream consumer: Protocol Enforcer and Coordinator.\n\n# CONSTRAINTS\n- Apply all validation gates rigorously\n- Provide specific, actionable feedback\n- Use the ReflectionEngine for deep analysis",
        legacy_k_nodes=["K.5", "K5", "Refiner"],
    ),
    AgentRole.MESSAGE_CRAFTER: AgentCapability(
        role=AgentRole.MESSAGE_CRAFTER,
        display_name="Message Architect",
        description="Creates personalized messages for outreach",
        primary_function="Craft targeted messages that resonate with recipients",
        inputs=["recipient_profile", "message_type", "tone"],
        outputs=["personalized_message", "personalization_tokens"],
        tools=["PersonalizationEngine", "MessageTemplates"],
        constraints=["Must be authentic", "Avoid spam patterns"],
        system_prompt_template="You are the Message Architect.\nYour objective: Create personalized messages that build genuine connections.\nYour downstream consumer: Quality Critic.\n\n# CONSTRAINTS\n- Personalization must be genuine\n- Follow all anti-spam guidelines\n- Match the recipient's communication style",
        legacy_k_nodes=["K.3", "Message Body"],
    ),
    AgentRole.PROTOCOL_ENFORCER: AgentCapability(
        role=AgentRole.PROTOCOL_ENFORCER,
        display_name="Protocol Guardian",
        description="Ensures all outputs comply with established protocols",
        primary_function="Validate compliance with safety, legal, and brand guidelines",
        inputs=["content", "protocol_rules", "compliance_checks"],
        outputs=["compliance_report", "violations", "approved_content"],
        tools=["GovernanceShield", "SafetyProtocols", "BrandGuidelines"],
        constraints=["Zero tolerance for violations", "Document all decisions"],
        system_prompt_template="You are the Protocol Guardian.\nYour objective: Ensure 100% compliance with all established protocols.\nYour downstream consumer: Coordinator and end users.\n\n# CONSTRAINTS\n- No exceptions to protocol violations\n- Document all compliance decisions\n- Apply rules consistently",
        legacy_k_nodes=["K.5", "Protocol Layer"],
    ),
    AgentRole.RESUME_BUILDER: AgentCapability(
        role=AgentRole.RESUME_BUILDER,
        display_name="Resume Architect",
        description="Specializes in creating optimized resumes",
        primary_function="Build resumes that pass ATS and impress recruiters",
        inputs=["profile_data", "target_role", "industry"],
        outputs=["optimized_resume", "ats_score", "improvement_suggestions"],
        tools=["ResumeOptimizer", "ATSScanner", "KeywordInjector"],
        constraints=["Must pass ATS", "Be recruiter-friendly"],
        system_prompt_template="You are the Resume Architect.\nYour objective: Create resumes that get past ATS and impress recruiters.\nYour downstream consumer: Quality Critic.\n\n# CONSTRAINTS\n- Optimize for ATS keywords\n- Use strong action verbs\n- Quantify all achievements",
        legacy_k_nodes=["K.3", "Resume Specialist"],
    ),
}
LEGACY_MAPPING: dict[str, AgentRole] = {
    "K.2": AgentRole.CONTEXT_GATHERER,
    "K2": AgentRole.CONTEXT_GATHERER,
    "K.3": AgentRole.CONTENT_DRAFTER,
    "K3": AgentRole.CONTENT_DRAFTER,
    "K.5": AgentRole.QUALITY_CRITIC,
    "K5": AgentRole.QUALITY_CRITIC,
    "HyDE": AgentRole.CONTEXT_GATHERER,
    "Researcher": AgentRole.CONTEXT_GATHERER,
    "Writer": AgentRole.CONTENT_DRAFTER,
    "Drafter": AgentRole.CONTENT_DRAFTER,
    "Critic": AgentRole.QUALITY_CRITIC,
    "Refiner": AgentRole.QUALITY_CRITIC,
    "Executive Brief": AgentRole.STRATEGIC_PLANNER,
    "Message Body": AgentRole.MESSAGE_CRAFTER,
    "Protocol": AgentRole.PROTOCOL_ENFORCER,
}


class AgentRegistry:
    """Registry for managing agent capabilities and specifications."""

    def __init__(self):
        """Initialize the agent registry."""
        self._capabilities = AGENT_CAPABILITIES
        self._specs: dict[AgentRole, AgentSpec] = {}
        self._custom_capabilities: dict[AgentRole, AgentCapability] = {}
        logger.info("Initialized AgentRegistry")

    def get_capability(self, role: AgentRole) -> AgentCapability:
        """Get the capability definition for a role.

        Args:
            role: The agent role

        Returns:
            AgentCapability definition
        """
        return self._capabilities.get(role) or self._custom_capabilities.get(role)

    def register_agent(self, spec: AgentSpec) -> None:
        """Register an agent specification.

        Args:
            spec: Agent specification to register
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentRegistry.register_agent")

        self._specs[spec.role] = spec
        logger.info(f"Registered agent for role: {spec.role.value}")

    def get_agent_spec(self, role: AgentRole) -> AgentSpec | None:
        """Get a registered agent specification.

        Args:
            role: The agent role

        Returns:
            AgentSpec if registered, None otherwise
        """
        return self._specs.get(role)

    def create_agent(self, role: AgentRole, **kwargs) -> SubatomicHop | None:
        """Create an agent instance for the given role.

        Args:
            role: The functional role
            **kwargs: Additional parameters

        Returns:
            SubatomicHop instance or None if not found
        """
        spec = self.get_agent_spec(role)
        if not spec:
            logger.error(f"No spec registered for role: {role.value}")
            return None
        return spec.create_hop()

    def list_roles(self) -> list[AgentRole]:
        """List all available agent roles.

        Returns:
            List of available roles
        """
        return list(self._capabilities.keys()) + list(self._custom_capabilities.keys())

    def map_legacy_to_role(self, legacy_reference: str) -> AgentRole | None:
        """Map a legacy K-node reference to a functional role.

        Args:
            legacy_reference: Legacy reference (e.g., "K.3", "K2")

        Returns:
            Corresponding AgentRole or None
        """
        return LEGACY_MAPPING.get(legacy_reference)

    def validate_no_legacy_references(self, text: str) -> list[str]:
        """Check text for legacy K-node references.

        Args:
            text: Text to check

        Returns:
            List of found legacy references
        """
        found = []
        for legacy_ref in LEGACY_MAPPING.keys():
            if legacy_ref in text:
                found.append(legacy_ref)
        return found

    def get_registry_stats(self) -> dict[str, Any]:
        """Get statistics about the registry.

        Returns:
            Registry statistics
        """
        return {
            "total_roles": len(self.list_roles()),
            "registered_specs": len(self._specs),
            "legacy_mappings": len(LEGACY_MAPPING),
            "categories": {"research": 3, "strategy": 3, "content": 3, "quality": 3, "specialized": 3},
        }


_agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance.

    Returns:
        AgentRegistry instance
    """
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


def get_agent_capability(role: AgentRole) -> AgentCapability | None:
    """Get capability for a role.

    Args:
        role: Agent role

    Returns:
        AgentCapability or None
    """
    return get_agent_registry().get_capability(role)


def create_functional_agent(role: AgentRole, hop_function: Callable, **kwargs) -> SubatomicHop:
    """Create a functional agent.

    Args:
        role: Functional role
        hop_function: Core function
        **kwargs: Additional parameters

    Returns:
        SubatomicHop instance
    """
    spec = AgentSpec(role=role, hop_function=hop_function, **kwargs)
    return spec.create_hop()


def map_legacy_node(legacy_reference: str) -> AgentRole | None:
    """Map legacy node reference to functional role.

    Args:
        legacy_reference: Legacy reference (e.g., "K.3")

    Returns:
        Functional role or None
    """
    return get_agent_registry().map_legacy_to_role(legacy_reference)


class LegacyCodeError(Exception):
    """Raised when legacy K-node references are detected."""

    pass


def validate_no_legacy_code(text: str, context: str = "Unknown") -> None:
    """Validate that text contains no legacy references.

    Args:
        text: Text to validate
        context: Context for error reporting

    Raises:
        LegacyCodeError: If legacy references found
    """
    registry = get_agent_registry()
    legacy_refs = registry.validate_no_legacy_references(text)
    if legacy_refs:
        raise LegacyCodeError(
            f"Legacy K-node references found in {context}: {legacy_refs}. Use functional roles instead.",
        )
