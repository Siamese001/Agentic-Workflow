"""ADG importability contract for system_learning/engines/seed_embedding_pack_builder.py."""
from __future__ import annotations

def test_module_importable():
    """Module seed_embedding_pack_builder must be importable."""
    import system_learning.engines.seed_embedding_pack_builder
    assert system_learning.engines.seed_embedding_pack_builder is not None
