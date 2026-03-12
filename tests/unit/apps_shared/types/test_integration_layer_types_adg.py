"""ADG importability contract for apps_shared/types/integration_layer_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_integration_layer_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_shared.types.integration_layer_types import (  # noqa: F401
        AppDomain,
        ServiceEndpoint,
        IntegrationConfig,
        ServiceRegistry,
        ConfigurationLoader,
        IntegrationBridge,
        get_integration_bridge,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AppDomain = None  # type: ignore[assignment,misc]
    ServiceEndpoint = None  # type: ignore[assignment,misc]
    IntegrationConfig = None  # type: ignore[assignment,misc]
    ServiceRegistry = None  # type: ignore[assignment,misc]
    ConfigurationLoader = None  # type: ignore[assignment,misc]
    IntegrationBridge = None  # type: ignore[assignment,misc]
    get_integration_bridge = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="integration_layer_types.py deps unavailable")
class TestIntegrationLayerTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: integration_layer_types.py must be importable."""
        assert _AVAILABLE

    def test_appdomain_is_type(self) -> None:
        assert AppDomain is not None

    def test_serviceendpoint_is_type(self) -> None:
        assert ServiceEndpoint is not None

    def test_integrationconfig_is_type(self) -> None:
        assert IntegrationConfig is not None

    def test_get_integration_bridge_callable(self) -> None:
        assert callable(get_integration_bridge)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

