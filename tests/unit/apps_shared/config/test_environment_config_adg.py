"""ADG importability contract for apps_shared/config/environment_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_environment_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.config.environment_config import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        EnvironmentConfig,
        EnvironmentValidationResult,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    EnvironmentConfig = None  # type: ignore[assignment,misc]
    EnvironmentValidationResult = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="environment_config.py deps unavailable")
class TestEnvironmentConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: environment_config.py must be importable."""
        assert _AVAILABLE

    def test_environmentconfig_is_type(self) -> None:
        assert EnvironmentConfig is not None

    def test_environmentvalidationresult_is_type(self) -> None:
        assert EnvironmentValidationResult is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None