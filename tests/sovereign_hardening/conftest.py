"""Pytest configuration for sovereign hardening test suite."""

import os

import pytest

from agentic_core.L2_execution.UniversalWriteGateway import reset_write_gateway
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)


@pytest.fixture(scope="function", autouse=True)
def inject_test_key_source():
    """Inject TestKeySource before every test so SandboxEnvelope construction works."""
    inject_key_source(TestKeySource())
    yield
    # Reset to None so tests do not leak into each other
    import agentic_core.L2_execution.enforcement.key_source as _ks
    _ks._injected_key_source = None


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
    """Modify test collection to add markers based on test names.

    Adds sovereign_hardening marker to every item in this suite so the
    global conftest default-marker filter does not deselect them.
    """
    sovereign_marker = pytest.mark.sovereign_hardening
    for item in items:
        # Only process items from this suite
        if "sovereign_hardening" not in str(item.fspath):
            continue
        # Always add sovereign_hardening so global filter passes it through
        item.add_marker(sovereign_marker)
        if "negative_control" in item.name or "tamper" in item.name.lower():
            item.add_marker(pytest.mark.negative_control)
        if "determinism" in item.name.lower():
            item.add_marker(pytest.mark.determinism)
        if "sovereignty" in item.name.lower() or "boundary" in item.name.lower():
            item.add_marker(pytest.mark.sovereignty)
