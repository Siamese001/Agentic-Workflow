"""ADG importability contract for agentic_core/L2_execution/config/hybrid_retriever_config.py."""
from __future__ import annotations

import agentic_core.L2_execution.config.hybrid_retriever_config  # noqa: F401


def test_module_importable():
    """Module hybrid_retriever_config must be importable."""
    assert agentic_core.L2_execution.config.hybrid_retriever_config is not None
