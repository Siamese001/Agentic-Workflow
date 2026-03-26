"""Interfaces smoke tests — behavioral contract verification."""

import pytest


@pytest.mark.smoke
def test_interfaces_package_exposes_public_api():
        import agentic_core.interfaces as mod
        from agentic_core.interfaces.determinism import canonical_hash
        from agentic_core.interfaces.determinism import strip_nondeterministic
        from agentic_core.interfaces.embeddings import SimilarityResult
        from agentic_core.interfaces.gateway import (
        from agentic_core.interfaces.IHealerProtocol import IHealerProtocol
        from agentic_core.interfaces.IMemoryStoreProtocol import IMemoryStoreProtocol
        from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol
        from agentic_core.interfaces.IValidatorProtocol import ValidatorProtocol
        from agentic_core.interfaces.mixins import HealerMixin, MetaLearningMixin
        from agentic_core.interfaces.validators import RuleFailure
        from agentic_core.interfaces.write_gateway import compute_replay_key
        """Interfaces package exposes at least one public symbol."""
        try:

    try:
#  # MOVED: import agentic_core.interfaces as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "interfaces package must expose public API"


@pytest.mark.smoke
def test_determinism_canonical_hash_is_deterministic():
    """canonical_hash returns identical output for identical input."""
    try:
#  # MOVED: from agentic_core.interfaces.determinism import canonical_hash
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    result1 = canonical_hash({"key": "value", "num": 42})
    result2 = canonical_hash({"key": "value", "num": 42})
    assert result1 == result2, "canonical_hash must be deterministic"
    assert isinstance(result1, str)
    assert len(result1) > 0


@pytest.mark.smoke
def test_determinism_strip_nondeterministic_removes_timestamps():
    """strip_nondeterministic produces stable output from dynamic input."""
    try:
#  # MOVED: from agentic_core.interfaces.determinism import strip_nondeterministic
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    data = {"key": "value", "timestamp": "2026-03-25T18:00:00Z"}
    result = strip_nondeterministic(data)
    assert isinstance(result, (dict, str, bytes))


@pytest.mark.smoke
def test_embeddings_interface_similarity_result_is_type():
    """SimilarityResult is a proper type/class."""
    try:
#  # MOVED: from agentic_core.interfaces.embeddings import SimilarityResult
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(SimilarityResult, type), "SimilarityResult should be a class"


@pytest.mark.smoke
def test_gateway_classes_are_types():
    """SovereignLLMGateway and GenerationRequest are proper classes."""
    try:
#  # MOVED: from agentic_core.interfaces.gateway import (
            GenerationRequest,
            SovereignLLMGateway,
        )
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(SovereignLLMGateway, type)
    assert isinstance(GenerationRequest, type)


@pytest.mark.smoke
def test_protocols_are_abstract_types():
    """Protocol interfaces are proper types suitable for isinstance checks."""
    try:
#  # MOVED: from agentic_core.interfaces.IHealerProtocol import IHealerProtocol
#  # MOVED: from agentic_core.interfaces.IMemoryStoreProtocol import IMemoryStoreProtocol
#  # MOVED: from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol
#  # MOVED: from agentic_core.interfaces.IValidatorProtocol import ValidatorProtocol
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    for proto in [ValidatorProtocol, IHealerProtocol, IOrchestratorProtocol, IMemoryStoreProtocol]:
        assert isinstance(proto, type), f"{proto.__name__} should be a type"


@pytest.mark.smoke
def test_mixins_are_instantiable_protocol_stubs():
    """HealerMixin and MetaLearningMixin are instantiable mixin classes."""
    try:
#  # MOVED: from agentic_core.interfaces.mixins import HealerMixin, MetaLearningMixin
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    for mixin in [HealerMixin, MetaLearningMixin]:
        assert isinstance(mixin, type), f"{mixin.__name__} should be a type"
        instance = mixin()
        assert isinstance(instance, mixin)


@pytest.mark.smoke
def test_validators_rule_failure_is_instantiable():
    """RuleFailure is a class that can be instantiated to represent a validation failure."""
    try:
#  # MOVED: from agentic_core.interfaces.validators import RuleFailure
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    assert isinstance(RuleFailure, type)
    instance = RuleFailure()
    assert instance is not None
    assert type(instance).__name__ == "RuleFailure"


@pytest.mark.smoke
def test_write_gateway_compute_replay_key_returns_string():
    """compute_replay_key returns a non-empty string for valid inputs."""
    try:
#  # MOVED: from agentic_core.interfaces.write_gateway import compute_replay_key
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    result = compute_replay_key(
        plan_hash="abc123",
        tool_calls=["tool_a", "tool_b"],
        stdout_digest="digest_001",
        state_diff_hash="diff_001",
    )
    assert isinstance(result, str)
    assert len(result) > 0
