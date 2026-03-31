"""ADG importability contract for apps_shared/config/integration_config.py."""
from __future__ import annotations


def test_module_importable():
    """Module integration_config must be importable."""
    import apps_shared.config.integration_config  # noqa: F401

    assert apps_shared.config.integration_config is not None
