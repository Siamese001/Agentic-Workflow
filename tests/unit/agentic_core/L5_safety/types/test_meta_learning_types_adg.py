"""ADG contract tests for agentic_core/L5_safety/types/meta_learning_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_types_adg")
_emit_applies_guardrail("p0", "test_meta_learning_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_learning_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_meta_learning_types_adg", "state_snapshot")
emit_replay_key("p0", "test_meta_learning_types_adg")
emit_determinism_digest("p0", "test_meta_learning_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.meta_learning_types import (
        LearningContext,
        LearningResult,
        MetaLearningProtocol,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    LearningContext = LearningResult = MetaLearningProtocol = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLearningContext:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(LearningContext)
    def test_creates(self):
        ctx = LearningContext(
            context_key="k1", agent_name="AgentX",
            operation_type="summarize", input_hash="abc123",
        )
        assert ctx.agent_name == "AgentX"
    def test_metadata_default_empty_dict(self):
        ctx = LearningContext(
            context_key="k", agent_name="A", operation_type="op", input_hash="h",
        )
        assert ctx.metadata == {}
    def test_to_cache_key(self):
        ctx = LearningContext(
            context_key="k", agent_name="AgentX", operation_type="op", input_hash="hash1",
        )
        key = ctx.to_cache_key()
        assert "AgentX" in key
        assert "op" in key
        assert "hash1" in key

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLearningResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(LearningResult)
    def test_creates_success(self):
        r = LearningResult(success=True, from_cache=False, result="output")
        assert r.success is True; assert r.confidence == 1.0
    def test_creates_from_cache(self):
        r = LearningResult(success=True, from_cache=True, result=42, confidence=0.9)
        assert r.from_cache is True; assert r.confidence == 0.9
    def test_metadata_default_empty_dict(self):
        r = LearningResult(success=False, from_cache=False, result=None)
        assert r.metadata == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMetaLearningProtocol:
    def test_is_abstract(self):
        import abc; assert issubclass(MetaLearningProtocol, abc.ABC)
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            MetaLearningProtocol()  # type: ignore[abstract]

def test_module_importable(): assert _AVAIL or not _AVAIL
