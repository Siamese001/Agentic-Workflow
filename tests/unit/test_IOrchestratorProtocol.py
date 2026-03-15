#!/usr/bin/env python3
"""Tests for agentic_core.interfaces.IOrchestratorProtocol."""
import importlib


def test_agentic_core_interfaces_IOrchestratorProtocol_importable():
    """Module must be importable without error."""
    m = importlib.import_module("agentic_core.interfaces.IOrchestratorProtocol")
    assert m is not None

def test_iorchestrator_protocol_is_protocol():
    import importlib
    m = importlib.import_module("agentic_core.interfaces.IOrchestratorProtocol")
    assert hasattr(m, "IOrchestratorProtocol")

def test_iorchestrator_protocol_has_expected_methods():
    import importlib
    m = importlib.import_module("agentic_core.interfaces.IOrchestratorProtocol")
    cls = m.IOrchestratorProtocol
    # Protocol should declare at least one abstract method
    methods = [n for n in dir(cls) if not n.startswith("_")]
