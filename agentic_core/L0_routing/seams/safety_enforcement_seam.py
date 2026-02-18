"""
Seam for L5 safety enforcement - approved L0→L5 interface.
"""

from __future__ import annotations


def load_code_deduplication_agent():
    """Load CodeDeduplicationAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.enforcement.CodeDeduplicationAgent")
    return mod.CodeDeduplicationAgent


def load_archival_gatekeeper():
    """Load archival_gatekeeper from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.archival_gatekeeper")


def load_ssot_scanner():
    """Load ssot_scanner from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.ssot_scanner")
