"""ADG importability contract for apps_shared/reasoning/BaseDispatchAgent.py."""
from __future__ import annotations



def test_module_importable():
    """Module BaseDispatchAgent must be importable."""
    import apps_shared.reasoning.BaseDispatchAgent  # noqa: F401

    assert apps_shared.reasoning.BaseDispatchAgent is not None
