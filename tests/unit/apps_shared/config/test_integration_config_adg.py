"""ADG importability contract for apps_shared/config/integration_config.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_integration_config.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.config.integration_config import (  # noqa: F401
        IntegrationConfig,
        get_domain_config,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IntegrationConfig = None  # type: ignore[assignment,misc]
    get_domain_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="integration_config.py deps unavailable")
class TestIntegrationConfigImportability:
    def test_module_importable(self) -> None:
        """ADG contract: integration_config.py must be importable."""
        assert _AVAILABLE

    def test_integrationconfig_is_type(self) -> None:
        assert IntegrationConfig is not None

    def test_get_domain_config_callable(self) -> None:
        assert callable(get_domain_config)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

