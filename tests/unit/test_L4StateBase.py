#!/usr/bin/env python3
"""Tests for agentic_core.base_agents.L4StateBase."""
import importlib

import pytest


def test_agentic_core_base_agents_L4StateBase_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.base_agents.L4StateBase")
    assert m is not None

def test_l4_state_base_is_class():
    import importlib
    m = importlib.import_module("agentic_core.base_agents.L4StateBase")
    assert hasattr(m, "L4StateBase")
    assert isinstance(m.L4StateBase, type)

def test_l4_state_base_name():
    import importlib
    m = importlib.import_module("agentic_core.base_agents.L4StateBase")
    assert "L4" in m.L4StateBase.__name__
