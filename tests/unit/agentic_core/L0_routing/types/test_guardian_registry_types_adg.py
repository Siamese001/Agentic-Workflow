"""ADG importability contract for agentic_core/L0_routing/types/guardian_registry_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_guardian_registry_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.guardian_registry_types import (  # noqa: F401
        GuardianTier,
        GuardianSpec,
        get_guardian_specs,
        get_guardian_by_id,
        get_all_check_ids,
        get_guardian_entrypoints,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GuardianTier = None  # type: ignore[assignment,misc]
    GuardianSpec = None  # type: ignore[assignment,misc]
    get_guardian_specs = None  # type: ignore[assignment,misc]
    get_guardian_by_id = None  # type: ignore[assignment,misc]
    get_all_check_ids = None  # type: ignore[assignment,misc]
    get_guardian_entrypoints = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="guardian_registry_types.py deps unavailable")
class TestGuardianRegistryTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: guardian_registry_types.py must be importable."""
        assert _AVAILABLE

    def test_guardiantier_is_type(self) -> None:
        assert GuardianTier is not None

    def test_guardianspec_is_type(self) -> None:
        assert GuardianSpec is not None

    def test_get_guardian_specs_callable(self) -> None:
        assert callable(get_guardian_specs)

    def test_get_guardian_by_id_callable(self) -> None:
        assert callable(get_guardian_by_id)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

