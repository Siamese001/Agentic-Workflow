"""apps-test-model: APP CONTRACT.

Focused proof for S2 Apps Research grounded-retrieval recovery.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_research.engines.company_brief_engine import (
    CompanyBriefEngine,
    CompanyBriefUnavailableError,
)
from apps_research.engines.query_decomposer import QueryPlan
from apps_research.integrations.search_retrieval import (
    RetrievedDoc,
    RetryableRetrievalTransportError,
    retrieve,
)
from apps_rg.integrations.apps_research_bridge import AppsResearchBridge


def _plan() -> QueryPlan:
    return QueryPlan(
        family="company_basics",
        query="Unify Consulting company overview founding history core business",
        min_sources=2,
    )


def _doc(*, snippet: str = "Grounded consulting evidence.") -> RetrievedDoc:
    return RetrievedDoc(
        url="https://www.unifyconsulting.com/about",
        title="Unify Consulting About",
        snippet=snippet,
        score=0.95,
        engines=("bing",),
    )


def _patch_single_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps_research.engines.query_decomposer.decompose_coverage_families",
        lambda *_args, **_kwargs: [_plan()],
    )


def test_managed_bridge_binds_approved_searxng_endpoint_and_receipt_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runs_root = tmp_path / "e2e" / "apps_research" / "runs"
    runs_root.mkdir(parents=True)
    captured: dict[str, object] = {}
    sentinel = object()

    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    monkeypatch.setattr(
        "apps_research.integrations.searxng_readiness.runtime_base_url",
        lambda: "http://localhost:8080",
    )

    def run_research(request, *, runner):
        captured["request"] = request
        captured["runner"] = runner
        return sentinel

    monkeypatch.setattr(
        "apps_research.integrations.spine_handoff.run_research_via_spine",
        run_research,
    )

    result = AppsResearchBridge(artifact_runs_root=runs_root)._invoke_apps_research(
        company_name="Unify Consulting",
        job_title="SVP Technical Pre-Sales",
        capability_ref="apps_research.v1",
        request_id="request-1",
        run_id="run-1",
        trace_id="trace-1",
    )

    request = captured["request"]
    assert result is sentinel
    assert os.environ["SEARXNG_BASE_URL"] == "http://localhost:8080"
    assert request.topic == "Unify Consulting"
    assert request.jd_context["_retrieval_receipt_path"] == str(
        (runs_root.parent / "retrieval_receipt.json").resolve()
    )
    assert request.jd_context["company_name"] == "Unify Consulting"
    assert request.jd_context["job_title"] == "SVP Technical Pre-Sales"
    assert request.jd_context["run_id"] == "run-1"
    assert request.jd_context["trace_root"] == "trace-1"
    assert request.jd_context["tenant_id"] == "default"
    assert request.jd_context["output_format"] == "apps_rg_targeting_brief_v1"
    assert request.jd_context["synthesis_template"] == (
        "apps_rg_targeting_brief_synthesis_v1"
    )
    assert request.jd_context["content"] == ""
    assert request.jd_context["jd_text"] == ""
    assert request.jd_context["jd_ref"] == ""
    assert request.jd_context["jd_context"] == {"role": "SVP Technical Pre-Sales"}


def test_managed_bridge_preserves_nonblank_operator_endpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runs_root = tmp_path / "e2e" / "apps_research" / "runs"
    runs_root.mkdir(parents=True)
    monkeypatch.setenv("SEARXNG_BASE_URL", "https://search.example.test")
    monkeypatch.setattr(
        "apps_research.integrations.searxng_readiness.runtime_base_url",
        lambda: pytest.fail("configured endpoint must not be replaced"),
    )
    monkeypatch.setattr(
        "apps_research.integrations.spine_handoff.run_research_via_spine",
        lambda _request, *, runner: runner,
    )

    AppsResearchBridge(artifact_runs_root=runs_root)._invoke_apps_research(
        company_name="Unify Consulting",
        job_title="SVP Technical Pre-Sales",
        capability_ref="apps_research.v1",
        request_id="request-1",
        run_id="run-1",
        trace_id="trace-1",
    )

    assert os.environ["SEARXNG_BASE_URL"] == "https://search.example.test"


def test_retrieval_receipt_records_grounded_family_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_single_plan(monkeypatch)
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")
    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        lambda *_args, **_kwargs: [_doc()],
    )
    monkeypatch.setattr(
        "apps_research.integrations.reranker_adapter.rerank",
        lambda _query, docs, *, cutoff: list(docs)[:cutoff],
    )
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    findings = CompanyBriefEngine()._run_research_v2(
        topic="Unify Consulting",
        depth_profile="COMPANY_BRIEF_STANDARD",
        jd_context={},
        retrieval_receipt_path=receipt_path,
    )

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    row = receipt["families"][0]
    assert findings["company_basics"]
    assert receipt["summary"]["status"] == "PASS"
    assert receipt["summary"]["grounded_family_count"] == 1
    assert receipt["configuration"]["provider"] == "searxng"
    assert receipt["configuration"]["base_url_origin"] == "http://localhost:8080"
    assert receipt["configuration_digest"].startswith("sha256:")
    assert row["query"] == _plan().query
    assert row["retrieval_attempt_status"] == "PASS"
    assert row["documents_before_rerank"] == 1
    assert row["documents_after_rerank"] == 1
    assert row["snippets_rejected"] == []
    assert row["grounded_character_count"] > 0
    assert row["accepted_documents"] == [
        {
            "engines": ["bing"],
            "score": 0.95,
            "snippet": "Grounded consulting evidence.",
            "title": "Unify Consulting About",
            "url": "https://www.unifyconsulting.com/about",
        }
    ]


def test_configuration_failure_is_explained_and_not_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_single_plan(monkeypatch)
    monkeypatch.delenv("SEARXNG_BASE_URL", raising=False)
    calls = 0

    def fail_configuration(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("SEARXNG_BASE_URL is not set")

    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        fail_configuration,
    )
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    with pytest.raises(CompanyBriefUnavailableError, match="no grounded findings"):
        CompanyBriefEngine()._run_research_v2(
            topic="Unify Consulting",
            depth_profile="COMPANY_BRIEF_STANDARD",
            jd_context={},
            retrieval_receipt_path=receipt_path,
        )

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    row = receipt["families"][0]
    assert calls == 1
    assert receipt["summary"]["status"] == "BLOCKED"
    assert receipt["summary"]["unexplained_failure_count"] == 0
    assert row["retrieval_attempt_status"] == "FAILED"
    assert row["attempts"] == [
        {
            "attempt": 1,
            "exception_message": "SEARXNG_BASE_URL is not set",
            "exception_type": "RuntimeError",
            "status": "FAILED",
        }
    ]


def test_retryable_transport_failure_gets_exactly_one_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_single_plan(monkeypatch)
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")
    calls = 0

    def retrieve_after_retry(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RetryableRetrievalTransportError("temporary connection reset")
        return [_doc()]

    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        retrieve_after_retry,
    )
    monkeypatch.setattr(
        "apps_research.integrations.reranker_adapter.rerank",
        lambda _query, docs, *, cutoff: list(docs)[:cutoff],
    )
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    CompanyBriefEngine()._run_research_v2(
        topic="Unify Consulting",
        depth_profile="COMPANY_BRIEF_STANDARD",
        jd_context={},
        retrieval_receipt_path=receipt_path,
    )

    row = json.loads(receipt_path.read_text(encoding="utf-8"))["families"][0]
    assert calls == 2
    assert [attempt["status"] for attempt in row["attempts"]] == ["RETRY", "PASS"]


def test_empty_rerank_is_recorded_and_still_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_single_plan(monkeypatch)
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")
    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        lambda *_args, **_kwargs: [_doc()],
    )
    monkeypatch.setattr(
        "apps_research.integrations.reranker_adapter.rerank",
        lambda *_args, **_kwargs: [],
    )
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    with pytest.raises(CompanyBriefUnavailableError, match="no grounded findings"):
        CompanyBriefEngine()._run_research_v2(
            topic="Unify Consulting",
            depth_profile="COMPANY_BRIEF_STANDARD",
            jd_context={},
            retrieval_receipt_path=receipt_path,
        )

    row = json.loads(receipt_path.read_text(encoding="utf-8"))["families"][0]
    assert row["retrieval_attempt_status"] == "RERANK_EMPTY"
    assert row["documents_before_rerank"] == 1
    assert row["documents_after_rerank"] == 0
    assert row["snippets_rejected"] == [
        {
            "reason": "RERANK_DROPPED",
            "title": "Unify Consulting About",
            "url": "https://www.unifyconsulting.com/about",
        }
    ]


def test_zero_documents_is_recorded_without_retry_or_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_single_plan(monkeypatch)
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")
    calls = 0

    def retrieve_no_documents(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return []

    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        retrieve_no_documents,
    )
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    with pytest.raises(CompanyBriefUnavailableError, match="no grounded findings"):
        CompanyBriefEngine()._run_research_v2(
            topic="Unify Consulting",
            depth_profile="COMPANY_BRIEF_STANDARD",
            jd_context={},
            retrieval_receipt_path=receipt_path,
        )

    row = json.loads(receipt_path.read_text(encoding="utf-8"))["families"][0]
    assert calls == 1
    assert row["retrieval_attempt_status"] == "ZERO_DOCUMENTS"
    assert row["documents_before_rerank"] == 0
    assert row["documents_after_rerank"] == 0
    assert row["accepted_documents"] == []
    assert row["snippets_rejected"] == []


def test_transport_timeout_is_typed_as_retryable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")

    def timeout(*_args, **_kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval._load_searxng_json",
        timeout,
    )

    with pytest.raises(
        RetryableRetrievalTransportError,
        match="SearXNG search request failed: timed out",
    ):
        retrieve("Unify Consulting company overview", top_k=10)


def test_receipt_contains_every_planned_unify_family(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")
    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        lambda *_args, **_kwargs: [_doc()],
    )
    monkeypatch.setattr(
        "apps_research.integrations.reranker_adapter.rerank",
        lambda _query, docs, *, cutoff: list(docs)[:cutoff],
    )
    jd_text = Path(
        "artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_jd.txt"
    ).read_text(encoding="utf-8")
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    CompanyBriefEngine()._run_research_v2(
        topic="Unify Consulting",
        depth_profile="COMPANY_BRIEF_STANDARD",
        jd_context={
            "company_name": "Unify Consulting",
            "job_title": "SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions",
            "content": jd_text,
            "jd_text": jd_text,
        },
        retrieval_receipt_path=receipt_path,
    )

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["summary"]["planned_family_count"] == 10
    assert [row["family"] for row in receipt["families"]] == [
        "company_basics",
        "partner_ecosystem",
        "commercial_motion",
        "adoption_motion",
        "tech_stack_and_tools",
        "competitive_landscape",
        "financials_and_growth",
        "recent_news_and_signals",
        "leadership_and_org",
        "role_context",
    ]
    role_row = receipt["families"][-1]
    assert role_row["query"] == (
        "Unify Consulting "
        "SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions "
        "partnerships platform engineering sales gtm applied ai"
    )
    assert role_row["jd_boosted"] is True
    assert all(row["retrieval_attempt_status"] == "PASS" for row in receipt["families"])


def test_role_context_rejects_documents_for_other_unify_entities(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    role_plan = QueryPlan(
        family="role_context",
        query=(
            "Unify Consulting SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions "
            "partnerships platform engineering sales gtm applied ai"
        ),
        min_sources=1,
        jd_boosted=True,
    )
    monkeypatch.setattr(
        "apps_research.engines.query_decomposer.decompose_coverage_families",
        lambda *_args, **_kwargs: [role_plan],
    )
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://localhost:8080")
    monkeypatch.setattr(
        "apps_research.integrations.search_retrieval.retrieve",
        lambda *_args, **_kwargs: [
            RetrievedDoc(
                url="https://www.ui.com/",
                title="Ubiquiti - Rethinking IT",
                snippet="UniFi enterprise networking products.",
                score=0.99,
                engines=("bing",),
            ),
            RetrievedDoc(
                url="https://www.unifyconsulting.com/role",
                title="Unify Consulting role",
                snippet="Relevant role context without engine provenance.",
                score=0.97,
                engines=(),
            ),
            _doc(),
        ],
    )
    monkeypatch.setattr(
        "apps_research.integrations.reranker_adapter.rerank",
        lambda _query, docs, *, cutoff: list(docs)[:cutoff],
    )
    receipt_path = tmp_path / "apps_research" / "retrieval_receipt.json"
    (receipt_path.parent / "runs").mkdir(parents=True)

    findings = CompanyBriefEngine()._run_research_v2(
        topic="Unify Consulting",
        depth_profile="COMPANY_BRIEF_STANDARD",
        jd_context={"job_title": "SVP Technical Pre-Sales"},
        retrieval_receipt_path=receipt_path,
    )

    row = json.loads(receipt_path.read_text(encoding="utf-8"))["families"][0]
    assert findings["role_context"]
    assert row["documents_before_rerank"] == 3
    assert row["documents_identity_admissible"] == 1
    assert row["accepted_documents"] == [
        {
            "engines": ["bing"],
            "score": 0.95,
            "snippet": "Grounded consulting evidence.",
            "title": "Unify Consulting About",
            "url": "https://www.unifyconsulting.com/about",
        }
    ]
    assert row["snippets_rejected"] == [
        {
            "reason": "COMPANY_IDENTITY_MISMATCH",
            "title": "Ubiquiti - Rethinking IT",
            "url": "https://www.ui.com/",
        },
        {
            "missing_fields": ["engines"],
            "reason": "REQUIRED_EVIDENCE_FIELDS_MISSING",
            "title": "Unify Consulting role",
            "url": "https://www.unifyconsulting.com/role",
        },
    ]
