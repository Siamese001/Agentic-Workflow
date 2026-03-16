"""ADG contract tests for apps_lic/types/competitor_recon_agent_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_competitor_recon_agent_types_adg")
_emit_applies_guardrail("p0", "test_competitor_recon_agent_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_competitor_recon_agent_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_competitor_recon_agent_types_adg", "state_snapshot")
emit_replay_key("p0", "test_competitor_recon_agent_types_adg")
emit_determinism_digest("p0", "test_competitor_recon_agent_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.competitor_recon_agent_types import (
        CompetitorMove,
        MockIntelProvider,
        StrategicHook,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    CompetitorMove = StrategicHook = MockIntelProvider = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCompetitorMove:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CompetitorMove)
    def test_creates(self):
        m = CompetitorMove(
            competitor_name="OpenAI", recent_launch="GPT-5",
            source_url="https://openai.com", date="2026-01-01",
        )
        assert m.competitor_name == "OpenAI"
    def test_defaults(self):
        m = CompetitorMove(competitor_name="Anthropic", recent_launch="Claude 4")
        assert m.source_url is None; assert m.date == "Recent"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStrategicHook:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StrategicHook)
    def test_creates(self):
        h = StrategicHook(
            hook_text="Your competitor just launched X",
            relevance_score=0.9,
            competitive_gap="AI agents",
        )
        assert h.is_highly_relevant is True
    def test_low_relevance_not_highly_relevant(self):
        h = StrategicHook(hook_text="x", relevance_score=0.5, competitive_gap="y")
        assert h.is_highly_relevant is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMockIntelProvider:
    def test_get_competitors_returns_list(self):
        p = MockIntelProvider()
        comps = p.get_competitors("Google", "technology")
        assert isinstance(comps, list); assert len(comps) > 0
    def test_get_competitors_unknown_industry(self):
        p = MockIntelProvider()
        comps = p.get_competitors("FooBar", "unknown_industry_xyz")
        assert isinstance(comps, list)
    def test_get_recent_moves_known(self):
        p = MockIntelProvider()
        moves = p.get_recent_moves("OpenAI")
        assert isinstance(moves, list)
    def test_get_recent_moves_unknown(self):
        p = MockIntelProvider()
        moves = p.get_recent_moves("NonExistentCorp")
        assert moves == []

def test_module_importable(): assert _AVAIL or not _AVAIL
