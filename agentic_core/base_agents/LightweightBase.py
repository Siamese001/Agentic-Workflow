"""
LightweightAgentBase - Minimal Infrastructure for Simple Agents

Phase 4 MRO Refactoring: Alternative to full SovereignBaseAgent.

Provides only essential infrastructure:
- CostGuardrailMixin (budget control)
- ContextManagementMixin (context window management)
- TracingMixin (observability)
- CachingMixin (performance - from Phase 3 split)
- MetricsMixin (performance - from Phase 3 split)

Does NOT include:
- HITLMixin (human-in-the-loop - heavy, not always needed)
- PerformanceMixin (full version - use split mixins instead)
- PineconeVectorMixin (vector memory - optional)
- HealerMixin (healing - optional for simple agents)
- MCPHardenedMixin (MCP protocol - optional)
- SubatomicTestingMixin (self-testing - optional)

MRO Depth: ~8 classes (vs ~20+ for full SovereignBaseAgent)

Usage:
    class SimpleAgent(LightweightAgentBase):
        def __post_init__(self):
            super().__post_init__()
            # Agent-specific initialization

    # For agents needing healing, add it explicitly:
    class HealingAgent(HealerMixin, LightweightAgentBase):
        pass
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.mixins.caching_mixin import CachingMixin
from agentic_core.mixins.context_management_mixin import ContextManagementMixin
from agentic_core.mixins.cost_mixin import CostGuardrailMixin
from agentic_core.mixins.metrics_mixin import MetricsMixin
from agentic_core.mixins.tracing_mixin import TracingMixin
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class LightweightAgentBase(
    CostGuardrailMixin, ContextManagementMixin, TracingMixin, CachingMixin, MetricsMixin
):
    """
    Lightweight base agent with minimal infrastructure.

    Phase 4 MRO Refactoring: Reduced MRO depth for simple agents.

    Includes:
    - Cost control and budget enforcement
    - Context window management
    - Distributed tracing
    - LRU caching with TTL
    - Performance metrics collection

    For additional capabilities, inherit from the relevant mixins:
    - HealerMixin: For autonomous healing
    - HITLMixin: For human-in-the-loop workflows
    - BatchingMixin: For batch operations
    - MCPHardenedMixin: For MCP protocol safety
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initializes all parent mixins in the correct MRO order."""
        super().__init__(**kwargs)
        self._lightweight_initialized = True
        Logger.debug(f"[LIGHTWEIGHT] {self.__class__.__name__} lightweight agent initialized")

    def verify_lightweight_state(self) -> bool:
        """
        Verify that lightweight infrastructure was properly initialized.

        Returns:
            True if all checks pass

        Raises:
            RuntimeError: If any initialization check fails
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LightweightAgentBase.verify_lightweight_state")

        errors = []
        if not getattr(self, "_lightweight_initialized", False):
            errors.append(
                f"{self.__class__.__name__}: _lightweight_initialized is False. Did you forget to call super().__post_init__()?"
            )
        if errors:
            error_msg = "Lightweight initialization failed:\n" + "\n".join(f"  - {e}" for e in errors)
            Logger.error(f"[LIGHTWEIGHT] {error_msg}")
            raise RuntimeError(error_msg)
        return True

    def get_lightweight_status(self) -> dict[str, Any]:
        """Get current status of lightweight infrastructure."""
        return {
            "lightweight_initialized": getattr(self, "_lightweight_initialized", False),
            "class_name": self.__class__.__name__,
            "mro_depth": len(type(self).__mro__),
            "capabilities": ["cost_control", "context_management", "tracing", "caching", "metrics"],
        }


__all__ = ["LightweightAgentBase"]
