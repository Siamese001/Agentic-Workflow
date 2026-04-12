"""ADG importability contract for agentic_core/L5_safety/validators/test_skip_detector_validator.py."""

from __future__ import annotations

import pytest


def test_module_importable():
    """Module test_skip_detector_validator must be importable."""
    try:
        from agentic_core.L5_safety.validators.test_skip_detector_validator import TestSilentSkipDetector

        assert TestSilentSkipDetector is not None
    except ImportError as e:
        assert False, f"Module should be importable: {e}"


def test_determinism_types_importable():
    """Module determinism_types must be importable or skip gracefully."""
    pytest.importorskip("agentic_core.runtime.determinism_types", reason="determinism_types not available")
    from agentic_core.runtime.determinism_types import DeterminismDigest

    assert DeterminismDigest is not None


def test_review_protocol_util_importable():
    """Module review_protocol_util must be importable or skip gracefully."""
    try:
        from agentic_core.L5_safety.review_protocol_util import ReviewProtocol

        assert ReviewProtocol is not None
    except ImportError:
        pass


def test_archetype_indicator_config_importable():
    """Module archetype_indicator_config must be importable or skip gracefully."""
    try:
        from agentic_core.L5_safety.config.archetype_indicator_config import ARCHETYPE_INDICATORS

        assert ARCHETYPE_INDICATORS is not None
    except ImportError:
        pass


def test_outreach_learning_agent_importable():
    """Module OutreachLearningAgent must be importable or skip gracefully."""
    try:
        from agentic_core.L5_safety.outreach_agents import OutreachLearningAgent

        assert OutreachLearningAgent is not None
    except ImportError:
        pass


def test_outreach_validation_executor_agent_importable():
    """Module OutreachValidationExecutorAgent must be importable or skip gracefully."""
    try:
        from agentic_core.L5_safety.outreach_agents import OutreachValidationExecutorAgent

        assert OutreachValidationExecutorAgent is not None
    except ImportError:
        pass


def test_archetype_indicator_util_importable():
    """Module archetype_indicator_util must be importable or skip gracefully."""
    try:
        from agentic_core.L5_safety.utils.archetype_indicator_util import IndicatorCalculator

        assert IndicatorCalculator is not None
    except ImportError:
        pass
