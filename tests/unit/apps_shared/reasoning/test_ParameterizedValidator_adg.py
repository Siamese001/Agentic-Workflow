"""ADG importability contract for apps_shared/reasoning/ParameterizedValidator.py."""
from __future__ import annotations


def test_module_importable():
    """Module ParameterizedValidator must be importable."""
    import apps_shared.reasoning.ParameterizedValidator  # noqa: F401

    assert apps_shared.reasoning.ParameterizedValidator is not None
