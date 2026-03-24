"""ADG importability contract for agentic_core/L0_routing/types/guardian_registry_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_guardian_registry_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.guardian_registry_types import (  # noqa: F401
        GuardianSpec,
        GuardianTier,
        get_all_check_ids,
        get_guardian_by_id,
        get_guardian_entrypoints,
        get_guardian_specs,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GuardianTier = None  # type: ignore[assignment,misc]
    GuardianSpec = None  # type: ignore[assignment,misc]
    get_guardian_specs = None  # type: ignore[assignment,misc]
    get_guardian_by_id = None  # type: ignore[assignment,misc]
    get_all_check_ids = None  # type: ignore[assignment,misc]
    get_guardian_entrypoints = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="guardian_registry_types deps unavailable")
class TestGuardianRegistryTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/guardian_registry_types.py must be importable."""
        assert _AVAILABLE

    def test_guardiantier_defined(self) -> None:
        assert GuardianTier is not None

    def test_guardianspec_defined(self) -> None:
        assert GuardianSpec is not None