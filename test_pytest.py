def test_pytest_works():
    """Simple test to verify pytest is working"""
    assert True

def test_import():
    """Test that pytest can import basic modules"""
    import pytest
    assert pytest.__version__ is not None
