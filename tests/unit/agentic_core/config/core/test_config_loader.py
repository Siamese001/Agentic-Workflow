#!/usr/bin/env python3
"""Tests for agentic_core.config.core.config_loader."""
import importlib


def test_agentic_core_config_core_config_loader_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.config.core.config_loader")
    assert m is not None

def test_config_loader_module_has_expected_callables():
    import importlib
    m = importlib.import_module("agentic_core.config.core.config_loader")
    # Module must expose something callable
    callables = [n for n in dir(m) if callable(getattr(m, n)) and not n.startswith("_")]
    assert len(callables) > 0, "config_loader must expose at least one callable"
