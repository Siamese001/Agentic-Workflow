"""Enum types for enums_v6_enums."""


class Route(Enum):
    """Message delivery routes"""
    INMAIL = 'INMAIL'
    CONNECTION_REQ = 'CONNECTION_REQ'
    EMAIL = 'EMAIL'
    FOLLOW_UP = 'FOLLOW_UP'

class Archetype(Enum):
    """Recipient archetypes for personalization - v11.6 4-archetype standard"""
    C_LEVEL = 'C_LEVEL'
    EXECUTIVE = 'EXECUTIVE'
    SENIOR_TA = 'SENIOR_TA'
    RECRUITER = 'RECRUITER'

class EventType(Enum):
    """Event types for message bus / state logging"""
    WORKFLOW_STARTED = 'WORKFLOW_STARTED'
    WORKFLOW_COMPLETED = 'WORKFLOW_COMPLETED'
    HOP_1_COMPLETED = 'HOP_1_COMPLETED'
    HOP_2_COMPLETED = 'HOP_2_COMPLETED'
    HOP_3_COMPLETED = 'HOP_3_COMPLETED'
    HOP_4_COMPLETED = 'HOP_4_COMPLETED'
    HOP_5_COMPLETED = 'HOP_5_COMPLETED'
    HOP_6_COMPLETED = 'HOP_6_COMPLETED'
    HOP_7_COMPLETED = 'HOP_7_COMPLETED'
    HOP_8_COMPLETED = 'HOP_8_COMPLETED'
    FACTUAL_LOOP_TRIGGERED = 'FACTUAL_LOOP_TRIGGERED'
    CREATIVE_LOOP_TRIGGERED = 'CREATIVE_LOOP_TRIGGERED'
    CIRCUIT_BREAKER_TRIGGERED = 'CIRCUIT_BREAKER_TRIGGERED'

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = 'IDLE'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class ValidationSeverity(Enum):
    """Validation result severity levels"""
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    INFO = 'INFO'

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    HALF_OPEN = 'HALF_OPEN'

class FailureClassifier(Enum):
    """
    Classifies S6 validation failures to determine retry strategy in HOP-7.
    """
    CREATIVE_FAILURE = 'CREATIVE_FAILURE'
    FACTUAL_FAILURE = 'FACTUAL_FAILURE'
