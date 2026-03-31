"""ADG importability contract for apps_shared/types/integration_layer_types.py."""
from __future__ import annotations


def test_module_importable():
    """Module integration_layer_types must be importable."""
    import apps_shared.types.integration_layer_types  # noqa: F401

    assert apps_shared.types.integration_layer_types is not None
