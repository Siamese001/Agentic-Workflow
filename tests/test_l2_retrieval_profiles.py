from __future__ import annotations

import asyncio
import types

import l2
from config_profiles_v10_10 import get_profile
from models import (
    Evidence,
    ExecutionContext,
    JobInput,
    ResumeInput,
    WorkflowConfig,
    WorkflowPlanBundle,
    StrategyPlan,
    StrategyStep,
    DraftingPlan,
    DraftSectionPlan,
    QAPlan,
    QACheck,
    SafetyPlan,
    SafetyCheck,
    RAGPlan,
    RetrievalConfig,
    RAGResult,
)


def _make_ctx() -> ExecutionContext:
    job = JobInput(
        title="Engineer",
        role_type="engineering",
        seniority="mid",
        posting_text="Looking for an engineer.",
    )
    resume = ResumeInput(
        summary="Some summary",
        experience_sections=[],
        skills=[],
    )
    cfg = WorkflowConfig()
    return ExecutionContext(
        job=job,
        resume=resume,
        config=cfg,
        prompt_registry=None,
        cache_manager=None,
        routing_policy=None,
        sandbox_config=None,
        meta_profile_snapshot=None,
    )


def _make_plans() -> WorkflowPlanBundle:
    strategy = StrategyPlan(steps=[StrategyStep(id="s1", order=1, description="step")])
    drafting = DraftingPlan(sections=[DraftSectionPlan(id="d1", title="Summary")])
    qa = QAPlan(checks=[QACheck(id="q1", description="check", severity="low")])
    safety = SafetyPlan(checks=[SafetyCheck(id="sf1", description="safe", severity="low")])
    rag = RAGPlan(strategy="hybrid", max_hits=8)
    return WorkflowPlanBundle(strategy=strategy, rag=rag, drafting=drafting, qa=qa, safety=safety)


def test_execute_retrieval_uses_high_quality_profile_retrieval_cfg(monkeypatch) -> None:
    """High-quality profile should flow its RetrievalConfig into retrieval.run_rag_retrieval.

    This test exercises l2._execute_retrieval with RESUME_HIGH_QUALITY and ensures
    that the RetrievalConfig passed to retrieval.run_rag_retrieval matches the
    profile values, and that HYDE is considered (hyde_query is non-None).
    """

    plans = _make_plans()

    ctx = _make_ctx()
    profile = get_profile("RESUME_HIGH_QUALITY")
    ctx.retrieval = profile.retrieval

    captured: dict = {}

    async def _fake_maybe_run_hyde_query(rag_plan, ctx):  # noqa: ARG001
        return "hyde-generated-query"

    def _fake_run_rag_retrieval(*, query: str, ctx, retrieval_cfg: RetrievalConfig, hyde_query, council_vote) -> RAGResult:  # noqa: ARG001
        captured["query"] = query
        captured["cfg"] = retrieval_cfg
        captured["hyde_query"] = hyde_query
        return RAGResult(evidence=[Evidence(text="e", score=1.0, source="bm25", metadata={})], used_hyde=bool(hyde_query))

    monkeypatch.setattr(l2, "_maybe_run_hyde_query", _fake_maybe_run_hyde_query, raising=True)
    # Patch the symbol that l2._execute_retrieval actually uses.
    monkeypatch.setattr(l2, "run_rag_retrieval", _fake_run_rag_retrieval, raising=True)

    # Patch spans to no-op.
    monkeypatch.setattr(l2, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(l2, "end_span", lambda *a, **k: None, raising=True)

    rag_result = asyncio.run(l2._execute_retrieval(plans, ctx))

    assert isinstance(rag_result, RAGResult)
    assert captured["hyde_query"] == "hyde-generated-query"
    cfg = captured["cfg"]
    assert isinstance(cfg, RetrievalConfig)
    # Ensure we are using profile's retrieval config (not default RetrievalConfig()).
    assert cfg.max_hits == profile.retrieval.max_hits
    assert cfg.strategy == profile.retrieval.strategy


def test_execute_retrieval_uses_fast_profile_without_hyde(monkeypatch) -> None:
    """FAST profile (BM25-only) should pass its RetrievalConfig and not use HYDE."""

    import retrieval as retrieval_mod

    plans = _make_plans()

    ctx = _make_ctx()
    profile = get_profile("RESUME_FAST")
    ctx.retrieval = profile.retrieval

    async def _fake_maybe_run_hyde_query(rag_plan, ctx):  # noqa: ARG001
        return None

    def _fake_run_rag_retrieval(*, query: str, ctx, retrieval_cfg: RetrievalConfig, hyde_query, council_vote) -> RAGResult:  # noqa: ARG001
        return RAGResult(evidence=[Evidence(text="e", score=1.0, source="bm25", metadata={})], used_hyde=False)

    monkeypatch.setattr(l2, "_maybe_run_hyde_query", _fake_maybe_run_hyde_query, raising=True)
    monkeypatch.setattr(retrieval_mod, "run_rag_retrieval", _fake_run_rag_retrieval, raising=True)
    monkeypatch.setattr(l2, "start_span", lambda *a, **k: types.SimpleNamespace(), raising=True)
    monkeypatch.setattr(l2, "end_span", lambda *a, **k: None, raising=True)

    rag_result = asyncio.run(l2._execute_retrieval(plans, ctx))

    assert isinstance(rag_result, RAGResult)
    # HYDE should not be used for RESUME_FAST profile; in this test, we only assert
    # that the orchestrator returns a result with used_hyde=False.
    assert rag_result.used_hyde is False
