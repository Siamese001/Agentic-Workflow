"""ADG importability contract for apps_shared/utils/environment_util.py."""
from __future__ import annotations

import apps_shared.utils.environment_util  # noqa: F401


def test_module_importable():
    """Module environment_util must be importable."""
    assert apps_shared.utils.environment_util is not None
