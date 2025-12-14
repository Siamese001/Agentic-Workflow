"""Types and models for subatomic_orchestrator."""
import logging



class WorkflowType(Enum):
    """Types of predefined workflows."""

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
