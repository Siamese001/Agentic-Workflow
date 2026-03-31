"""ADG importability contract for apps_shared/reasoning/BaseReflectionAgent.py."""
from __future__ import annotations


def test_module_importable():
    """Module BaseReflectionAgent must be importable."""
    import apps_shared.reasoning.BaseReflectionAgent  # noqa: F401

    assert apps_shared.reasoning.BaseReflectionAgent is not None
