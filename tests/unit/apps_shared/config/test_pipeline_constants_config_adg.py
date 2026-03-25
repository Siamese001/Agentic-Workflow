"""ADG importability contract for apps_shared/config/pipeline_constants_config.py."""
from __future__ import annotations

import apps_shared.config.pipeline_constants_config as _mod  # noqa: F401


def test_module_importable():
    """Module pipeline_constants_config must be importable."""
    assert _mod is not None
