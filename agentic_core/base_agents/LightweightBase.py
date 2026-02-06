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
from dataclasses import dataclass
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class LightweightAgentBase(
    CostGuardrailMixin,
    ContextManagementMixin,
    TracingMixin,
    CachingMixin,
    MetricsMixin,
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

    def __post_init__(self) -> None:
        """Initialize lightweight infrastructure."""
        # Initialize all parent mixins
        # Note: dataclass doesn't call __init__ automatically for mixins
        # so we need to initialize them here

        # Initialize CachingMixin
        import threading
        from collections import OrderedDict

        from agentic_core.base_agents.caching_mixin import CacheConfig

        self._cache_config = CacheConfig()
        self._cache_store = OrderedDict()
        self._cache_lock = threading.RLock()
        self._caching_initialized = True

        # Initialize MetricsMixin
        from agentic_core.base_agents.metrics_mixin import MetricsConfig

        self._metrics_config = MetricsConfig()
        self._metrics_store = {}
        self._metrics_lock = threading.RLock()
        self._metrics_initialized = True

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
        errors = []

        if not getattr(self, "_lightweight_initialized", False):
            errors.append(
                f"{self.__class__.__name__}: _lightweight_initialized is False. "
                "Did you forget to call super().__post_init__()?",
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
            "capabilities": [
                "cost_control",
                "context_management",
                "tracing",
                "caching",
                "metrics",
            ],
        }


__all__ = ["LightweightAgentBase"]
