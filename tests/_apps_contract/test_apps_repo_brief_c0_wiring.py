"""DS-2 governance tests — apps_repo_brief C0 runtime wiring.

Plan: apps-repo-brief-c0-runtime-wiring-f4a8b2
8 test cases:
1. _build_c0_fec returns a dict with expected keys when adapter succeeds
2. _build_c0_fec returns None on exception (fail-soft)
3. run_repo_brief_via_spine calls _build_c0_fec when c0_required=True (default)
4. run_repo_brief_via_spine skips C0 when c0_required=False
5. GovernedExecRun.run() accepts c0_fec kwarg without error
6. GovernedExecRun.run() returns run_record with c0_fec threaded
7. fec_producer grounded=False when no retrieval sources (backward-compat)
8. fec_producer grounded=True when c0_retrieval_sources provided
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(**kwargs: Any) -> SimpleNamespace:
    defaults = {
        "trace_id": "test-trace-001",
        "brief_type": "executive",
        "audience": "engineers",
        "emphasis_areas": ["routing", "evidence"],
        "c0_required": True,
        "depth_profile": "REPO_BRIEF_STANDARD",
        "policy_hash": "",
        "blueprint_hash": "",
        "repo_snapshot_id": "",
        "replay_key": "",
        "normalized_request_hash": "",
        "persona_schema_version": "",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Test 1: _build_c0_fec happy path
# ---------------------------------------------------------------------------

def test_build_c0_fec_returns_expected_keys() -> None:
    from apps_repo_brief.integrations.spine_handoff import _build_c0_fec

    request = _make_request()
    result = _build_c0_fec(request)

    assert result is not None
    assert result["c0_state"] == "PASS"
    assert "c0_retrieval_sources" in result
    assert "evidence_ids" in result
    assert "contradiction_flags" in result
    assert "missing_evidence_flags" in result
    assert "retrieval_surface_id" in result
    assert result["retrieval_surface_id"] == "repo_brief_docs"


# ---------------------------------------------------------------------------
# Test 2: _build_c0_fec fail-soft on exception
# ---------------------------------------------------------------------------

def test_build_c0_fec_returns_none_on_exception() -> None:
    from apps_repo_brief.integrations.spine_handoff import _build_c0_fec

    request = _make_request()
    with patch(
        "apps_repo_brief.c0.repo_brief_c0_adapter.RepoBriefC0Adapter.build_c0_request",
        side_effect=RuntimeError("C0 unavailable"),
    ):
        result = _build_c0_fec(request)

    assert result is None


# ---------------------------------------------------------------------------
# Test 3: run_repo_brief_via_spine invokes C0 when c0_required=True
# ---------------------------------------------------------------------------

def test_run_via_spine_calls_c0_when_required() -> None:
    from apps_repo_brief.integrations.spine_handoff import run_repo_brief_via_spine

    request = _make_request(c0_required=True)

    mock_runner = MagicMock()
    mock_runner.run.return_value = {"trace_id": "test-trace-001", "c0_fec": {}}

    with patch(
        "apps_repo_brief.integrations.spine_handoff._build_c0_fec",
        return_value={"c0_state": "PASS", "c0_retrieval_sources": []},
    ) as mock_c0:
        run_repo_brief_via_spine(request, runner=mock_runner)

    mock_c0.assert_called_once_with(request)
    mock_runner.run.assert_called_once()
    _, kwargs = mock_runner.run.call_args
    assert kwargs["c0_fec"] is not None
    assert kwargs["c0_fec"]["c0_state"] == "PASS"


# ---------------------------------------------------------------------------
# Test 4: run_repo_brief_via_spine skips C0 when c0_required=False
# ---------------------------------------------------------------------------

def test_run_via_spine_skips_c0_when_not_required() -> None:
    from apps_repo_brief.integrations.spine_handoff import run_repo_brief_via_spine

    request = _make_request(c0_required=False)
    mock_runner = MagicMock()
    mock_runner.run.return_value = {"trace_id": "test-trace-001", "c0_fec": None}

    with patch(
        "apps_repo_brief.integrations.spine_handoff._build_c0_fec",
    ) as mock_c0:
        run_repo_brief_via_spine(request, runner=mock_runner)

    mock_c0.assert_not_called()
    _, kwargs = mock_runner.run.call_args
    assert kwargs["c0_fec"] is None


# ---------------------------------------------------------------------------
# Test 5: GovernedExecRun.run() accepts c0_fec kwarg without error
# ---------------------------------------------------------------------------

def test_governed_exec_run_accepts_c0_fec_kwarg() -> None:
    from apps_repo_brief.integrations.governed_exec_run import GovernedExecRun

    runner = GovernedExecRun()
    request = _make_request()
    c0_fec = {"c0_state": "PASS", "c0_retrieval_sources": ["src-1"]}

    with patch("apps_shared.cert.maybe_invoke_exit_eval", return_value=None):
        result = runner.run(request, c0_fec=c0_fec)

    assert result is not None


# ---------------------------------------------------------------------------
# Test 6: GovernedExecRun.run() returns run_record with c0_fec threaded
# ---------------------------------------------------------------------------

def test_governed_exec_run_threads_c0_fec_into_run_record() -> None:
    from apps_repo_brief.integrations.governed_exec_run import GovernedExecRun

    runner = GovernedExecRun()
    request = _make_request()
    c0_fec = {"c0_state": "PASS", "c0_retrieval_sources": ["doc-abc"]}

    with patch("apps_shared.cert.maybe_invoke_exit_eval", return_value=None):
        result = runner.run(request, c0_fec=c0_fec)

    assert result["c0_fec"] == c0_fec
    assert result["trace_id"] == "test-trace-001"
    assert result["collection"] == "repo_brief_docs"


# ---------------------------------------------------------------------------
# Test 7: produce_fec grounded=False when no retrieval sources
# ---------------------------------------------------------------------------

def test_produce_fec_grounded_false_when_no_sources() -> None:
    from apps_repo_brief.cert.fec_producer import produce_fec

    result = produce_fec({})

    assert result["grounded"] is False
    assert result["evidence_sufficiency"] == "template_only"
    assert result["retrieval_sources"] == []


# ---------------------------------------------------------------------------
# Test 8: produce_fec grounded=True when c0_retrieval_sources provided
# ---------------------------------------------------------------------------

def test_produce_fec_grounded_true_with_c0_sources() -> None:
    from apps_repo_brief.cert.fec_producer import produce_fec

    ctx = {
        "c0_retrieval_sources": ["src-001", "src-002"],
        "template_ids": ["repo_brief_v1"],
    }
    result = produce_fec(ctx)

    assert result["grounded"] is True
    assert result["evidence_sufficiency"] == "grounded"
    assert "src-001" in result["retrieval_sources"]
    assert "src-002" in result["retrieval_sources"]
