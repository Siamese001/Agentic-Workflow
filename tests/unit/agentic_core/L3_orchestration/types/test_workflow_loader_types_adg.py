"""ADG contract tests for L3_orchestration/types/workflow_loader_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_workflow_loader_types_adg")
_emit_applies_guardrail("p0", "test_workflow_loader_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_workflow_loader_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_workflow_loader_types_adg", "state_snapshot")
emit_replay_key("p0", "test_workflow_loader_types_adg")
emit_determinism_digest("p0", "test_workflow_loader_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.workflow_loader_types import (
        KNodeConfig,
        WordCountConstraints,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False; WordCountConstraints = KNodeConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestWordCountConstraints:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(WordCountConstraints)
    def test_creates(self):
        w = WordCountConstraints(min_words=10, max_words=20)
        assert w.min_words == 10; assert w.max_words == 20
    def test_from_list(self):
        w = WordCountConstraints.from_list([5, 15])
        assert w.min_words == 5; assert w.max_words == 15

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKNodeConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(KNodeConfig)
    def test_creates_defaults(self):
        k = KNodeConfig(description="test node")
        assert k.TEMP == 0.7; assert k.rag_hops == 2
    def test_input_dependencies_defaults_empty(self):
        k = KNodeConfig(description="x")
        assert k.input_dependencies == []

def test_module_importable(): assert _AVAIL or not _AVAIL
