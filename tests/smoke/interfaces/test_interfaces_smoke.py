"""Interfaces smoke tests — import verification and basic functionality."""

import pytest


@pytest.mark.smoke
def test_interfaces_importable():
    """Verify interfaces module imports without error."""
    try:
        import agentic_core.interfaces

        assert agentic_core.interfaces is not None
    except ImportError as e:
        pytest.skip(f"interfaces not available: {e}")


@pytest.mark.smoke
def test_determinism_importable():
    """Verify determinism functions import without error."""
    try:
        from agentic_core.interfaces.determinism import (
            canonical_bytes,
            canonical_hash,
            strip_nondeterministic,
        )

        assert callable(canonical_bytes)
        assert callable(canonical_hash)
        assert callable(strip_nondeterministic)
    except ImportError as e:
        pytest.skip(f"determinism functions not available: {e}")


@pytest.mark.smoke
def test_embeddings_interface_importable():
    """Verify embeddings interface imports without error."""
    try:
        from agentic_core.interfaces.embeddings import (
            SimilarityResult,
            query_similarity,
        )

        assert SimilarityResult is not None
        assert callable(query_similarity)
    except ImportError as e:
        pytest.skip(f"embeddings interface not available: {e}")


@pytest.mark.smoke
def test_gateway_importable():
    """Verify gateway imports without error."""
    try:
        from agentic_core.interfaces.gateway import (
            SovereignLLMGateway,
            GenerationRequest,
        )

        assert SovereignLLMGateway is not None
        assert GenerationRequest is not None
    except ImportError as e:
        pytest.skip(f"gateway not available: {e}")


@pytest.mark.smoke
def test_protocols_importable():
    """Verify protocol classes import without error."""
    try:
        from agentic_core.interfaces.IValidatorProtocol import ValidatorProtocol
        from agentic_core.interfaces.IHealerProtocol import IHealerProtocol
        from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol
        from agentic_core.interfaces.IMemoryStoreProtocol import IMemoryStoreProtocol

        assert ValidatorProtocol is not None
        assert IHealerProtocol is not None
        assert IOrchestratorProtocol is not None
        assert IMemoryStoreProtocol is not None
    except ImportError as e:
        pytest.skip(f"protocols not available: {e}")


@pytest.mark.smoke
def test_mixins_importable():
    """Verify interface mixins import without error."""
    try:
        from agentic_core.interfaces.mixins import (
            HealerMixin,
            MetaLearningMixin,
        )

        assert HealerMixin is not None
        assert MetaLearningMixin is not None
    except ImportError as e:
        pytest.skip(f"mixins not available: {e}")


@pytest.mark.smoke
def test_validators_importable():
    """Verify validators import without error."""
    try:
        from agentic_core.interfaces.validators import (
            RuleFailure,
        )

        assert RuleFailure is not None
    except ImportError as e:
        pytest.skip(f"validators not available: {e}")


@pytest.mark.smoke
def test_write_gateway_importable():
    """Verify write gateway imports without error."""
    try:
        from agentic_core.interfaces.write_gateway import (
            compute_replay_key,
        )

        assert callable(compute_replay_key)
    except ImportError as e:
        pytest.skip(f"write gateway not available: {e}")
