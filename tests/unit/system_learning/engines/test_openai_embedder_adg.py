"""ADG importability contract for system_learning/engines/openai_embedder.py."""
from __future__ import annotations

def test_module_importable():
    """Module openai_embedder must be importable."""
    import system_learning.engines.openai_embedder
    assert system_learning.engines.openai_embedder is not None
