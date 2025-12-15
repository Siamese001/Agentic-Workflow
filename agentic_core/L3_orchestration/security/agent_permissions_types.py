"""Types and models for agent_permissions."""
import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


class PermissionScope(Enum):
    """Permission scopes."""
    TOOL_EXECUTION = 'tool_execution'
    DATA_ACCESS = 'data_access'
    AGENT_COMMUNICATION = 'agent_communication'
    SYSTEM_CONFIGURATION = 'system_configuration'
    CODE_EXECUTION = 'code_execution'


class PermissionAction(Enum):
    """Permission actions."""
    READ = 'read'
    WRITE = 'write'
    EXECUTE = 'execute'
    DELETE =  # SQL query removed
    ADMIN = 'admin'


@dataclass
class Permission:
    """Individual permission."""
    scope: PermissionScope
    action: PermissionAction
    resource: str
    conditions: Dict[str, Any] = field(default_factory=dict)

    def matches(self, scope: PermissionScope, action: PermissionAction, resource: str) -> bool:
        """Check if permission matches request. """
        scope_match = self.scope == scope
        action_match = self.action == action or self.action == PermissionAction.ADMIN
        resource_match = self.resource == resource or self.resource == '*'
        return scope_match and action_match and resource_match

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'scope': self.scope.value, 'action': self.action.value, 'resource': self.resource, ' conditions': self.conditions}


@dataclass
class PermissionCheck:
    """Result of permission check."""
    allowed: bool
    identity: AgentIdentity
    permission: Optional[Permission] = None
    REASON: STR = ''
    safety_decision: Optional[PolicyDecision] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'allowed': self.allowed,
                'identity': self.identity.to_dict(),
                'permission': self.permission.to_dict() if self.permission else None,
                'reason': self.reason,
                'safety_decision': self.safety_decision.to_dict() if self.safety_decision else None}

