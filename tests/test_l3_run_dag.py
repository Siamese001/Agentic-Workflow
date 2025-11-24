from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List
from unittest.mock import patch

import pytest

from l3 import DAGResult, run_dag
from core.models.models import WorkflowPlanBundle


@dataclass
class _FakeStrategyBranch:
    id: str
    description: str = "desc"
    text: str = "txt"


@dataclass
class _FakeStrategy:
    branches: List[_FakeStrategyBranch] = field(default_factory=list)
    chosen_branch_id: str | None = None


@dataclass
class _FakeRagEvidenceItem:
    text: str
    score: float
    source: str | None = None


@dataclass
class _FakeRag:
    evidence: List[_FakeRagEvidenceItem] = field(default_factory=list)


@dataclass
class _FakeDraftSection:
    title: str
    text: str


@dataclass
class _FakeDrafting:
    sections: List[_FakeDraftSection] = field(default_factory=list)


@dataclass
class _FakeQaFinding:
    id: str
    severity: str
    message: str


@dataclass
class _FakeQa:
    findings: List[_FakeQaFinding] = field(default_factory=list)


@dataclass
class _FakeSafetyFinding:
    check_id: str
    category: str
    severity: str
    message: str


@dataclass
class _FakeSafety:
    findings: List[_FakeSafetyFinding] = field(default_factory=list)


@dataclass
class _FakeL2Results:
    """Minimal stand-in for L2ResultBundle for testing run_dag.

    Only the attributes actually read by run_dag are modelled here.
    """

    strategy: Any
    rag: Any
    drafting: Any
    qa: Any
    safety: Any


def _make_l2_result() -> _FakeL2Results:
    strategy = _FakeStrategy(
        branches=[_FakeStrategyBranch(id="b1", description="strategy desc")],
        chosen_branch_id="b1",
    )
    rag = _FakeRag(
        evidence=[_FakeRagEvidenceItem(text="doc", score=0.9, source="src")],
    )
    drafting = _FakeDrafting(
        sections=[_FakeDraftSection(title="t", text="body")],
    )
    qa = _FakeQa(
        findings=[_FakeQaFinding(id="f1", severity="low", message="m")],
    )
    safety = _FakeSafety(
        findings=[_FakeSafetyFinding(check_id="s1", category="cat", severity="low", message="ok")],
    )
    return _FakeL2Results(
        strategy=strategy,
        rag=rag,
        drafting=drafting,
        qa=qa,
        safety=safety,
    )


@dataclass
class _FakeCtx:
    """Lightweight stand-in for ExecutionContext for testing run_dag.

    The real ExecutionContext is a Pydantic model with many required fields.
    For these tests we only need an object to thread through to orchestrate_execution,
    which is fully patched out, so a simple dataclass is sufficient.
    """

    config: dict = field(default_factory=dict)
    
    def span_context(self):
        """Return a fake span context for observability."""
        return {}


@pytest.fixture
def ctx() -> Any:
    return _FakeCtx()


@pytest.fixture
def plans() -> Any:
    # Minimal stub; run_dag never inspects the plan when orchestrate_execution
    # is patched, so a simple object is sufficient.
    @dataclass
    class _FakePlans:
        pass

    return _FakePlans()


