"""ADG importability contract for system_learning/engines/embedding_service_factory.py."""
from __future__ import annotations

import system_learning.engines.embedding_service_factory  # noqa: F401


def test_module_importable():
    """Module embedding_service_factory must be importable."""
    assert system_learning.engines.embedding_service_factory is not None
