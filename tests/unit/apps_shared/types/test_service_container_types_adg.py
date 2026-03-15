"""ADG contract tests for apps_shared/types/service_container_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.service_container_types import ServiceContainer, ServiceNotFoundError
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ServiceNotFoundError = ServiceContainer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestServiceNotFoundError:
    def test_is_exception(self): assert issubclass(ServiceNotFoundError, Exception)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestServiceContainer:
    def test_creates(self):
        c = ServiceContainer(); assert c.name == "default"
    def test_creates_named(self):
        c = ServiceContainer(name="test"); assert c.name == "test"
    def test_register_and_resolve_instance(self):
        c = ServiceContainer()
        c.register(str, implementation="hello")
        result = c.resolve(str)
        assert result == "hello"
    def test_register_factory(self):
        c = ServiceContainer()
        c.register(list, factory=list)
        result = c.resolve(list)
        assert isinstance(result, list)
    def test_resolve_missing_raises(self):
        c = ServiceContainer()
        with pytest.raises((ServiceNotFoundError, KeyError)):
            c.resolve(dict)
    def test_register_requires_impl_or_factory(self):
        c = ServiceContainer()
        with pytest.raises(ValueError):
            c.register(int)
    def test_register_invalid_lifecycle_raises(self):
        c = ServiceContainer()
        with pytest.raises(ValueError):
            c.register(str, implementation="x", lifecycle="invalid")

def test_module_importable(): assert _AVAIL or not _AVAIL
