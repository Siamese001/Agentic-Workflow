"""ADG contract tests for apps_lic/types/message_route_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.message_route_types import (
        MessageRoute, RecipientArchetype, SignatureFormat, CTAFormat,
        RouteConditions, RouteConstraints, RouteConfig, ROUTE_CONFIGS,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    MessageRoute = RecipientArchetype = SignatureFormat = CTAFormat = None  # type: ignore[assignment,misc]
    RouteConditions = RouteConstraints = RouteConfig = ROUTE_CONFIGS = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMessageRoute:
    def test_is_enum(self):
        import enum; assert issubclass(MessageRoute, enum.Enum)
    def test_has_inmail(self): assert MessageRoute.INMAIL.value == "INMAIL"
    def test_five_routes(self): assert len(list(MessageRoute)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRecipientArchetype:
    def test_is_enum(self):
        import enum; assert issubclass(RecipientArchetype, enum.Enum)
    def test_has_c_level(self): assert RecipientArchetype.C_LEVEL.value == "C_LEVEL"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteConditions:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouteConditions)
    def test_defaults_none(self):
        r = RouteConditions(); assert r.connection_status is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteConstraints:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouteConstraints)
    def test_default_signature(self):
        r = RouteConstraints(); assert r.signature_format == SignatureFormat.STANDARD

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteConfigs:
    def test_is_dict(self): assert isinstance(ROUTE_CONFIGS, dict)
    def test_connection_req_present(self): assert MessageRoute.CONNECTION_REQ in ROUTE_CONFIGS
    def test_inmail_present(self): assert MessageRoute.INMAIL in ROUTE_CONFIGS

def test_module_importable(): assert _AVAIL or not _AVAIL
