"""
agentic_core/L1_cognition/reasoning/types/domain_types.py

Passive data structures for DomainContextManager.
Extracted from engine/domain_manager.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class SharingPolicy(Enum):
    """Policy for cross-domain pattern sharing."""

    NONE = "none"
    READ_ONLY = "read_only"
    BIDIRECTIONAL = "bidirectional"
    SELECTIVE = "selective"


@dataclass
class DomainContext:
    """
    Context for a specific domain.

    Attributes:
        domain: Domain identifier
        parent_domain: Parent domain for inheritance (if any)
        sharing_policy: Policy for cross-domain sharing
        allowed_sources: Domains allowed to share patterns with this domain
        pattern_types_shared: Pattern types allowed for sharing (if selective)
    """

    domain: str
    parent_domain: str | None = None
    sharing_policy: SharingPolicy = SharingPolicy.NONE
    allowed_sources: list[str] = field(default_factory=list)
    pattern_types_shared: list[str] = field(default_factory=list)

    def can_read_from(self, source_domain: str) -> bool:
        """Check if this domain can read patterns from source domain."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "DomainContext.can_read_from")

        if self.sharing_policy == SharingPolicy.NONE:
            return False
        if self.sharing_policy == SharingPolicy.BIDIRECTIONAL:
            return True
        if source_domain in self.allowed_sources:
            return True
        if self.parent_domain == source_domain:
            return True
        return False

    def can_share_pattern_type(self, pattern_type: str) -> bool:
        """Check if a pattern type can be shared."""
        if self.sharing_policy == SharingPolicy.NONE:
            return False
        if self.sharing_policy in (SharingPolicy.READ_ONLY, SharingPolicy.BIDIRECTIONAL):
            return True
        if self.sharing_policy == SharingPolicy.SELECTIVE:
            return pattern_type in self.pattern_types_shared
        return False
