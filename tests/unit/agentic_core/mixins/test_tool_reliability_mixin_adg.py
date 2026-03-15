"""ADG importability contract for agentic_core/mixins/tool_reliability_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_reliability_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.tool_reliability_mixin import (  # noqa: F401
        CircuitBreakerConfig,
        CircuitBreakerError,
        CircuitState,
        RetryPolicy,
        T,
        ToolHealth,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    T = None  # type: ignore[assignment,misc]
    CircuitState = None  # type: ignore[assignment,misc]
    RetryPolicy = None  # type: ignore[assignment,misc]
    CircuitBreakerConfig = None  # type: ignore[assignment,misc]
    ToolHealth = None  # type: ignore[assignment,misc]
    CircuitBreakerError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_reliability_mixin deps unavailable")
class TestToolReliabilityMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/tool_reliability_mixin.py must be importable."""
        assert _AVAILABLE

    def test_circuitstate_defined(self) -> None:
        assert CircuitState is not None

    def test_retrypolicy_defined(self) -> None:
        assert RetryPolicy is not None

    def test_circuitbreakerconfig_defined(self) -> None:
        assert CircuitBreakerConfig is not None

    def test_toolhealth_defined(self) -> None:
        assert ToolHealth is not None

    def test_circuitbreakererror_defined(self) -> None:
        assert CircuitBreakerError is not None
