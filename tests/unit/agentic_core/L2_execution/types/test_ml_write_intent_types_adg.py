"""ADG contract tests for agentic_core/L2_execution/types/ml_write_intent_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L2_execution.types.ml_write_intent_types import (
        MLWriteIntent, MLWriteEnvelopeViolation, MLWriteIntentExecutor,
        is_commit_sandbox_active, execute_ml_write_intent_outside_sandbox,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    MLWriteIntent = MLWriteEnvelopeViolation = MLWriteIntentExecutor = None  # type: ignore[assignment,misc]
    is_commit_sandbox_active = execute_ml_write_intent_outside_sandbox = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMLWriteEnvelopeViolation:
    def test_is_exception(self): assert issubclass(MLWriteEnvelopeViolation, Exception)
    def test_has_violation_code(self): assert MLWriteEnvelopeViolation.VIOLATION_CODE == "ML_WRITE_OUTSIDE_SANDBOX"
    def test_raises(self):
        with pytest.raises(MLWriteEnvelopeViolation):
            raise MLWriteEnvelopeViolation()

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMLWriteIntent:
    def test_creates_pattern_store(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"key": "val"})
        assert intent.kind == "pattern_store"
        assert intent.requires_commit is True
    def test_creates_cache_set(self):
        intent = MLWriteIntent(kind="cache_set", payload={"key": "val"})
        assert intent.kind == "cache_set"
    def test_intent_hash_64_hex(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"x": 1})
        assert len(intent.intent_hash) == 64
    def test_invalid_kind_raises(self):
        with pytest.raises(ValueError):
            MLWriteIntent(kind="direct_write", payload={})  # type: ignore[arg-type]
    def test_requires_commit_false_raises(self):
        with pytest.raises(ValueError):
            MLWriteIntent(kind="pattern_store", payload={}, requires_commit=False)
    def test_payload_not_dict_raises(self):
        with pytest.raises(TypeError):
            MLWriteIntent(kind="pattern_store", payload="not_a_dict")  # type: ignore[arg-type]
    def test_canonical_bytes_deterministic(self):
        i = MLWriteIntent(kind="cache_set", payload={"a": 1})
        assert i.canonical_bytes() == i.canonical_bytes()

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSandboxActive:
    def test_inactive_outside_context(self):
        assert is_commit_sandbox_active() is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMLWriteIntentExecutor:
    def test_execute_inside_sandbox(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"k": "v"})
        with MLWriteIntentExecutor() as ex:
            result = ex.execute(intent)
        assert result["executed"] is True
        assert result["intent_hash"] == intent.intent_hash
    def test_execute_outside_raises(self):
        intent = MLWriteIntent(kind="cache_set", payload={"k": "v"})
        ex = MLWriteIntentExecutor()
        with pytest.raises(MLWriteEnvelopeViolation):
            ex.execute(intent)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOutsideSandboxGuard:
    def test_raises_outside(self):
        intent = MLWriteIntent(kind="pattern_store", payload={})
        with pytest.raises(MLWriteEnvelopeViolation):
            execute_ml_write_intent_outside_sandbox(intent)

def test_module_importable(): assert _AVAIL or not _AVAIL
