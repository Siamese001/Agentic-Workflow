"""
Phase 6 — Wave 1 Tests: read_only_retrieval_scope() + RetrievalMutationViolation.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    RetrievalMutationViolation,
    assert_not_read_only,
    is_read_only_retrieval_active,
    read_only_retrieval_scope,
)

pytestmark = pytest.mark.unit_min_deps


class TestScopeActivation:
    def test_scope_inactive_by_default(self):
        assert is_read_only_retrieval_active() is False

    def test_scope_active_inside_context(self):
        with read_only_retrieval_scope():
            assert is_read_only_retrieval_active() is True

    def test_scope_inactive_after_context(self):
        with read_only_retrieval_scope():
            pass
        assert is_read_only_retrieval_active() is False

    def test_scope_restored_on_exception(self):
        with pytest.raises(RuntimeError):
            with read_only_retrieval_scope():
                raise RuntimeError("boom")
        assert is_read_only_retrieval_active() is False

    def test_nested_scope_stays_active_until_outermost_exits(self):
        with read_only_retrieval_scope():
            with read_only_retrieval_scope():
                assert is_read_only_retrieval_active() is True
            assert is_read_only_retrieval_active() is True
        assert is_read_only_retrieval_active() is False


class TestMutationBlockedInsideReadOnlyScope:
    def test_mutation_blocked_inside_read_only_scope(self):
        """
        Core Wave 1 guarantee: assert_not_read_only() raises inside scope.
        """
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("redis.setex")
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc_info.value)

    def test_mutation_blocked_includes_operation_detail(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("pinecone.upsert")
        assert "pinecone.upsert" in str(exc_info.value)

    def test_mutation_blocked_redis_setex(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("redis.setex")
        assert exc_info.value.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_mutation_blocked_pinecone_upsert(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation) as exc_info:
                assert_not_read_only("pinecone.upsert")
        assert exc_info.value.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_mutation_blocked_file_write(self):
        with read_only_retrieval_scope():
            with pytest.raises(RetrievalMutationViolation):
                assert_not_read_only("file.write")

    def test_violation_carries_code_substring(self):
        """Negative test: violation message contains code substring."""
        with read_only_retrieval_scope():
            try:
                assert_not_read_only("redis.set")
                pytest.fail("Expected RetrievalMutationViolation")
            except RetrievalMutationViolation as exc:  # guardian: allow-silent-swallower
                assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc)
                assert exc.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_violation_detail_preserved(self):
        with read_only_retrieval_scope():
            try:
                assert_not_read_only("pinecone.upsert")
            except RetrievalMutationViolation as exc:  # guardian: allow-silent-swallower
                assert exc.detail == "pinecone.upsert"


class TestMutationAllowedOutsideReadOnlyScope:
    def test_mutation_allowed_outside_read_only_scope(self):
        """
        Core Wave 1 guarantee: assert_not_read_only() is a no-op outside scope.
        """
        assert_not_read_only("redis.setex")  # must not raise

    def test_mutation_allowed_after_scope_exits(self):
        with read_only_retrieval_scope():
            pass
        assert_not_read_only("pinecone.upsert")  # must not raise

    def test_mutation_allowed_with_empty_operation(self):
        assert_not_read_only("")  # must not raise

    def test_mutation_allowed_with_no_operation(self):
        assert_not_read_only()  # must not raise


class TestRetrievalMutationViolation:
    def test_violation_is_exception(self):
        exc = RetrievalMutationViolation("test detail")
        assert isinstance(exc, Exception)

    def test_violation_code_constant(self):
        assert RetrievalMutationViolation.code == "RETRIEVAL_MUTATION_BLOCKED"

    def test_violation_detail_stored(self):
        exc = RetrievalMutationViolation("my detail")
        assert exc.detail == "my detail"

    def test_violation_empty_detail(self):
        exc = RetrievalMutationViolation()
        assert exc.detail == ""
        assert "RETRIEVAL_MUTATION_BLOCKED" in str(exc)
