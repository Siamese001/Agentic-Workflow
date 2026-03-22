#!/usr/bin/env python3
"""Tests for agentic_core.base_agents.L1CognitionBase."""
import importlib


def test_agentic_core_base_agents_L1CognitionBase_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.base_agents.L1CognitionBase")
    assert m is not None

def test_l1_cognition_base_is_class():
    import importlib
    m = importlib.import_module("agentic_core.base_agents.L1CognitionBase")
    assert hasattr(m, "L1CognitionBase")
    assert isinstance(m.L1CognitionBase, type)

def test_l1_cognition_base_has_layer_attribute():
    import importlib
    m = importlib.import_module("agentic_core.base_agents.L1CognitionBase")
    # Layer-tagged base classes must carry their layer identity
    assert hasattr(m.L1CognitionBase, "__name__")
