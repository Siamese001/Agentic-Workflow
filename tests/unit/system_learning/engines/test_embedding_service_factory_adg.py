"""ADG importability contract for system_learning/engines/embedding_service_factory.py."""
from __future__ import annotations

def test_module_importable():
    """Module embedding_service_factory must be importable."""
    import system_learning.engines.embedding_service_factory
    assert system_learning.engines.embedding_service_factory is not None
