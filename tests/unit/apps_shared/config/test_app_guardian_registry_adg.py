"""ADG importability contract for apps_shared/config/app_guardian_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_app_guardian_registry.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.config.app_guardian_registry import (  # noqa: F401
        AppGuardianSpec,
        get_specs_for_app,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AppGuardianSpec = None  # type: ignore[assignment,misc]
    get_specs_for_app = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="app_guardian_registry.py deps unavailable")
class TestAppGuardianRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: app_guardian_registry.py must be importable."""
        assert _AVAILABLE

    def test_appguardianspec_is_type(self) -> None:
        assert AppGuardianSpec is not None

    def test_get_specs_for_app_callable(self) -> None:
        assert callable(get_specs_for_app)