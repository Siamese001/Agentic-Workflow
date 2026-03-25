"""ADG importability contract for apps_shared/types/integration_layer_types.py."""
from __future__ import annotations

import apps_shared.types.integration_layer_types  # noqa: F401


def test_module_importable():
    """Module integration_layer_types must be importable."""
    assert apps_shared.types.integration_layer_types is not None
