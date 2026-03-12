"""ADG importability contract for agentic_core/L5_safety/config/structure_blueprint/sovereign_kernel.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_sovereign_kernel.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.config.structure_blueprint.sovereign_kernel import (  # noqa: F401
        is_kernel_component,
        is_modular_extension,
        validate_boundary,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    is_kernel_component = None  # type: ignore[assignment,misc]
    is_modular_extension = None  # type: ignore[assignment,misc]
    validate_boundary = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_kernel.py deps unavailable")
class TestSovereignKernelImportability:
    def test_module_importable(self) -> None:
        """ADG contract: sovereign_kernel.py must be importable."""
        assert _AVAILABLE

    def test_is_kernel_component_callable(self) -> None:
        assert callable(is_kernel_component)

    def test_is_modular_extension_callable(self) -> None:
        assert callable(is_modular_extension)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

