"""ADG importability contract for apps_shared/config/environment_config.py."""
from __future__ import annotations

import apps_shared.config.environment_config  # noqa: F401


def test_module_importable():
    """Module environment_config must be importable."""
    assert apps_shared.config.environment_config is not None