@patch("l3.collect_error_events")
@patch("l3.aggregate_correction_signals")
@patch("l3.evaluate_all_surfaces")
@patch("l3.orchestrate_execution")
def test_run_dag_builds_expected_final_state_patch(
    mock_orchestrate,
    mock_evaluate,
    mock_aggregate,
    mock_collect,
    ctx: Any,
    plans: WorkflowPlanBundle,
) -> None:
    """run_dag should produce a deterministic final_state_patch shape from L2 outputs."""

    mock_orchestrate.return_value = _make_l2_result()

    mock_evaluate.return_value = [
        type("Sig", (), {"surface": "l2.qa", "severity": "high", "reason": "r", "recommended_action": "fix"})()
    ]
    mock_aggregate.return_value = type(
        "Agg",
        (),
        {"surface": "l2.qa", "severity": "high", "reason": "r", "recommended_action": "fix", "needs_correction": True},
    )()

    mock_collect.return_value = [
        {"message": "err", "code": "E", "severity": "error", "properties": {"k": "v"}},
    ]

    result = run_dag(ctx=ctx, plans=plans)
    assert isinstance(result, DAGResult)

    patch = result.final_state_patch
    assert isinstance(patch, dict)

    # Required top-level keys
    for key in [
        "strategy_text",
        "rag_evidence",
        "drafted_sections",
        "qa_findings",
        "safety_findings",
        "correction_signals",
        "ais_error_events",
        "safety_passed",
    ]:
        assert key in patch

    assert patch["strategy_text"] == "strategy desc"
    assert patch["rag_evidence"] == [
        {"text": "doc", "score": 0.9, "source": "src"},
    ]
    assert patch["drafted_sections"] == [
        {"title": "t", "text": "body"},
    ]
    assert patch["qa_findings"] == [
        {"id": "f1", "severity": "low", "message": "m"},
    ]
    assert patch["safety_findings"] == [
        {"id": "s1", "category": "cat", "severity": "low", "message": "ok"},
    ]

    # Correction signals should include per-surface, aggregate, and AIS-derived entries.
    assert isinstance(patch["correction_signals"], list)
    # At least one surface-level and one aggregate self-correction signal
    assert any(s.get("surface") == "l2.qa" for s in patch["correction_signals"])
    assert any(s.get("aggregate") is True for s in patch["correction_signals"])
    # And at least one AIS-derived signal (we tagged by the presence of error_code/message).
    assert any(s.get("reason") == "err" or s.get("message") == "err" for s in patch["correction_signals"])

    assert isinstance(patch["ais_error_events"], list)
    assert patch["ais_error_events"][0]["code"] == "E"
    assert "safety_passed" in patch
    assert isinstance(patch["safety_passed"], bool)

    # DAGResult.corrected should reflect that signals (self-correction or AIS) exist.
    assert result.corrected is True


@patch("l3.collect_error_events", side_effect=Exception("boom"))
@patch("l3.evaluate_all_surfaces", side_effect=Exception("boom"))
@patch("l3.orchestrate_execution")
def test_run_dag_tolerates_correction_and_ais_failures(
    mock_orchestrate,
    _mock_eval,
    _mock_collect,
    ctx: Any,
    plans: Any,
) -> None:
    """Failures in correction evaluation or AIS collection must not break run_dag."""

    mock_orchestrate.return_value = _make_l2_result()

    result = run_dag(ctx=ctx, plans=plans)

    patch = result.final_state_patch
    assert isinstance(patch, dict)
    # Even on failure paths, keys should be present with safe fallbacks.
    assert "correction_signals" in patch
    assert "ais_error_events" in patch
    assert "safety_passed" in patch
    assert isinstance(patch["safety_passed"], bool)
    # With both correction evaluation and AIS collection failing, no signals
    # should be recorded and the corrected flag should remain False.
    assert result.corrected is False


@patch("l3.orchestrate_execution")
def test_run_dag_handles_missing_strategy_branches(
    mock_orchestrate,
    ctx: Any,
    plans: Any,
) -> None:
    """If strategy branches are missing, strategy_text should fall back to 'error' or empty string without crashing."""

    # Strategy without branches
    @dataclass
    class _Strategy:
        branches: List[Any] = field(default_factory=list)
        chosen_branch_id: str | None = None

    fake = _make_l2_result()
    fake.strategy = _Strategy()
    mock_orchestrate.return_value = fake

    result = run_dag(ctx=ctx, plans=plans)
    patch = result.final_state_patch
    assert "strategy_text" in patch
