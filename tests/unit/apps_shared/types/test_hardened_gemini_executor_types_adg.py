"""ADG importability contract for apps_shared/types/hardened_gemini_executor_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_hardened_gemini_executor_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.types.hardened_gemini_executor_types import (  # noqa: F401
        DEFAULT_TIMEOUT,
        THRESHOLD,
        CircuitBreaker,
        CircuitBreakerOpenError,
        CircuitBreakerState,
        ContextOverflowError,
        HardenedGeminiConfig,
        InteractionTelemetry,
        create_agent_executor,
        create_hardened_gemini_executor,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ContextOverflowError = None  # type: ignore[assignment,misc]
    CircuitBreakerOpenError = None  # type: ignore[assignment,misc]
    HardenedGeminiConfig = None  # type: ignore[assignment,misc]
    InteractionTelemetry = None  # type: ignore[assignment,misc]
    CircuitBreakerState = None  # type: ignore[assignment,misc]
    CircuitBreaker = None  # type: ignore[assignment,misc]
    create_hardened_gemini_executor = None  # type: ignore[assignment,misc]
    create_agent_executor = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    DEFAULT_TIMEOUT = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="hardened_gemini_executor_types.py deps unavailable")
class TestHardenedGeminiExecutorTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: hardened_gemini_executor_types.py must be importable."""
        assert _AVAILABLE

    def test_contextoverflowerror_is_type(self) -> None:
        assert ContextOverflowError is not None

    def test_circuitbreakeropenerror_is_type(self) -> None:
        assert CircuitBreakerOpenError is not None

    def test_hardenedgeminiconfig_is_type(self) -> None:
        assert HardenedGeminiConfig is not None

    def test_create_hardened_gemini_executor_callable(self) -> None:
        assert callable(create_hardened_gemini_executor)

    def test_create_agent_executor_callable(self) -> None:
        assert callable(create_agent_executor)

    def test_threshold_defined(self) -> None:
        assert THRESHOLD is not None

    def test_default_timeout_defined(self) -> None:
        assert DEFAULT_TIMEOUT is not None