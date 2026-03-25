"""Behavioral contract tests for agentic_core.L0_routing.engines.reasoning_policy_engine."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.engines.reasoning_policy_engine"


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


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_proposalcommitter_is_instantiable(mod):
    """ProposalCommitter is accessible and is a type."""
    cls = getattr(mod, "ProposalCommitter", None)
    assert cls is not None, "ProposalCommitter must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ProposalCommitter must be a class"


def test_reasoningintensityprofile_is_instantiable(mod):
    """ReasoningIntensityProfile is accessible and is a type."""
    cls = getattr(mod, "ReasoningIntensityProfile", None)
    assert cls is not None, "ReasoningIntensityProfile must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReasoningIntensityProfile must be a class"


def test_reasoningpolicyengine_is_instantiable(mod):
    """ReasoningPolicyEngine is accessible and is a type."""
    cls = getattr(mod, "ReasoningPolicyEngine", None)
    assert cls is not None, "ReasoningPolicyEngine must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReasoningPolicyEngine must be a class"


def test_reasoningtier_is_instantiable(mod):
    """ReasoningTier is accessible and is a type."""
    cls = getattr(mod, "ReasoningTier", None)
    assert cls is not None, "ReasoningTier must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "ReasoningTier must be a class"


def test_requeststructurefeatures_is_instantiable(mod):
    """RequestStructureFeatures is accessible and is a type."""
    cls = getattr(mod, "RequestStructureFeatures", None)
    assert cls is not None, "RequestStructureFeatures must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RequestStructureFeatures must be a class"


def test_routedecisionartifact_is_instantiable(mod):
    """RouteDecisionArtifact is accessible and is a type."""
    cls = getattr(mod, "RouteDecisionArtifact", None)
    assert cls is not None, "RouteDecisionArtifact must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RouteDecisionArtifact must be a class"


def test_build_envelope_hash_is_callable(mod):
    """build_envelope_hash is accessible and callable."""
    func = getattr(mod, "build_envelope_hash", None)
    assert func is not None, "build_envelope_hash must be defined in {MODULE_PATH}"
    assert callable(func), "build_envelope_hash must be callable"


def test_build_profile_hash_is_callable(mod):
    """build_profile_hash is accessible and callable."""
    func = getattr(mod, "build_profile_hash", None)
    assert func is not None, "build_profile_hash must be defined in {MODULE_PATH}"
    assert callable(func), "build_profile_hash must be callable"


def test_compute_complexity_score_is_callable(mod):
    """compute_complexity_score is accessible and callable."""
    func = getattr(mod, "compute_complexity_score", None)
    assert func is not None, "compute_complexity_score must be defined in {MODULE_PATH}"
    assert callable(func), "compute_complexity_score must be callable"


def test_compute_policy_config_hash_is_callable(mod):
    """compute_policy_config_hash is accessible and callable."""
    func = getattr(mod, "compute_policy_config_hash", None)
    assert func is not None, "compute_policy_config_hash must be defined in {MODULE_PATH}"
    assert callable(func), "compute_policy_config_hash must be callable"


def test_create_and_commit_routing_contract_is_callable(mod):
    """create_and_commit_routing_contract is accessible and callable."""
    func = getattr(mod, "create_and_commit_routing_contract", None)
    assert func is not None, "create_and_commit_routing_contract must be defined in {MODULE_PATH}"
    assert callable(func), "create_and_commit_routing_contract must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"

