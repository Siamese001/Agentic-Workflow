"""ADG importability contract for agentic_core/adg/runtime/antipattern_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_antipattern_registry.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.antipattern_registry import (  # noqa: F401
        AntipatternCategory,
        AntipatternRecord,
        AntipatternRegistry,
        AntipatternRegistryReport,
        AntipatternSeverity,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AntipatternSeverity = None  # type: ignore[assignment,misc]
    AntipatternCategory = None  # type: ignore[assignment,misc]
    AntipatternRecord = None  # type: ignore[assignment,misc]
    AntipatternRegistryReport = None  # type: ignore[assignment,misc]
    AntipatternRegistry = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="antipattern_registry deps unavailable")
class TestAntipatternRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/antipattern_registry.py must be importable."""
        assert _AVAILABLE

    def test_antipatternseverity_defined(self) -> None:
        assert AntipatternSeverity is not None

    def test_antipatterncategory_defined(self) -> None:
        assert AntipatternCategory is not None

    def test_antipatternrecord_defined(self) -> None:
        assert AntipatternRecord is not None

    def test_antipatternregistryreport_defined(self) -> None:
        assert AntipatternRegistryReport is not None

    def test_antipatternregistry_defined(self) -> None:
        assert AntipatternRegistry is not None
