from dataclasses import dataclass
from enum import Enum
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class PolicySeverity(Enum):
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'

@dataclass
class SovereignPolicy:
    id: str
    description: str
    severity: PolicySeverity
    enabled: bool = True

class SovereignPolicyRegistry:
    """
    The Immutable Constitution of the Agentic Core.
    Defines what IS allowed, independent of HOW it is checked.
    """
    DATA_LOCALITY = SovereignPolicy(id='GOV-001', description='L4 State must not leave local execution environment without explicit encryption.', severity=PolicySeverity.CRITICAL)
    MAX_TOKENS_PER_TURN = SovereignPolicy(id='GOV-002', description='Single LLM turn must not exceed 32k tokens.', severity=PolicySeverity.HIGH)
    NO_PLAINTEXT_SECRETS = SovereignPolicy(id='GOV-003', description='No high-entropy strings (API keys) in logs or stdout.', severity=PolicySeverity.CRITICAL)

    @classmethod
    def get_all(cls):
        return [v for k, v in cls.__dict__.items() if isinstance(v, SovereignPolicy)]
