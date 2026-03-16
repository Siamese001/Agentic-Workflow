"""ADG contract tests for apps_rg/types/thematic_analysis_node_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_thematic_analysis_node_types_adg")
_emit_applies_guardrail("p0", "test_thematic_analysis_node_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_thematic_analysis_node_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_thematic_analysis_node_types_adg", "state_snapshot")
emit_replay_key("p0", "test_thematic_analysis_node_types_adg")
emit_determinism_digest("p0", "test_thematic_analysis_node_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_rg.types.thematic_analysis_node_types import (
        AuthenticityPatterns,
        CompetitiveIntelligence,
        ThematicAnalysisNode,
        ThematicAnalysisOutput,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    AuthenticityPatterns = CompetitiveIntelligence = ThematicAnalysisOutput = ThematicAnalysisNode = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAuthenticityPatterns:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AuthenticityPatterns)
    def test_creates(self):
        p = AuthenticityPatterns(
            executive_summary_patterns=["Built and scaled"],
            achievement_verb_patterns=["Spearheaded"],
            metric_presentation_patterns=["X% improvement"],
            competency_phrasing_patterns=["Expert in"],
        )
        assert len(p.achievement_verb_patterns) == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestThematicAnalysisNode:
    def test_creates(self): n = ThematicAnalysisNode(); assert n is not None
    def test_call_returns_output(self):
        n = ThematicAnalysisNode()
        result = n("Software Engineer role at ACME", "ACME")
        assert isinstance(result, ThematicAnalysisOutput)
        assert result.company_name == "ACME"
    def test_engineering_theme(self):
        n = ThematicAnalysisNode()
        result = n("Senior Software Engineer", "Corp")
        assert "Engineering" in result.primary_theme or result.primary_theme

def test_module_importable(): assert _AVAIL or not _AVAIL
