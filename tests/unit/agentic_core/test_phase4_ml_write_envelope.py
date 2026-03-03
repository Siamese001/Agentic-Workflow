"""
Phase 4 — Wave 1 Tests: ML write envelope enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.ml_write_intent import (
    MLWriteEnvelopeViolation,
    MLWriteIntent,
    MLWriteIntentExecutor,
    execute_ml_write_intent_outside_sandbox,
    is_commit_sandbox_active,
)

pytestmark = pytest.mark.unit_min_deps


class TestMLWriteIntent:
    def test_build_pattern_store_intent(self):
        intent = MLWriteIntent(
            kind="pattern_store",
            payload={"pattern_id": "p-001", "domain": "agentic_core"},
        )
        assert intent.kind == "pattern_store"
        assert intent.requires_commit is True
        assert len(intent.intent_hash) == 64

    def test_build_cache_set_intent(self):
        intent = MLWriteIntent(
            kind="cache_set",
            payload={"key": "k1", "value": "v1", "ttl": 3600},
        )
        assert intent.kind == "cache_set"
        assert len(intent.intent_hash) == 64

    def test_intent_hash_stable(self):
        payload = {"key": "k", "value": "v"}
        i1 = MLWriteIntent(kind="cache_set", payload=payload)
        i2 = MLWriteIntent(kind="cache_set", payload=payload)
        assert i1.intent_hash == i2.intent_hash

    def test_intent_hash_differs_by_kind(self):
        payload = {"key": "k"}
        i1 = MLWriteIntent(kind="cache_set", payload=payload)
        i2 = MLWriteIntent(kind="pattern_store", payload=payload)
        assert i1.intent_hash != i2.intent_hash

    def test_invalid_kind_raises(self):
        with pytest.raises(ValueError, match="kind must be one of"):
            MLWriteIntent(kind="direct_pinecone_write", payload={})  # type: ignore[arg-type]

    def test_requires_commit_false_raises(self):
        with pytest.raises(ValueError, match="requires_commit must be True"):
            MLWriteIntent(kind="cache_set", payload={}, requires_commit=False)

    def test_non_dict_payload_raises(self):
        with pytest.raises(TypeError, match="payload must be a dict"):
            MLWriteIntent(kind="cache_set", payload="raw_string")  # type: ignore[arg-type]

    def test_canonical_bytes_deterministic(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"a": 1})
        assert intent.canonical_bytes() == intent.canonical_bytes()


class TestMLWriteSandbox:
    def test_sandbox_inactive_by_default(self):
        assert is_commit_sandbox_active() is False

    def test_sandbox_active_inside_context(self):
        with MLWriteIntentExecutor():
            assert is_commit_sandbox_active() is True

    def test_sandbox_inactive_after_context(self):
        with MLWriteIntentExecutor():
            pass
        assert is_commit_sandbox_active() is False

    def test_ml_write_allowed_inside_commit_sandbox(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"pattern_id": "p-sandbox"})
        with MLWriteIntentExecutor() as executor:
            result = executor.execute(intent)
        assert result["executed"] is True
        assert result["kind"] == "pattern_store"
        assert result["intent_hash"] == intent.intent_hash

    def test_ml_write_blocked_outside_commit_sandbox(self):
        """
        Negative: executing MLWriteIntent outside the sandbox raises
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX code.
        """
        executor = MLWriteIntentExecutor()
        intent = MLWriteIntent(kind="cache_set", payload={"key": "k"})
        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            executor.execute(intent)

    def test_direct_write_outside_sandbox_raises(self):
        """
        Negative: direct ML write attempt (simulated via
        execute_ml_write_intent_outside_sandbox) raises MLWriteEnvelopeViolation.
        """
        intent = MLWriteIntent(kind="pattern_store", payload={"domain": "apps_rg"})
        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            execute_ml_write_intent_outside_sandbox(intent)

    def test_violation_error_carries_violation_code(self):
        err = MLWriteEnvelopeViolation("test")
        assert "ML_WRITE_OUTSIDE_SANDBOX" in str(err)

    def test_sandbox_restores_state_on_exception(self):
        """Sandbox must deactivate even if execute() raises."""
        try:
            with MLWriteIntentExecutor():
                assert is_commit_sandbox_active() is True
                raise RuntimeError("simulated failure")
        except RuntimeError:
            pass
        assert is_commit_sandbox_active() is False

    def test_cache_set_allowed_inside_sandbox(self):
        intent = MLWriteIntent(kind="cache_set", payload={"key": "ast-result", "ttl": 3600})
        with MLWriteIntentExecutor() as executor:
            result = executor.execute(intent)
        assert result["executed"] is True
        assert result["kind"] == "cache_set"
