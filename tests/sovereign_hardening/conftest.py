"""Pytest configuration for sovereign hardening test suite."""

import pytest
import os
from unittest.mock import patch

from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway, reset_write_gateway


@pytest.fixture(scope="function", autouse=True)
def reset_write_gateway_fixture():
    """Reset write gateway before each test."""
    reset_write_gateway()
    yield
    reset_write_gateway()


@pytest.fixture(scope="function")
def tamper_env():
    """Fixture to temporarily enable W_HARDEN_NEGCTRL_TAMPER."""
    original_value = os.environ.get('W_HARDEN_NEGCTRL_TAMPER')
    os.environ['W_HARDEN_NEGCTRL_TAMPER'] = '1'
    yield
    if original_value is None:
        os.environ.pop('W_HARDEN_NEGCTRL_TAMPER', None)
    else:
        os.environ['W_HARDEN_NEGCTRL_TAMPER'] = original_value


@pytest.fixture(scope="function")
def clean_env():
    """Fixture to ensure clean environment (no tampering)."""
    original_value = os.environ.get('W_HARDEN_NEGCTRL_TAMPER')
    os.environ.pop('W_HARDEN_NEGCTRL_TAMPER', None)
    yield
    if original_value is not None:
        os.environ['W_HARDEN_NEGCTRL_TAMPER'] = original_value


def pytest_configure(config):
    """Configure pytest for sovereign hardening tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "negative_control: Tests that use W_HARDEN_NEGCTRL_TAMPER"
    )
    config.addinivalue_line(
        "markers", "determinism: Tests for determinism validation"
    )
    config.addinivalue_line(
        "markers", "sovereignty: Tests for sovereignty enforcement"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        if "negative_control" in item.name or "tamper" in item.name.lower():
            item.add_marker(pytest.mark.negative_control)
        if "determinism" in item.name.lower():
            item.add_marker(pytest.mark.determinism)
        if "sovereignty" in item.name.lower() or "boundary" in item.name.lower():
            item.add_marker(pytest.mark.sovereignty)
