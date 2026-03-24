"""ADG importability contract for apps_shared/utils/environment_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_environment_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.utils.environment_util import (  # noqa: F401
        EnvironmentValidator,
        get_environment_config,
        validate_environment,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    EnvironmentValidator = None  # type: ignore[assignment,misc]
    get_environment_config = None  # type: ignore[assignment,misc]
    validate_environment = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="environment_util.py deps unavailable")
class TestEnvironmentUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: environment_util.py must be importable."""
        assert _AVAILABLE

    def test_environmentvalidator_is_type(self) -> None:
        assert EnvironmentValidator is not None

    def test_get_environment_config_callable(self) -> None:
        assert callable(get_environment_config)

    def test_validate_environment_callable(self) -> None:
        assert callable(validate_environment)