"""ADG importability contract for agentic_core/utils/meta_learning_storage_util.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.utils.meta_learning_storage_util  # noqa: F401


def test_module_importable():
    import agentic_core.utils.meta_learning_storage_util  # noqa: F401
    """Module meta_learning_storage_util must be importable."""
    assert agentic_core.utils.meta_learning_storage_util is not None
