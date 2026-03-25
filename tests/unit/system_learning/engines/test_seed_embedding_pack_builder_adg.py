"""ADG importability contract for system_learning/engines/seed_embedding_pack_builder.py."""
from __future__ import annotations

import system_learning.engines.seed_embedding_pack_builder  # noqa: F401


def test_module_importable():
    """Module seed_embedding_pack_builder must be importable."""
    assert system_learning.engines.seed_embedding_pack_builder is not None
