"""ADG importability contract for system_learning/types/seed_embedding_pack_types.py."""
from __future__ import annotations

import system_learning.types.seed_embedding_pack_types  # noqa: F401


def test_module_importable():
    """Module seed_embedding_pack_types must be importable."""
    assert system_learning.types.seed_embedding_pack_types is not None
