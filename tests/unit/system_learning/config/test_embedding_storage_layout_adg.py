"""ADG importability contract for system_learning/config/embedding_storage_layout.py."""
from __future__ import annotations

def test_module_importable():
    """Module embedding_storage_layout must be importable."""
    import system_learning.config.embedding_storage_layout
    assert system_learning.config.embedding_storage_layout is not None