"""ADG importability contract for system_learning/engines/embedding_retention_scheduler.py."""
from __future__ import annotations



def test_module_importable():
    """Module embedding_retention_scheduler must be importable."""
    import system_learning.engines.embedding_retention_scheduler  # noqa: F401

    assert system_learning.engines.embedding_retention_scheduler is not None
