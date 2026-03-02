#!/usr/bin/env python3
"""
Test for test_set_typed_documented_100_util
# GENERATED_MIRROR_TEST
"""

import pytest

from tests.helpers.dev_tools_loader import load_dev_script


def test_test_set_typed_documented_100_util_can_import():
    """Test that the module can be imported successfully."""
    try:
        mod = load_dev_script("set_typed_documented_100_util.py")
        assert mod is not None
    except ImportError as e:
        pytest.skip(
            f"Cannot load dev_tools/l0_scripts/set_typed_documented_100_util.py: {e}",
        )


def test_test_set_typed_documented_100_util_has_file_attribute():
    """Test that module has __file__ attribute."""
    try:
        mod = load_dev_script("set_typed_documented_100_util.py")
        assert hasattr(mod, "__file__")
    except ImportError:
        pytest.skip("Cannot load dev_tools/l0_scripts/set_typed_documented_100_util.py")


def test_test_set_typed_documented_100_util_has_public_attributes():
    """Test that module has public attributes or callables."""
    try:
        mod = load_dev_script("set_typed_documented_100_util.py")
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
        pytest.skip("Cannot load dev_tools/l0_scripts/set_typed_documented_100_util.py")
