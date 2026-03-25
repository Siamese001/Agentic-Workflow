"""ADG importability contract for agentic_core/utils/project_root_util.py."""
from __future__ import annotations

import agentic_core.utils.project_root_util  # noqa: F401


def test_module_importable():
    """Module project_root_util must be importable."""
    assert agentic_core.utils.project_root_util is not None
