"""Test policy guardrail embedder functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPolicyGuardrailEmbedder:
    """Test policy guardrail embedder functionality."""

    def test_policy_guardrail_embedder_imports(self):
        """Test policy guardrail embedder module imports."""
        from system_learning.embedding import policy_embedder
        assert policy_embedder is not None

    def test_policy_embedder_class(self):
        """Test policy embedder class exists."""
        from system_learning.embedding.policy_embedder import PolicyGuardrailEmbedder
        assert PolicyGuardrailEmbedder is not None

    def test_policy_embed_function(self):
        """Test policy embed function."""
        from system_learning.embedding.policy_embedder import embed_policy
        assert callable(embed_policy)
