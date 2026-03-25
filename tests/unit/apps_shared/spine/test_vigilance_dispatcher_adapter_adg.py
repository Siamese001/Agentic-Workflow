"""ADG importability contract for apps_shared/spine/vigilance_dispatcher_adapter.py."""
from __future__ import annotations

import apps_shared.spine.vigilance_dispatcher_adapter  # noqa: F401


def test_module_importable():
    """Module vigilance_dispatcher_adapter must be importable."""
    assert apps_shared.spine.vigilance_dispatcher_adapter is not None
