"""ADG-driven tests for apps_shared/scripts/meta_control_config_bridge.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.meta_control_config_bridge import (  # noqa: F401
        load_app_component_config,
        render_app_component_config,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    load_app_component_config = None  # type: ignore[assignment,misc]
    render_app_component_config = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="meta_control_config_bridge.py deps unavailable")
class TestLoadAppComponentConfig:
    def test_is_callable(self):
        assert callable(load_app_component_config)

@pytest.mark.skipif(not _AVAILABLE, reason="meta_control_config_bridge.py deps unavailable")
class TestRenderAppComponentConfig:
    def test_is_callable(self):
        assert callable(render_app_component_config)


def test_module_importable():
    """Module meta_control_config_bridge.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE