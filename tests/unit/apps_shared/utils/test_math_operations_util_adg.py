"""ADG importability contract for apps_shared/utils/math_operations_util.py."""
from __future__ import annotations



def test_module_importable():
    """Module math_operations_util must be importable."""
    import apps_shared.utils.math_operations_util  # noqa: F401

    assert apps_shared.utils.math_operations_util is not None