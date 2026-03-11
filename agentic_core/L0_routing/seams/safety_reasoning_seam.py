"""
Seam for L5 safety reasoning agents - approved L0→L5 interface.
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

def load_naming_agent():
    """Load NamingAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.NamingAgent")
    return mod.NamingAgent


def load_structure_enforcer_agent():
    """Load StructureEnforcerAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.StructureEnforcerAgent")
    return mod.StructureEnforcerAgent


def load_cognitive_disposition_agent():
    """Load CognitiveDispositionAgent from L5 reasoning."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.CognitiveDispositionAgent")
    return mod.CognitiveDispositionAgent


def load_file_classification_agent():
    """Load FileClassificationAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.FileClassificationAgent")
    return mod.FileClassificationAgent


def load_location_validator_agent():
    """Load LocationValidatorAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.location_validator")
    return mod.LocationValidatorAgent


def load_verification_gate_adapter():
    """Load verification_gate_adapter from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.verification_gate_adapter")


def load_human_review_adapter():
    """Load human_review_adapter from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.human_review_adapter")


def load_inspector_executor():
    """Load InspectorExecutor from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
    return mod.InspectorExecutor
