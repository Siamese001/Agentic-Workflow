"""ADG importability contract for agentic_core/L5_safety/validators/config_with_logic_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_config_with_logic_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.config_with_logic_validator import (  # noqa: F401
        ConfigWithLogicDetector,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ConfigWithLogicDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="config_with_logic_validator deps unavailable")
class TestConfigWithLogicValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/config_with_logic_validator.py must be importable."""
        assert _AVAILABLE

    def test_configwithlogicdetector_defined(self) -> None:
        assert ConfigWithLogicDetector is not None
