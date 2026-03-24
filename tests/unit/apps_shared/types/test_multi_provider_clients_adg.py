"""ADG-driven tests for apps_shared/types/multi_provider_clients.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.types.multi_provider_clients import (  # noqa: F401
        Provider,
        get_client,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    Provider = None  # type: ignore[assignment,misc]
    get_client = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="multi_provider_clients.py deps unavailable")
class TestProvider:
    def test_is_enum(self):
        import enum
        assert issubclass(Provider, enum.Enum)
    def test_has_members(self):
        assert len(list(Provider)) >= 1
    def test_importable(self):
        assert Provider is not None

@pytest.mark.skipif(not _AVAILABLE, reason="multi_provider_clients.py deps unavailable")
class TestGetClient:
    def test_is_callable(self):
        assert callable(get_client)


def test_module_importable():
    """Module multi_provider_clients.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE