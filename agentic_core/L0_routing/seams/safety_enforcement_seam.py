"""
Seam for L5 safety enforcement - approved L0→L5 interface.
"""

from __future__ import annotations


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def load_code_deduplication_agent():
    """Load CodeDeduplicationAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.enforcement.CodeDeduplicationAgent")
    return mod.CodeDeduplicationAgent


def load_archival_gatekeeper():
    """Load archival_gatekeeper from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.archival_gatekeeper_gate")


def load_ssot_scanner():
    """Load ssot_scanner from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.ssot_scanner_enforcer")


def load_activation_gate():
    """Load activation_gate from L5 — approved seam for healing approval mediation."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.activation_gate")
