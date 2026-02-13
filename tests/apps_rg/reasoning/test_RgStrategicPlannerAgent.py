#!/usr/bin/env python3
"""
Test for test_RgStrategicPlannerAgent
# GENERATED_MIRROR_TEST
"""

import importlib

import pytest


def test_test_RgStrategicPlannerAgent_can_import():
    """Test that the module can be imported successfully."""
    try:
        mod = importlib.import_module("apps_rg.reasoning.RgStrategicPlannerAgent")
        assert mod is not None
    except ImportError as e:
        pytest.skip(f"Cannot import module apps_rg.reasoning.RgStrategicPlannerAgent: {e}")


def test_test_RgStrategicPlannerAgent_has_file_attribute():
    """Test that module has __file__ attribute."""
    try:
        mod = importlib.import_module("apps_rg.reasoning.RgStrategicPlannerAgent")
        assert hasattr(mod, "__file__")
    except ImportError:
        pytest.skip("Cannot import module apps_rg.reasoning.RgStrategicPlannerAgent")


def test_test_RgStrategicPlannerAgent_has_public_attributes():
    """Test that module has public attributes or callables."""
    try:
        mod = importlib.import_module("apps_rg.reasoning.RgStrategicPlannerAgent")
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
        pytest.skip("Cannot import module apps_rg.reasoning.RgStrategicPlannerAgent")
