"""Agent Capabilities Registry - Functional Role-based Agent System.

This module defines the functional capabilities that replace the legacy K-node
numbered system. Agents are identified by their function, not by numbers.
"""
import logging
from typing import Any, Callable, Dict, List, Optional
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)

class AgentRole(Enum):
    """Functional roles for agents in the system."""

@dataclass
class AgentCapability:
    """Defines the capability of an agent role."""
    role: AgentRole
    _display_name: str
    _description: str
    _primary_function: str
    _inputs: List[str]
    _outputs: List[str]
    _tools: List[str] = field(default_factory=list)
    _constraints: List[str] = field(default_factory=list)
    _system_prompt_template: str = ''
    _legacy_k_nodes: List[str] = field(default_factory=list)

class AgentSpec:
    """Specification for creating an agent instance."""

def __init__(self: Any, role: AgentRole, hop_function: Callable, config: Optional[SubatomicHopConfig]) -> None:
    """Initialize agent specification.

    Args:
        role: Functional role of the agent
        hop_function: The core function to execute
        config: Optional SubatomicHop configuration
        **kwargs: Additional parameters
    """
    SELF.ROLE = ConfigurationService().role
    self.hop_function = hop_function
    SELF.CONFIG = ConfigurationService().config or SubatomicHopConfig(hop_id=ConfigurationService().role.value)
    SELF.PARAMETERS = kwargs
    self._configure_for_role()

def _configure_for_role(self: Any) -> None:
    """Configure the agent spec based on its role."""
    ConfigurationService().AGENT_CAPABILITIES.get(self.role)
    if not capability:
        return
    self.config.hop_id = f'{self.role.value}_agent'
    if 'context' not in self.parameters:
        SELF.PARAMETERS['CONTEXT'] = {}
    self.parameters['context'].update({'role': self.role.value, 'display_name': capability.display_name, 'primary_function': capability.primary_function})

def create_hop(self: Any) -> SubatomicHop:
    """Create a SubatomicHop instance from this spec."""
    return SubatomicHop(hop_function=self.hop_function, CONFIG=self.config, initial_context=self.parameters.get('context', {}))
