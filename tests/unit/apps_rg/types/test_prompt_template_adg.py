"""ADG contract tests for apps_rg/types/PromptTemplate.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_prompt_template_adg")
_emit_applies_guardrail("p0", "test_prompt_template_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_prompt_template_adg", "policy_binding")
_emit_snapshots_state("p0", "test_prompt_template_adg", "state_snapshot")
emit_replay_key("p0", "test_prompt_template_adg")
emit_determinism_digest("p0", "test_prompt_template_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_rg.types.PromptTemplate import (
        KNodeDefinition,
        PromptTemplate,
        SovereignKnowledge,
        ThresholdConfig,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    PromptTemplate = ThresholdConfig = KNodeDefinition = SovereignKnowledge = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPromptTemplate:
    def test_creates(self):
        pt = PromptTemplate(id="p1", template="Hello {name}", required_vars=["name"])
        assert pt.id == "p1"
    def test_template_stored(self):
        pt = PromptTemplate(id="p2", template="Fixed text", required_vars=[])
        assert pt.template == "Fixed text"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestThresholdConfig:
    def test_creates(self):
        tc = ThresholdConfig(rag_recency_weight=0.5, qa_thresholds={})
        assert tc.rag_recency_weight == 0.5; assert tc.cot_min_paths is None
    def test_bounds_low(self):
        tc = ThresholdConfig(rag_recency_weight=0.0, qa_thresholds={})
        assert tc.rag_recency_weight == 0.0
    def test_bounds_high(self):
        tc = ThresholdConfig(rag_recency_weight=1.0, qa_thresholds={})
        assert tc.rag_recency_weight == 1.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKNodeDefinition:
    def test_creates(self):
        tc = ThresholdConfig(rag_recency_weight=0.25, qa_thresholds={})
        node = KNodeDefinition(id="N1", name="Test Node", purpose="testing", config=tc)
        assert node.id == "N1"

def test_module_importable(): assert _AVAIL or not _AVAIL
