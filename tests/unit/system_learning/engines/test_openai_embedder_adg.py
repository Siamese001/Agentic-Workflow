"""ADG importability contract for system_learning/engines/openai_embedder.py."""
from __future__ import annotations

import system_learning.engines.openai_embedder  # noqa: F401


def test_module_importable():
    """Module openai_embedder must be importable."""
    assert system_learning.engines.openai_embedder is not None
