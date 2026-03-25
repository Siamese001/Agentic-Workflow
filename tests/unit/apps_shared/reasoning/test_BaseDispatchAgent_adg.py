"""ADG importability contract for apps_shared/reasoning/BaseDispatchAgent.py."""
from __future__ import annotations

import apps_shared.reasoning.BaseDispatchAgent  # noqa: F401


def test_module_importable():
    """Module BaseDispatchAgent must be importable."""
    assert apps_shared.reasoning.BaseDispatchAgent is not None
