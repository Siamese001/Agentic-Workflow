"""
Seam for L6 observability - approved L0→L6 interface.
"""

from __future__ import annotations


def load_meta_learning_agent():
    """Load MetaLearningAgent from L6."""
    import importlib

    mod = importlib.import_module("agentic_core.L6_observability.meta_learning.MetaLearningAgent")
    return mod.MetaLearningAgent
