"""Importability contracts for trimmed validator dependencies."""

from __future__ import annotations

import pytest


def test_module_importable():
    module = pytest.importorskip(
        "agentic_core.L5_safety.validators.test_skip_detector_validator",
        reason="Requires test_skip_detector_validator from the monorepo checkout.",
    )
    assert getattr(module, "TestSilentSkipDetector", None) is not None


def test_determinism_types_importable():
    module = pytest.importorskip(
        "agentic_core.runtime.determinism_types",
        reason="determinism_types not available",
    )
    assert getattr(module, "DeterminismDigest", None) is not None


def test_review_protocol_util_importable():
    module = pytest.importorskip(
        "agentic_core.L5_safety.review_protocol_util",
        reason="review_protocol_util not available",
    )
    assert getattr(module, "ReviewProtocol", None) is not None


def test_archetype_indicator_config_importable():
    module = pytest.importorskip(
        "agentic_core.L5_safety.config.archetype_indicator_config",
        reason="archetype_indicator_config not available",
    )
    assert getattr(module, "ARCHETYPE_INDICATORS", None) is not None


def test_outreach_learning_agent_importable():
    module = pytest.importorskip(
        "agentic_core.L5_safety.outreach_agents",
        reason="outreach_agents not available",
    )
    assert getattr(module, "OutreachLearningAgent", None) is not None


def test_outreach_validation_executor_agent_importable():
    module = pytest.importorskip(
        "agentic_core.L5_safety.outreach_agents",
        reason="outreach_agents not available",
    )
    assert getattr(module, "OutreachValidationExecutorAgent", None) is not None


def test_archetype_indicator_util_importable():
    module = pytest.importorskip(
        "agentic_core.L5_safety.utils.archetype_indicator_util",
        reason="archetype_indicator_util not available",
    )
    assert getattr(module, "IndicatorCalculator", None) is not None
