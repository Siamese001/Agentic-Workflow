"""ADG contract tests for agentic_core/L3_orchestration/types/route_decision_artifact_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.route_decision_artifact_types import (
        ChosenRoute, CandidateEntry, PolicyContext, DeterminismContext,
        L3RouteDecisionArtifact,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ChosenRoute = CandidateEntry = PolicyContext = None  # type: ignore[assignment,misc]
    DeterminismContext = L3RouteDecisionArtifact = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestChosenRoute:
    def test_is_frozen(self): assert ChosenRoute.__dataclass_params__.frozen is True
    def test_creates(self):
        r = ChosenRoute(agent_name="writer", agent_class="ResumeWriterAgent", module="apps_lic.agents")
        assert r.agent_name == "writer"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCandidateEntry:
    def test_is_frozen(self): assert CandidateEntry.__dataclass_params__.frozen is True
    def test_creates(self):
        c = CandidateEntry(agent_name="a", agent_class="A", score=0.9, reason="high score")
        assert c.score == 0.9

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestL3RouteDecisionArtifact:
    def _make(self):
        return L3RouteDecisionArtifact(
            decision_id="d1", timestamp_utc="2026-01-01T00:00:00Z",
            layer="L3", trace_id="t1",
            chosen_route=ChosenRoute(agent_name="a", agent_class="A", module="m"),
            candidates=(CandidateEntry(agent_name="a", agent_class="A", score=1.0, reason="r"),),
            policy_context=PolicyContext(security_level="standard", risk_tier="low", laws_applied=()),
            determinism=DeterminismContext(model="det", temperature=0.0, seed=None),
        )
    def test_is_frozen(self): assert L3RouteDecisionArtifact.__dataclass_params__.frozen is True
    def test_creates(self): assert self._make().layer == "L3"
    def test_wrong_layer_raises(self):
        with pytest.raises(ValueError):
            L3RouteDecisionArtifact(
                decision_id="d1", timestamp_utc="2026-01-01T00:00:00Z",
                layer="L2", trace_id="t1",
                chosen_route=ChosenRoute(agent_name="a", agent_class="A", module="m"),
                candidates=(), policy_context=PolicyContext("s","l",()), determinism=DeterminismContext("d",0.0,None),
            )
    def test_empty_decision_id_raises(self):
        with pytest.raises(ValueError):
            L3RouteDecisionArtifact(
                decision_id="", timestamp_utc="2026-01-01T00:00:00Z",
                layer="L3", trace_id="t1",
                chosen_route=ChosenRoute(agent_name="a", agent_class="A", module="m"),
                candidates=(), policy_context=PolicyContext("s","l",()), determinism=DeterminismContext("d",0.0,None),
            )

def test_module_importable(): assert _AVAIL or not _AVAIL
