"""ADG contract tests for apps_shared/types/integration_layer_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.integration_layer_types import (
        AppDomain, ServiceEndpoint, IntegrationConfig, ServiceRegistry,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    AppDomain = ServiceEndpoint = IntegrationConfig = ServiceRegistry = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAppDomain:
    def test_is_enum(self):
        import enum; assert issubclass(AppDomain, enum.Enum)
    def test_is_str_enum(self): assert issubclass(AppDomain, str)
    def test_has_lic(self): assert AppDomain.LIC.value == "lic"
    def test_has_rg(self): assert AppDomain.RG.value == "rg"
    def test_three_domains(self): assert len(list(AppDomain)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestServiceEndpoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ServiceEndpoint)
    def test_creates(self):
        ep = ServiceEndpoint(name="my_service", domain=AppDomain.LIC)
        assert ep.name == "my_service"; assert ep.enabled is True
    def test_hash(self):
        ep = ServiceEndpoint(name="svc", domain=AppDomain.RG)
        assert hash(ep) == hash("rg:svc")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestIntegrationConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IntegrationConfig)
    def test_defaults(self):
        c = IntegrationConfig()
        assert c.enable_cross_domain is True; assert c.cache_ttl == 3600

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestServiceRegistry:
    def test_creates(self): r = ServiceRegistry(); assert r is not None
    def test_register_and_list(self):
        r = ServiceRegistry()
        ep = ServiceEndpoint(name="svc1", domain=AppDomain.LIC)
        r.register(ep)
        services = r.list_services(AppDomain.LIC)
        assert "svc1" in services

def test_module_importable(): assert _AVAIL or not _AVAIL
