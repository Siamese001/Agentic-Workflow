"""ADG importability contract for system_learning/engines/faiss_startup_integrity.py."""
from __future__ import annotations

import system_learning.engines.faiss_startup_integrity  # noqa: F401


def test_module_importable():
    """Module faiss_startup_integrity must be importable."""
    assert system_learning.engines.faiss_startup_integrity is not None
