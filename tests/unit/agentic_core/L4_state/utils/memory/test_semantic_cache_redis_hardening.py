"""Test SemanticCacheRedisHardening functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSemanticCacheRedisHardening:
    """Test SemanticCacheRedisHardening functionality."""

    def test_semantic_cache_redis_hardening_imports(self):
        """Test semantic_cache_redis_hardening module imports."""
        from agentic_core import semantic_cache_redis_hardening

        assert semantic_cache_redis_hardening is not None

    def test_semantic_cache_redis_hardening_class(self):
        """Test SemanticCacheRedisHardening class exists."""
        from agentic_core import SemanticCacheRedisHardening

        assert SemanticCacheRedisHardening is not None

    def test_semantic_cache_redis_hardening_callable(self):
        """Test semantic_cache_redis_hardening functions are callable."""
        from agentic_core import validate_semantic_cache_redis_hardening

        assert callable(validate_semantic_cache_redis_hardening)