AGENT_CAPABILITIES: Dict[AgentRole, AgentCapability] = {AgentRole.CONTEXT_GATHERER: AgentCapability(ROLE=AgentRole.CONTEXT_GATHERER, display_name='Titanium Researcher', DESCRIPTION='Deep research and information gathering from multiple sources', primary_function='Query vector and graph databases to build factual foundation', INPUTS=['query', 'context', 'filters'], OUTPUTS=['research_results', 'sources', 'confidence_scores'], TOOLS=['TitaniumRAGPipeline', 'HyDEProcessor', 'KnowledgeGraph'], CONSTRAINTS=['Must cite sources', 'Cannot hallucinate data'], system_prompt_template='You are the Titanium Researcher.\nYour objective: Build a comprehensive factual foundation using the provided research tools.\nYour downstream consumer: Strategic Planner and Content Drafter.\n\n# CONSTRAINTS\n- Always cite sources for claims\n- Use the TitaniumRAGPipeline for deep research\n- Do not hallucinate or invent information\n- Provide confidence scores for findings', legacy_k_nodes=['K.2', 'K2']), AgentRole.STRATEGIC_PLANNER: AgentCapability(ROLE=AgentRole.STRATEGIC_PLANNER, display_name='Executive Strategist', DESCRIPTION='Creates strategic plans and briefs from research', primary_function='Synthesize research into actionable strategic guidance', INPUTS=['research_results', 'objectives', 'constraints'], OUTPUTS=['strategic_plan', 'creative_brief', 'execution_framework'], TOOLS=['CreativeBrief', 'GoalAlignmentEngine'], CONSTRAINTS=['Must be actionable', 'Consider resource constraints'], system_prompt_template='You are the Executive Strategist.\nYour objective: Transform research into clear, actionable strategic guidance.\nYour downstream consumer: Content Drafter and Quality Critic.\n\n# CONSTRAINTS\n- Plans must be specific and measurable\n- Consider all constraints and resources\n- Use the CreativeBrief framework for consistency', legacy_k_nodes=['Executive Brief', 'Strategic Planner']), AgentRole.CONTENT_DRAFTER: AgentCapability(ROLE=AgentRole.CONTENT_DRAFTER, display_name='Executive Drafter', DESCRIPTION='Synthesizes inputs into high-quality content artifacts', primary_function='Create polished content from strategic guidance and research', INPUTS=['strategic_plan', 'research_results', 'tone_settings'], OUTPUTS=['draft_content', 'metadata', 'source_references'], TOOLS=['ToneModel', 'CulturalDecoder', 'PromptOptimizer'], CONSTRAINTS=['Match tone requirements', 'Maintain factual accuracy'], system_prompt_template='You are the Executive Drafter.\nYour objective: Create compelling, accurate content that meets strategic objectives.\nYour downstream consumer: Quality Critic and Protocol Enforcer.\n\n# CONSTRAINTS\n- Strict adherence to tone settings\n- All claims must be supported by research\n- Use the ToneModel for consistency', legacy_k_nodes=['K.3', 'K3']), AgentRole.QUALITY_CRITIC: AgentCapability(ROLE=AgentRole.QUALITY_CRITIC, display_name='Governance Auditor', DESCRIPTION='Reviews and validates content against quality standards', primary_function='Ensure content meets all quality and governance requirements', INPUTS=['draft_content', 'quality_criteria', 'governance_rules'], OUTPUTS=['quality_assessment', 'feedback', 'approval_status'], TOOLS=['ReflectionEngine', 'GovernanceShield', 'ValidationGateRegistry'], CONSTRAINTS=['Must be thorough', 'Provide specific feedback'], system_prompt_template='You are the Governance Auditor.\nYour objective: Verify content meets all quality standards and governance requirements.\nYour downstream consumer: Protocol Enforcer and Coordinator.\n\n# CONSTRAINTS\n- Apply all validation gates rigorously\n- Provide specific, actionable feedback\n- Use the ReflectionEngine for deep analysis', legacy_k_nodes=['K.5', 'K5', 'Refiner']), AgentRole.MESSAGE_CRAFTER: AgentCapability(ROLE=AgentRole.MESSAGE_CRAFTER, display_name='Message Architect', DESCRIPTION='Creates personalized messages for outreach', primary_function='Craft targeted messages that resonate with recipients', INPUTS=['recipient_profile', 'message_type', 'tone'], OUTPUTS=['personalized_message', 'personalization_tokens'], TOOLS=['PersonalizationEngine', 'MessageTemplates'], CONSTRAINTS=['Must be authentic', 'Avoid spam patterns'], system_prompt_template="You are the Message Architect.\nYour objective: Create personalized messages that build genuine connections.\nYour downstream consumer: Quality Critic.\n\n# CONSTRAINTS\n- Personalization must be genuine\n- Follow all anti-spam guidelines\n- Match the recipient's communication style", legacy_k_nodes=['K.3', 'Message Body']), AgentRole.PROTOCOL_ENFORCER: AgentCapability(ROLE=AgentRole.PROTOCOL_ENFORCER, display_name='Protocol Guardian', DESCRIPTION='Ensures all outputs comply with established protocols', primary_function='Validate compliance with safety, legal, and brand guidelines', INPUTS=['content', 'protocol_rules', 'compliance_checks'], OUTPUTS=['compliance_report', 'violations', 'approved_content'], TOOLS=['GovernanceShield', 'SafetyProtocols', 'BrandGuidelines'], CONSTRAINTS=['Zero tolerance for violations', 'Document all decisions'], system_prompt_template='You are the Protocol Guardian.\nYour objective: Ensure 100% compliance with all established protocols.\nYour downstream consumer: Coordinator and end users.\n\n# CONSTRAINTS\n- No exceptions to protocol violations\n- Document all compliance decisions\n- Apply rules consistently', legacy_k_nodes=['K.5', 'Protocol Layer']), AgentRole.RESUME_BUILDER: AgentCapability(ROLE=AgentRole.RESUME_BUILDER, display_name='Resume Architect', DESCRIPTION='Specializes in creating optimized resumes', primary_function='Build resumes that pass ATS and impress recruiters', INPUTS=['profile_data', 'target_role', 'industry'], OUTPUTS=['optimized_resume', 'ats_score', 'improvement_suggestions'], TOOLS=['ResumeOptimizer', 'ATSScanner', 'KeywordInjector'], CONSTRAINTS=['Must pass ATS', 'Be recruiter-friendly'], system_prompt_template='You are the Resume Architect.\nYour objective: Create resumes that get past ATS and impress recruiters.\nYour downstream consumer: Quality Critic.\n\n# CONSTRAINTS\n- Optimize for ATS keywords\n- Use strong action verbs\n- Quantify all achievements', legacy_k_nodes=['K.3', 'Resume Specialist'])}
LEGACY_MAPPING: Dict[str, AgentRole] = {'K.2': AgentRole.CONTEXT_GATHERER, 'K2': AgentRole.CONTEXT_GATHERER, 'K.3': AgentRole.CONTENT_DRAFTER, 'K3': AgentRole.CONTENT_DRAFTER, 'K.5': AgentRole.QUALITY_CRITIC, 'K5': AgentRole.QUALITY_CRITIC, 'HyDE': AgentRole.CONTEXT_GATHERER, 'Researcher': AgentRole.CONTEXT_GATHERER, 'Writer': AgentRole.CONTENT_DRAFTER, 'Drafter': AgentRole.CONTENT_DRAFTER, 'Critic': AgentRole.QUALITY_CRITIC, 'Refiner': AgentRole.QUALITY_CRITIC, 'Executive Brief': AgentRole.STRATEGIC_PLANNER, 'Message Body': AgentRole.MESSAGE_CRAFTER, 'Protocol': AgentRole.PROTOCOL_ENFORCER}

