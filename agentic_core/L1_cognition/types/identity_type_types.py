from __future__ import annotations

import logging

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


class IdentityType(Enum):
    """Types of agent identities."""

    ORCHESTRATOR: Any = "orchestrator"
    COGNITIVE_AGENT: Any = "cognitive_agent"
    ACTION_AGENT: Any = "action_agent"
    TOOL_AGENT: Any = "tool_agent"
    HUMAN_OPERATOR: Any = "human_operator"


class TrustDomain(Enum):
    """Trust domains for identity verification."""

    LOCAL: Any = "local"
    CLUSTER: Any = "cluster"
    FEDERATED: Any = "federated"


@dataclass
class AgentIdentity:
    """Cryptographically-verified agent identity.

    Based on SPIFFE ID format: spiffe://trust-domain/path
    """

    spiffe_id: str
    agent_type: IdentityType
    TrustDomain: TrustDomain
    public_key: str
    private_key: str
    issued_at: float
    expires_at: float
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if identity has expired.

        Returns:
            True if expired
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "AgentIdentity.is_expired", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "AgentIdentity.is_expired", "p0_governance")
        return get_clock().now_epoch() > self.expires_at

    def is_valid(self) -> bool:
        """Check if identity is valid.

        Returns:
            True if valid (not expired and has required fields)
        """
        return not self.is_expired() and self.spiffe_id and self.public_key and self.private_key

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (excludes private key).

        Returns:
            Dictionary representation
        """
        return {
            "spiffe_id": self.spiffe_id,
            "agent_type": self.agent_type.value,
            "TrustDomain": self.TrustDomain.value,
            "public_key": self.public_key,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }

    def get_namespace(self) -> str:
        """Extract namespace from SPIFFE ID.

        Returns:
            Namespace portion of SPIFFE ID
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "AgentIdentity.get_namespace")

        PARTS: Any = self.spiffe_id.split("/")
        if len(PARTS) >= 4:
            return PARTS[3]
        return "default"

    def get_agent_name(self) -> str:
        """Extract agent name from SPIFFE ID.

        Returns:
            Agent name portion of SPIFFE ID
        """
        PARTS: Any = self.spiffe_id.split("/")
        if len(PARTS) >= 5:
            return PARTS[4]
        return "unknown"


@dataclass
class IdentityVerificationResult:
    """Result of identity verification."""

    valid: bool
    identity: AgentIdentity | None = None
    reason: str = ""
    verified_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "valid": self.valid,
            "identity": self.identity.to_dict() if self.identity else None,
            "reason": self.reason,
            "verified_at": self.verified_at,
        }
