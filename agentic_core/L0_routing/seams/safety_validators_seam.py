"""
Seam for L5 safety validators - approved L0→L5 interface.
"""

from __future__ import annotations


def load_hygiene_guardian():
    """Load HygieneGuardianAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.validators.HygieneGuardianAgent")
    return mod.HygieneGuardianAgent


def load_autonomy_guardian():
    """Load AutonomyGuardianAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.validators.AutonomyGuardianAgent")
    return mod.AutonomyGuardianAgent


def load_healing_strategy():
    """Load healing_strategy module from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.validators.healing_strategy")


def load_canonical_truth_validator():
    """Load canonical_truth_validator from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.validators.canonical_truth_validator")


def load_cognitive_disposition_agent():
    """Load CognitiveDispositionAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.validators.CognitiveDispositionAgent")
    return mod.CognitiveDispositionAgent


def load_dashboard_ssot_definitions():
    """Load dashboard_ssot_definitions_config from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.validators.dashboard_ssot_definitions_config")
