"""ADG importability contract for system_learning/engines/faiss_startup_integrity.py."""
from __future__ import annotations



def test_module_importable():
    """Module faiss_startup_integrity must be importable."""
    import system_learning.engines.faiss_startup_integrity  # noqa: F401

    assert system_learning.engines.faiss_startup_integrity is not None
