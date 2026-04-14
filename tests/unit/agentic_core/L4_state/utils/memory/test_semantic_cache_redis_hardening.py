"""Test semantic cache redis hardening functionality."""

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
agentic_core = import_or_skip(
    "agentic_core",
    reason="agentic_core unavailable for test_semantic_cache_redis_hardening.py tests",
)
module_under_test = getattr(agentic_core, "semantic_cache_redis_hardening")


@pytest.mark.unit
class TestSemanticCacheRedisHardening:
    """Test semantic cache redis hardening functionality."""

    def test_module_imports(self):
        assert module_under_test is not None

    def test_module_class(self):
        exported_class = getattr(agentic_core, "SemanticCacheRedisHardening")
        assert exported_class is not None

    def test_module_callable(self):
        validator = getattr(agentic_core, "validate_semantic_cache_redis_hardening")
        assert callable(validator)
