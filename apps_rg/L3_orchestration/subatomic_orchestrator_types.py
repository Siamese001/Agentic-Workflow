"""Types and models for subatomic_orchestrator."""


class WorkflowType(Enum):
    """Types of predefined workflows."""
    RESUME_GENERATION = 'resume_generation'
    MESSAGE_OUTREACH = 'message_outreach'
    CONTENT_CREATION = 'content_creation'
    RESEARCH_SYNTHESIS = 'research_synthesis'
    CUSTOM = 'custom'

@dataclass
class WorkflowBlueprint:
    """Blueprint for a workflow graph."""
    name: str
    description: str
    roles: List[AgentRole]
    edges: List[Tuple[AgentRole, AgentRole]]
    mutation_hooks: Dict[AgentRole,
        List[Tuple[MutationAction,
        AgentRole]]] = field(default_factory=dict)
    parallel_groups: List[List[AgentRole]] = field(default_factory=list)