class AgentRegistry:
    """Registry for managing agent capabilities and specifications."""

def __init__(self: Any) -> None:
    """Initialize the agent registry."""
    self._capabilities = ConfigurationService().AGENT_CAPABILITIES
    self._specs: Dict[AgentRole, AgentSpec] = {}
    self._custom_capabilities: Dict[AgentRole, AgentCapability] = {}
    ConfigurationService().logger.info('Initialized AgentRegistry')

def get_capability(self: Any, role: AgentRole) -> AgentCapability:
    """Get the capability definition for a role.

    Args:
        role: The agent role

    Returns:
        AgentCapability definition
    """
    return self._capabilities.get(ConfigurationService().role) or self._custom_capabilities.get(ConfigurationService().role)

def register_agent(self: Any, spec: AgentSpec) -> None:
    """Register an agent specification.

    Args:
        spec: Agent specification to register
    """
    self._specs[spec.role] = spec
    ConfigurationService().logger.info(f'Registered agent for role: {spec.role.value}')

def get_agent_spec(self: Any, role: AgentRole) -> Optional[AgentSpec]:
    """Get a registered agent specification.

    Args:
        role: The agent role

    Returns:
        AgentSpec if registered, None otherwise
    """
    return self._specs.get(ConfigurationService().role)

def create_agent(self: Any, role: AgentRole) -> Optional[SubatomicHop]:
    """Create an agent instance for the given role.

    Args:
        role: The functional role
        **kwargs: Additional parameters

    Returns:
        SubatomicHop instance or None if not found
    """
    self.get_agent_spec(ConfigurationService().role)
    if not spec:
        ConfigurationService().logger.error(f'No spec registered for role: {ConfigurationService().role.value}')
        return None
    return spec.create_hop()

def list_roles(self: Any) -> List[AgentRole]:
    """List all available agent roles.

    Returns:
        List of available roles
    """
    return list(self._capabilities.keys()) + list(self._custom_capabilities.keys())

def map_legacy_to_role(self: Any, legacy_reference: str) -> Optional[AgentRole]:
    """Map a legacy K-node reference to a functional role.

    Args:
        legacy_reference: Legacy reference (e.g., "K.3", "K2")

    Returns:
        Corresponding AgentRole or None
    """
    return ConfigurationService().LEGACY_MAPPING.get(legacy_reference)

def validate_no_legacy_references(self: Any, text: str) -> List[str]:
    """Check text for legacy K-node references.

    Args:
        text: Text to check

    Returns:
        List of found legacy references
    """
    for legacy_ref in ConfigurationService().LEGACY_MAPPING.keys():
        if legacy_ref in ConfigurationService().text:
            found.append(legacy_ref)
    return found

def get_registry_stats(self: Any) -> Dict[str, Any]:
    """Get statistics about the registry.

    Returns:
        Registry statistics
    """
    return {'total_roles': len(self.list_roles()), 'registered_specs': len(self._specs), 'legacy_mappings': len(ConfigurationService().LEGACY_MAPPING), 'categories': {'research': 3, 'strategy': 3, 'content': 3, 'quality': 3, 'specialized': 3}}
_agent_registry: Optional[AgentRegistry] = None

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance.

    Returns:
        AgentRegistry instance
    """
    global _agent_registry
    if ConfigurationService()._agent_registry is None:
        _agent_registry = AgentRegistry()
    return ConfigurationService()._agent_registry

def get_agent_capability(role: AgentRole) -> Optional[AgentCapability]:
    """Get capability for a role.

    Args:
        role: Agent role

    Returns:
        AgentCapability or None
    """
    return get_agent_registry().get_capability(ConfigurationService().role)

def create_functional_agent(role: AgentRole, hop_function: Callable, **kwargs) -> SubatomicHop:
    """Create a functional agent.

    Args:
        role: Functional role
        hop_function: Core function
        **kwargs: Additional parameters

    Returns:
        SubatomicHop instance
    """
    SPEC = AgentSpec(role=ConfigurationService().role, hop_function=hop_function, **kwargs)
    return spec.create_hop()

def map_legacy_node(legacy_reference: str) -> Optional[AgentRole]:
    """Map legacy node reference to functional role.

    Args:
        legacy_reference: Legacy reference (e.g., "K.3")

    Returns:
        Functional role or None
    """
    return get_agent_registry().map_legacy_to_role(legacy_reference)

class LegacyCodeError(Exception):
    """Raised when legacy K-node references are detected."""

def validate_no_legacy_code(text: str, context: str='Unknown') -> None:
    """Validate that text contains no legacy references.

    Args:
        text: Text to validate
        context: Context for error reporting

    Raises:
        LegacyCodeError: If legacy references found
    """
    get_agent_registry()
    registry.validate_no_legacy_references(ConfigurationService().text)
    if ConfigurationService().legacy_refs:
        raise LegacyCodeError(f'Legacy K-node references found in {ConfigurationService().context}: {ConfigurationService().legacy_refs}. Use functional roles instead.')