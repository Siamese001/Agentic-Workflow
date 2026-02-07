from dataclasses import dataclass
from enum import Enum


class PolicySeverity(Enum):
    CRITICAL = "CRITICAL"  # System halt
    HIGH = "HIGH"  # Mission abort
    MEDIUM = "MEDIUM"  # Warning + Log
    LOW = "LOW"  # Log only


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

    # 1. Data Sovereignty Laws
    DATA_LOCALITY = SovereignPolicy(
        id="GOV-001",
        description="L4 State must not leave local execution environment without explicit encryption.",
        severity=PolicySeverity.CRITICAL,
    )

    # 2. Resource Laws
    MAX_TOKENS_PER_TURN = SovereignPolicy(
        id="GOV-002", description="Single LLM turn must not exceed 32k tokens.", severity=PolicySeverity.HIGH
    )

    # 3. Security Laws
    NO_PLAINTEXT_SECRETS = SovereignPolicy(
        id="GOV-003",
        description="No high-entropy strings (API keys) in logs or stdout.",
        severity=PolicySeverity.CRITICAL,
    )

    @classmethod
    def get_all(cls):
        return [v for k, v in cls.__dict__.items() if isinstance(v, SovereignPolicy)]
