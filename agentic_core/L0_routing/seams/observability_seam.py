"""
Seam for L6 observability - approved L0→L6 interface.
"""

from __future__ import annotations


def load_meta_learning_agent():
    """Load MetaLearningClient from L1 cognition (canonical meta-learning interface).

    Note: agentic_core.L6_observability.meta_learning does not exist.
    The canonical meta-learning client lives in L1_cognition.
    Returns None if the module cannot be imported (fail-open for seam).
    """
    import importlib

    try:
        mod = importlib.import_module("agentic_core.L1_cognition.engines.meta_client")
        return mod.MetaLearningClient
    except ImportError:
        return None
