#!/usr/bin/env python3
"""Tests for agentic_core.config.sovereign_config."""
import importlib


def test_agentic_core_config_core_sovereign_config_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.config.sovereign_config")
    assert m is not None

def test_sovereign_config_manager_instantiates():
    import importlib
    m = importlib.import_module("agentic_core.config.sovereign_config")
    mgr = m.SovereignConfigManager()
    assert mgr is not None
