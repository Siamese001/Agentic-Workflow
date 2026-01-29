"""
RG Core Infrastructure - LIC-Aligned Sovereign Architecture.

Provides the foundational components for all RG agents:
- RGAgentBase: Abstract base class with mixin integration
- ImmutableStagingBuffer: Write-once state management
- TraceRegistry: Structured execution tracing
"""

from __future__ import annotations

from apps_rg.shared.core.agent_base import RGAgentBase
from apps_rg.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_rg.shared.core.mixins import HealerMixin, SubatomicTestingMixin, mcp_hardened_mixin
from apps_rg.shared.core.trace_registry import TraceRegistry

__all__ = [
    "RGAgentBase",
    "ImmutableStagingBuffer",
    "TraceRegistry",
    "MCPHardenedMixin",
    "HealerMixin",
    "SubatomicTestingMixin",
]
