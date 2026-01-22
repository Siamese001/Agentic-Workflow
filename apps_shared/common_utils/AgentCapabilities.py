"""Agent Capabilities Registry - Functional Role-based Agent System.

This module defines the functional capabilities that replace the legacy K-node
numbered system. Agents are identified by their function, not by numbers.
"""

import logging


logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Functional roles for agents in the system."""

    # Core Research & Analysis
    CONTEXT_GATHERER = "context_gatherer"  # Formerly K.2/HyDE - Deep research
    FACT_CHECKER = "fact_checker"  # Validation and verification
    INSIGHT_ANALYZER = "insight_analyzer"  # Pattern recognition

    # Strategy & Planning
    STRATEGIC_PLANNER = "strategic_planner"  # Formerly Executive Brief
    WORKFLOW_ARCHITECT = "workflow_architect"  # DAG design
    GAP_ANALYZER = "gap_analyzer"  # Identify missing elements

    # Content Creation
    CONTENT_DRAFTER = "content_drafter"  # Formerly K.3 - Primary writer
    MESSAGE_CRAFTER = "message_crafter"  # Specialized messaging
    RESUME_BUILDER = "resume_builder"  # Resume-specific content

    # Quality & Governance
    QUALITY_CRITIC = "quality_critic"  # Formerly K.5/Refiner
    PROTOCOL_ENFORCER = "protocol_enforcer"  # Governance and rules
    TUNE_ADJUSTER = "tune_adjuster"  # Tone and style optimization

    # Specialized Roles
    PERSONALIZER = "personalizer"  # Customization per user
    OPTIMIZER = "optimizer"  # Performance improvement
    COORDINATOR = "coordinator"  # Orchestration and sync


@dataclass
class AgentCapability:
    """Defines the capability of an agent role."""

    role: AgentRole
    display_name: str
    description: str
    primary_function: str
    inputs: list[str]
    outputs: list[str]
    tools: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    system_prompt_template: str = ""

    # Legacy mapping for transition
    legacy_k_nodes: list[str] = field(default_factory=list)


class AgentSpec:
    """Specification for creating an agent instance."""

    def __init__(
        self,
        role: AgentRole,
        hop_function: Callable,
        config: SubatomicHopConfig | None = None,
        **kwargs,
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

        # Configure based on role
        self._configure_for_role()

    def _configure_for_role(self):
        """Configure the agent spec based on its role."""
        capability = AGENT_CAPABILITIES.get(self.role)
        if not capability:
            return

        # Update configuration based on capability
        self.config.hop_id = f"{self.role.value}_agent"

        # Add role-specific context
        if "context" not in self.parameters:
            self.parameters["context"] = {}

        self.parameters["context"].update(
            {
                "role": self.role.value,
                "display_name": capability.display_name,
                "primary_function": capability.primary_function,
            }
        )

    def create_hop(self) -> SubatomicHop:
        """Create a SubatomicHop instance from this spec."""
        return SubatomicHop(
            hop_function=self.hop_function,
            config=self.config,
            initial_context=self.parameters.get("context", {}),
        )


# Registry of agent capabilities
AGENT_CAPABILITIES: dict[AgentRole, AgentCapability] = {
    # Context Gathering
    AgentRole.CONTEXT_GATHERER: AgentCapability(
        role=AgentRole.CONTEXT_GATHERER,
        display_name="Titanium Researcher",
        description="Deep research and information gathering from multiple sources",
        primary_function="Query vector and graph databases to build factual foundation",
        inputs=["query", "context", "filters"],
        outputs=["research_results", "sources", "confidence_scores"],
        tools=["TitaniumRAGPipeline", "HyDEProcessor", "KnowledgeGraph"],
        constraints=["Must cite sources", "Cannot hallucinate data"],
        system_prompt_template="""You are the Titanium Researcher.
Your objective: Build a comprehensive factual foundation using the provided research tools.
Your downstream consumer: Strategic Planner and Content Drafter.

# CONSTRAINTS
- Always cite sources for claims
- Use the TitaniumRAGPipeline for deep research
- Do not hallucinate or invent information
- Provide confidence scores for findings""",
        legacy_k_nodes=["K.2", "K2"],
    ),
    # Strategic Planning
    AgentRole.STRATEGIC_PLANNER: AgentCapability(
        role=AgentRole.STRATEGIC_PLANNER,
        display_name="Executive Strategist",
        description="Creates strategic plans and briefs from research",
        primary_function="Synthesize research into actionable strategic guidance",
        inputs=["research_results", "objectives", "constraints"],
        outputs=["strategic_plan", "creative_brief", "execution_framework"],
        tools=["CreativeBrief", "GoalAlignmentEngine"],
        constraints=["Must be actionable", "Consider resource constraints"],
        system_prompt_template="""You are the Executive Strategist.
Your objective: Transform research into clear, actionable strategic guidance.
Your downstream consumer: Content Drafter and Quality Critic.

# CONSTRAINTS
- Plans must be specific and measurable
- Consider all constraints and resources
- Use the CreativeBrief framework for consistency""",
        legacy_k_nodes=["Executive Brief", "Strategic Planner"],
    ),
    # Content Drafting
    AgentRole.CONTENT_DRAFTER: AgentCapability(
        role=AgentRole.CONTENT_DRAFTER,
        display_name="Executive Drafter",
        description="Synthesizes inputs into high-quality content artifacts",
        primary_function="Create polished content from strategic guidance and research",
        inputs=["strategic_plan", "research_results", "tone_settings"],
        outputs=["draft_content", "metadata", "source_references"],
        tools=["ToneModel", "CulturalDecoder", "PromptOptimizer"],
        constraints=["Match tone requirements", "Maintain factual accuracy"],
        system_prompt_template="""You are the Executive Drafter.
