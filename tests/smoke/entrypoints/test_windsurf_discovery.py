#!/usr/bin/env python3
"""
Simple test to verify Windsorf Testing tab discovery
"""


def test_windsurf_testing_tab_discovery():
    """Test that Windsorf can discover this simple test"""
    assert True is True
    assert 1 + 1 == 2


def test_pytest_configuration():
    """Test that pytest configuration is working"""
    import pytest

    assert pytest.__version__ is not None
