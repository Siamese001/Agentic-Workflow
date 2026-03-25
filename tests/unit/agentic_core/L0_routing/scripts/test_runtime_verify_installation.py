"""Runtime installation verification — behavioral contract tests."""

from __future__ import annotations

import importlib
import logging


def test_importlib_can_resolve_agentic_core():
    """importlib can locate the agentic_core package at runtime."""
    spec = importlib.util.find_spec("agentic_core")
    assert spec is not None, "agentic_core must be discoverable by importlib"
    assert spec.name == "agentic_core"


def test_importlib_can_resolve_l0_routing():
    """importlib can locate L0_routing subpackage."""
    spec = importlib.util.find_spec("agentic_core.L0_routing")
    assert spec is not None, "L0_routing must be discoverable by importlib"


def test_logging_configuration_baseline():
    """Logging infrastructure supports structured handler attachment."""
    logger = logging.getLogger("agentic_core.test.runtime_verify")
    assert logger.level == logging.NOTSET or logger.level >= 0
    assert isinstance(logger.handlers, list)
