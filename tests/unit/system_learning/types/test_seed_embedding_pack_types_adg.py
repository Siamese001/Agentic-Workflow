"""ADG importability contract for system_learning/types/seed_embedding_pack_types.py."""
from __future__ import annotations



def test_module_importable():
    """Module seed_embedding_pack_types must be importable."""
    import system_learning.types.seed_embedding_pack_types  # noqa: F401

    assert system_learning.types.seed_embedding_pack_types is not None