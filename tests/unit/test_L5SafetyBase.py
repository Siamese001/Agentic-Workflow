#!/usr/bin/env python3
"""Tests for agentic_core.base_agents.L5SafetyBase."""
import importlib

import pytest


def test_agentic_core_base_agents_L5SafetyBase_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.base_agents.L5SafetyBase")
    assert m is not None

def test_l5_safety_base_is_class():
    import importlib
    m = importlib.import_module("agentic_core.base_agents.L5SafetyBase")
    assert hasattr(m, "L5SafetyBase")
    assert isinstance(m.L5SafetyBase, type)

def test_l5_safety_base_name():
    import importlib
    m = importlib.import_module("agentic_core.base_agents.L5SafetyBase")
    assert "L5" in m.L5SafetyBase.__name__
