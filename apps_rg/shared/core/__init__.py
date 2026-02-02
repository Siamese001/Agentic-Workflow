"""
RG Core Infrastructure - LIC-Aligned Sovereign Architecture.

Provides the foundational components for all RG agents:
- RGAgentBase: Abstract base class with mixin integration
- ImmutableStagingBuffer: Write-once state management
- TraceRegistry: Structured execution tracing
"""

from __future__ import annotations

from apps_rg.shared.core.mixins import HealerMixin, MCPHardenedMixin, SubatomicTestingMixin
from apps_rg.shared.core.RGAgentBaseAgent import RGAgentBase
from apps_rg.shared.core.state_transaction_types import ImmutableStagingBuffer
from apps_rg.shared.core.trace_registry_types import TraceRegistry

__all__ = [
    "RGAgentBase",
    "ImmutableStagingBuffer",
    "TraceRegistry",
    "MCPHardenedMixin",
    "HealerMixin",
    "SubatomicTestingMixin",
]
