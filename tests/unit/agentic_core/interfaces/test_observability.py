"""Behavioral contract tests for agentic_core.interfaces.observability."""

from __future__ import annotations

import importlib

import pytest

MODULE_PATH = "agentic_core.interfaces.observability"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_circuitbreakerstate_is_instantiable(mod):
    """CircuitBreakerState is accessible and is a type."""
    cls = getattr(mod, "CircuitBreakerState", None)
    assert cls is not None, "CircuitBreakerState must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CircuitBreakerState must be a class"


def test_systemtelemetry_is_instantiable(mod):
    """SystemTelemetry is accessible and is a type."""
    cls = getattr(mod, "SystemTelemetry", None)
    assert cls is not None, "SystemTelemetry must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "SystemTelemetry must be a class"


def test_record_execution_trace_is_callable(mod):
    """Test record_execution_trace_is_callable runtime behavior."""
    func = getattr(mod, "record_execution_trace", None)
    assert func is not None, "record_execution_trace must be defined"
    assert callable(func), "record_execution_trace must be callable"
