"""ADG importability contract for apps_lic/reasoning/LICValidationExecutor.py."""
from __future__ import annotations


def test_module_importable():
    """Module LICValidationExecutor must be importable."""
    import apps_lic.reasoning.LICValidationExecutor  # noqa: F401

    assert apps_lic.reasoning.LICValidationExecutor is not None
