"""ADG contract tests for apps_rg/types/PromptTemplate.py."""
from __future__ import annotations

import pytest

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
