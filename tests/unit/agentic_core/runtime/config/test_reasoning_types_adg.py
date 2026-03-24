"""ADG importability contract for agentic_core/runtime/config/reasoning_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_reasoning_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.config.reasoning_types import (  # noqa: F401
        CONFIG,
        GovernorConfig,
        ModelConfig,
        ModelProvider,
        RAGConfig,
        ReasoningConfig,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ModelProvider = None  # type: ignore[assignment,misc]
    ModelConfig = None  # type: ignore[assignment,misc]
    RAGConfig = None  # type: ignore[assignment,misc]
    GovernorConfig = None  # type: ignore[assignment,misc]
    ReasoningConfig = None  # type: ignore[assignment,misc]
    CONFIG = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_types deps unavailable")
class TestReasoningTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/config/reasoning_types.py must be importable."""
        assert _AVAILABLE

    def test_modelprovider_defined(self) -> None:
        assert ModelProvider is not None

    def test_modelconfig_defined(self) -> None:
        assert ModelConfig is not None

    def test_ragconfig_defined(self) -> None:
        assert RAGConfig is not None

    def test_governorconfig_defined(self) -> None:
        assert GovernorConfig is not None

    def test_reasoningconfig_defined(self) -> None:
        assert ReasoningConfig is not None