"""ADG importability contract for apps_shared/reasoning/BaseProactiveAgent.py."""
from __future__ import annotations


def test_module_importable():
    """Module BaseProactiveAgent must be importable."""
    import apps_shared.reasoning.BaseProactiveAgent  # noqa: F401

    assert apps_shared.reasoning.BaseProactiveAgent is not None