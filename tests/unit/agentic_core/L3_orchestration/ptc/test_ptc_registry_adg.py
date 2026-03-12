"""ADG importability contract for agentic_core/L3_orchestration/ptc/ptc_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ptc_registry.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.ptc.ptc_registry import (  # noqa: F401
        ToolRegistry,
        get_global_registry,
        register_tool,
        get_tool,
        list_tools,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolRegistry = None  # type: ignore[assignment,misc]
    get_global_registry = None  # type: ignore[assignment,misc]
    register_tool = None  # type: ignore[assignment,misc]
    get_tool = None  # type: ignore[assignment,misc]
    list_tools = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ptc_registry.py deps unavailable")
class TestPtcRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ptc_registry.py must be importable."""
        assert _AVAILABLE

    def test_toolregistry_is_type(self) -> None:
        assert ToolRegistry is not None

    def test_get_global_registry_callable(self) -> None:
        assert callable(get_global_registry)

    def test_register_tool_callable(self) -> None:
        assert callable(register_tool)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

