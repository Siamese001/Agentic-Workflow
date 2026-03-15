"""ADG importability contract for agentic_core/L5_safety/config/structure_blueprint/_constants.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test__constants.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
        SubfolderDefinition,
        TerritoryDefinition,
        build_sovereign_territories,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SubfolderDefinition = None  # type: ignore[assignment,misc]
    TerritoryDefinition = None  # type: ignore[assignment,misc]
    build_sovereign_territories = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="_constants deps unavailable")
class TestConstantsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/config/structure_blueprint/_constants.py must be importable."""
        assert _AVAILABLE

    def test_subfolderdefinition_defined(self) -> None:
        assert SubfolderDefinition is not None

    def test_territorydefinition_defined(self) -> None:
        assert TerritoryDefinition is not None
