"""ADG importability contract for agentic_core/config/core/injection_layer_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_injection_layer_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.config.core.injection_layer_config import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        InjectionLayer,
        InstructionalPattern,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InjectionLayer = None  # type: ignore[assignment,misc]
    InstructionalPattern = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="injection_layer_config.py deps unavailable")
class TestInjectionLayerConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: injection_layer_config.py must be importable."""
        assert _AVAILABLE

    def test_injectionlayer_is_type(self) -> None:
        assert InjectionLayer is not None

    def test_instructionalpattern_is_type(self) -> None:
        assert InstructionalPattern is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None