"""
Seam for L6 vigilance event types - approved L0→L6 interface.
"""

from __future__ import annotations


def load_vigilance_types():
    """Load vigilance event types from L6."""
    import importlib

    return importlib.import_module("agentic_core.L6_observability.types.vigilance_event_types")


def get_vigilance_event_artifact():
    """Get VigilanceEventArtifact class."""
    return load_vigilance_types().VigilanceEventArtifact


def get_vigilance_severity():
    """Get VigilanceSeverity enum."""
    return load_vigilance_types().VigilanceSeverity
