"""Wave C2 tests — CONSENSUS_JURORS SSOT registry.

Plan: `docs/archive/windsurf/legacy-tree/plans/consensus-validator-unification-5e9f3a.md` Wave C2.
"""

from __future__ import annotations

import importlib
import warnings

import pytest

pytestmark = pytest.mark.unit


def _reimport_model_registry():
    """Force-reimport the model_registry so env-var changes re-resolve."""
    import agentic_core.L0_routing.config.model_registry as mod  # noqa: PLC0415

    return importlib.reload(mod)


def test_default_consensus_jurors_is_three_heterogeneous():
    mod = _reimport_model_registry()
    jurors = mod.CONSENSUS_JURORS
    assert isinstance(jurors, tuple)
    assert len(jurors) == 3
    assert mod.OPENAI_MODEL_ID in jurors
    assert mod.ANTHROPIC_MODEL_ID in jurors
    assert mod.GEMINI_PRO_MODEL_ID in jurors


def test_env_var_override_accepts_custom_four_juror_set(monkeypatch):
    monkeypatch.setenv("CONSENSUS_JURORS", "j1,j2,j3,j4")
    mod = _reimport_model_registry()
    assert mod.CONSENSUS_JURORS == ("j1", "j2", "j3", "j4")


def test_env_var_override_strips_whitespace(monkeypatch):
    monkeypatch.setenv("CONSENSUS_JURORS", "  alpha  ,  beta , gamma  ")
    mod = _reimport_model_registry()
    assert mod.CONSENSUS_JURORS == ("alpha", "beta", "gamma")


def test_empty_env_var_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("CONSENSUS_JURORS", "   ")
    mod = _reimport_model_registry()
    assert len(mod.CONSENSUS_JURORS) == 3


def test_all_commas_fallback_to_default(monkeypatch):
    """Pathological input of only separators → fallback to default."""
    monkeypatch.setenv("CONSENSUS_JURORS", ", , ,")
    mod = _reimport_model_registry()
    assert len(mod.CONSENSUS_JURORS) == 3


def test_consensus_engine_uses_registry_default():
    """ConsensusEngine.__init__ default path sources from CONSENSUS_JURORS."""
    # Ensure no env override polluting this test.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from agentic_core.L0_routing.config.model_registry import CONSENSUS_JURORS  # noqa: PLC0415
        from agentic_core.L1_cognition.enforcement.consensus_validator import (  # noqa: PLC0415
            ConsensusEngine,
        )

    engine = ConsensusEngine()
    assert tuple(engine.providers) == CONSENSUS_JURORS


def test_caller_supplied_providers_still_wins():
    """Explicit providers= list overrides the registry default."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from agentic_core.L1_cognition.enforcement.consensus_validator import (  # noqa: PLC0415
            ConsensusEngine,
        )

    custom = ["custom-a", "custom-b"]
    engine = ConsensusEngine(providers=custom)
    assert engine.providers == custom


def test_consensus_jurors_exported_in_all():
    mod = _reimport_model_registry()
    assert "CONSENSUS_JURORS" in mod.__all__
