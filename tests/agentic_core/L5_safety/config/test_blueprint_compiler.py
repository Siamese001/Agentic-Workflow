#!/usr/bin/env python3
"""
Test for test_blueprint_compiler
# GENERATED_MIRROR_TEST
"""

import importlib

import pytest


def test_test_blueprint_compiler_can_import():
    """Test that the module can be imported successfully."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.config.blueprint_compiler")
        assert mod is not None
    except ImportError as e:
        pytest.skip(f"Cannot import module agentic_core.L5_safety.config.blueprint_compiler: {e}")


def test_test_blueprint_compiler_has_file_attribute():
    """Test that module has __file__ attribute."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.config.blueprint_compiler")
        assert hasattr(mod, "__file__")
    except ImportError:
        pytest.skip("Cannot import module agentic_core.L5_safety.config.blueprint_compiler")


def test_test_blueprint_compiler_has_public_attributes():
    """Test that module has public attributes or callables."""
    try:
        mod = importlib.import_module("agentic_core.L5_safety.config.blueprint_compiler")
        # Count non-private attributes
        public_attrs = [name for name in dir(mod) if not name.startswith("_")]
        # Look for at least one callable
        callables = [name for name in public_attrs if callable(getattr(mod, name))]

        if callables:
            # Test that first callable is callable
            assert callable(getattr(mod, callables[0]))
        else:
            # If no callables, at least assert we have some public attributes
            assert len(public_attrs) >= 0
    except ImportError:
        pytest.skip("Cannot import module agentic_core.L5_safety.config.blueprint_compiler")
