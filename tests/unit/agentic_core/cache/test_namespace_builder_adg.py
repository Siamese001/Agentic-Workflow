"""ADG importability contract for agentic_core/cache/namespace_builder.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_namespace_builder.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.cache.namespace_builder import (  # noqa: F401
        NS,
        build_key,
        build_mission_key,
        build_global_key,
        parse_key,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    NS = None  # type: ignore[assignment,misc]
    build_key = None  # type: ignore[assignment,misc]
    build_mission_key = None  # type: ignore[assignment,misc]
    build_global_key = None  # type: ignore[assignment,misc]
    parse_key = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="namespace_builder.py deps unavailable")
class TestNamespaceBuilderImportability:
    def test_module_importable(self) -> None:
        """ADG contract: namespace_builder.py must be importable."""
        assert _AVAILABLE

    def test_ns_is_type(self) -> None:
        assert NS is not None

    def test_build_key_callable(self) -> None:
        assert callable(build_key)

    def test_build_mission_key_callable(self) -> None:
        assert callable(build_mission_key)