Your objective: Create compelling, accurate content that meets strategic objectives.
Your downstream consumer: Quality Critic and Protocol Enforcer.

# CONSTRAINTS
- Strict adherence to tone settings
- All claims must be supported by research
- Use the ToneModel for consistency""",
        legacy_k_nodes=["K.3", "K3"],
    ),
    # Quality Criticism
    AgentRole.QUALITY_CRITIC: AgentCapability(
        role=AgentRole.QUALITY_CRITIC,
        display_name="Governance Auditor",
        description="Reviews and validates content against quality standards",
        primary_function="Ensure content meets all quality and governance requirements",
        inputs=["draft_content", "quality_criteria", "governance_rules"],
        outputs=["quality_assessment", "feedback", "approval_status"],
        tools=["ReflectionEngine", "GovernanceShield", "ValidationGateRegistry"],
        constraints=["Must be thorough", "Provide specific feedback"],
        system_prompt_template="""You are the Governance Auditor.
Your objective: Verify content meets all quality standards and governance requirements.
Your downstream consumer: Protocol Enforcer and Coordinator.

# CONSTRAINTS
- Apply all validation gates rigorously
- Provide specific, actionable feedback
- Use the ReflectionEngine for deep analysis""",
        legacy_k_nodes=["K.5", "K5", "Refiner"],
    ),
    # Message Crafting
    AgentRole.MESSAGE_CRAFTER: AgentCapability(
        role=AgentRole.MESSAGE_CRAFTER,
        display_name="Message Architect",
        description="Creates personalized messages for outreach",
        primary_function="Craft targeted messages that resonate with recipients",
        inputs=["recipient_profile", "message_type", "tone"],
        outputs=["personalized_message", "personalization_tokens"],
        tools=["PersonalizationEngine", "MessageTemplates"],
        constraints=["Must be authentic", "Avoid spam patterns"],
        system_prompt_template="""You are the Message Architect.
Your objective: Create personalized messages that build genuine connections.
Your downstream consumer: Quality Critic.

# CONSTRAINTS
- Personalization must be genuine
- Follow all anti-spam guidelines
- Match the recipient's communication style""",
        legacy_k_nodes=["K.3", "Message Body"],
    ),
    # Protocol Enforcement
    AgentRole.PROTOCOL_ENFORCER: AgentCapability(
        role=AgentRole.PROTOCOL_ENFORCER,
        display_name="Protocol Guardian",
        description="Ensures all outputs comply with established protocols",
        primary_function="Validate compliance with safety, legal, and brand guidelines",
        inputs=["content", "protocol_rules", "compliance_checks"],
        outputs=["compliance_report", "violations", "approved_content"],
        tools=["GovernanceShield", "SafetyProtocols", "BrandGuidelines"],
        constraints=["Zero tolerance for violations", "Document all decisions"],
        system_prompt_template="""You are the Protocol Guardian.
Your objective: Ensure 100% compliance with all established protocols.
Your downstream consumer: Coordinator and end users.

# CONSTRAINTS
- No exceptions to protocol violations
- Document all compliance decisions
- Apply rules consistently""",
        legacy_k_nodes=["K.5", "Protocol Layer"],
    ),
    # Resume Building
    AgentRole.RESUME_BUILDER: AgentCapability(
        role=AgentRole.RESUME_BUILDER,
        display_name="Resume Architect",
        description="Specializes in creating optimized resumes",
        primary_function="Build resumes that pass ATS and impress recruiters",
        inputs=["profile_data", "target_role", "industry"],
        outputs=["optimized_resume", "ats_score", "improvement_suggestions"],
        tools=["ResumeOptimizer", "ATSScanner", "KeywordInjector"],
        constraints=["Must pass ATS", "Be recruiter-friendly"],
        system_prompt_template="""You are the Resume Architect.
Your objective: Create resumes that get past ATS and impress recruiters.
Your downstream consumer: Quality Critic.

# CONSTRAINTS
- Optimize for ATS keywords
- Use strong action verbs
- Quantify all achievements""",
        legacy_k_nodes=["K.3", "Resume Specialist"],
    ),
}


# Legacy mapping for transition
LEGACY_MAPPING: dict[str, AgentRole] = {
    # Direct mappings
    "K.2": AgentRole.CONTEXT_GATHERER,
    "K2": AgentRole.CONTEXT_GATHERER,
    "K.3": AgentRole.CONTENT_DRAFTER,
    "K3": AgentRole.CONTENT_DRAFTER,
    "K.5": AgentRole.QUALITY_CRITIC,
    "K5": AgentRole.QUALITY_CRITIC,
    # Functional mappings
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
            "categories": {
                "research": 3,
                "strategy": 3,
                "content": 3,
                "quality": 3,
                "specialized": 3,
            },
        }


# Global registry instance
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


# Convenience functions
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


# Exception for legacy code detection
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
            f"Legacy K-node references found in {context}: {legacy_refs}. "
            f"Use functional roles instead."
        )