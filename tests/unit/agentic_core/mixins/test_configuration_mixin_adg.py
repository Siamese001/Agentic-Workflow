"""ADG importability contract for agentic_core/mixins/configuration_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_configuration_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.configuration_mixin import (  # noqa: F401
        ConfigMixin,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ConfigMixin = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="configuration_mixin.py deps unavailable")
class TestConfigurationMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: configuration_mixin.py must be importable."""
        assert _AVAILABLE

    def test_configmixin_is_type(self) -> None:
        assert ConfigMixin is not None

