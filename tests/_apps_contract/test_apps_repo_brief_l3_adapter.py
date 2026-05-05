"""DS-3 governance tests — apps_repo_brief L3 managed workflow adapter.

Plan: apps-repo-brief-l3-workflow-e2c7d9
10 test cases:
1.  expand() returns WorkflowExpansion with l3_expanded=True
2.  expand() returns stage_count=3
3.  Stage dependency order is 1→2→3 (no skips)
4.  expand() never mutates run_context
5.  HITL_REQUIRED when c0_state=FAIL
6.  HITL_REQUIRED when evidence_status=MISSING
7.  HITL_ADVISORY when contradiction_flags present (c0_state PASS)
8.  HITL_NONE when all signals clean
9.  evidence_refs injected into requires_evidence_refs stages only
10. spine_handoff calls expand() fail-soft (exception → log, continue)
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Test 1: expand() returns WorkflowExpansion with l3_expanded=True
# ---------------------------------------------------------------------------

def test_expand_returns_workflow_expansion_l3_expanded() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        RepoBriefL3WorkflowAdapter,
        WorkflowExpansion,
    )

    adapter = RepoBriefL3WorkflowAdapter()
    result = adapter.expand({})

    assert isinstance(result, WorkflowExpansion)
    assert result.l3_expanded is True


# ---------------------------------------------------------------------------
# Test 2: expand() returns stage_count=3
# ---------------------------------------------------------------------------

def test_expand_returns_stage_count_3() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        RepoBriefL3WorkflowAdapter,
    )

    result = RepoBriefL3WorkflowAdapter().expand({})
    assert result.stage_count == 3
    assert len(result.stages) == 3


# ---------------------------------------------------------------------------
# Test 3: Stage dependency order is 1→2→3
# ---------------------------------------------------------------------------

def test_stage_dependency_order_sequential() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        RepoBriefL3WorkflowAdapter,
    )

    result = RepoBriefL3WorkflowAdapter().expand({})
    sequences = [s["sequence"] for s in result.stages]
    assert sequences == [1, 2, 3]

    stage1, stage2, stage3 = result.stages
    assert stage1["depends_on"] == []
    assert stage1["stage_id"] in stage2["depends_on"]
    assert stage2["stage_id"] in stage3["depends_on"]


# ---------------------------------------------------------------------------
# Test 4: expand() never mutates run_context
# ---------------------------------------------------------------------------

def test_expand_does_not_mutate_run_context() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        RepoBriefL3WorkflowAdapter,
    )

    ctx: dict[str, Any] = {"c0_fec": {"c0_state": "PASS", "evidence_ids": ["e1"]}}
    original_ctx = dict(ctx)
    RepoBriefL3WorkflowAdapter().expand(ctx)
    assert ctx == original_ctx


# ---------------------------------------------------------------------------
# Test 5: HITL_REQUIRED when c0_state=FAIL
# ---------------------------------------------------------------------------

def test_hitl_required_when_c0_state_fail() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        HITL_REQUIRED,
        RepoBriefL3WorkflowAdapter,
    )

    ctx = {"c0_fec": {"c0_state": "FAIL", "evidence_ids": [], "contradiction_flags": []}}
    result = RepoBriefL3WorkflowAdapter().expand(ctx)
    assert result.hitl_posture == HITL_REQUIRED
    assert "c0_state_fail" in result.hitl_triggers


# ---------------------------------------------------------------------------
# Test 6: HITL_REQUIRED when evidence_status=MISSING
# ---------------------------------------------------------------------------

def test_hitl_required_when_evidence_status_missing() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        HITL_REQUIRED,
        RepoBriefL3WorkflowAdapter,
    )

    ctx = {
        "c0_fec": {
            "c0_state": "PASS",
            "evidence_status": "MISSING",
            "contradiction_flags": [],
            "evidence_ids": [],
        }
    }
    result = RepoBriefL3WorkflowAdapter().expand(ctx)
    assert result.hitl_posture == HITL_REQUIRED
    assert "evidence_status_missing" in result.hitl_triggers


# ---------------------------------------------------------------------------
# Test 7: HITL_ADVISORY when contradiction_flags present and c0_state PASS
# ---------------------------------------------------------------------------

def test_hitl_advisory_when_contradiction_flags() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        HITL_ADVISORY,
        RepoBriefL3WorkflowAdapter,
    )

    ctx = {
        "c0_fec": {
            "c0_state": "PASS",
            "evidence_status": "PASS",
            "contradiction_flags": ["conflict-a"],
            "evidence_ids": [],
        }
    }
    result = RepoBriefL3WorkflowAdapter().expand(ctx)
    assert result.hitl_posture == HITL_ADVISORY
    assert "contradiction_flags_present" in result.hitl_triggers


# ---------------------------------------------------------------------------
# Test 8: HITL_NONE when all signals clean
# ---------------------------------------------------------------------------

def test_hitl_none_when_clean() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        HITL_NONE,
        RepoBriefL3WorkflowAdapter,
    )

    ctx = {
        "c0_fec": {
            "c0_state": "PASS",
            "evidence_status": "PASS",
            "contradiction_flags": [],
            "evidence_ids": ["e1", "e2"],
        }
    }
    result = RepoBriefL3WorkflowAdapter().expand(ctx)
    assert result.hitl_posture == HITL_NONE
    assert result.hitl_triggers == []


# ---------------------------------------------------------------------------
# Test 9: evidence_refs injected into requires_evidence_refs stages only
# ---------------------------------------------------------------------------

def test_evidence_refs_injected_only_into_requiring_stages() -> None:
    from apps_repo_brief.integrations.repo_brief_l3_workflow_adapter import (
        RepoBriefL3WorkflowAdapter,
    )

    ctx = {
        "c0_fec": {
            "c0_state": "PASS",
            "evidence_status": "PASS",
            "contradiction_flags": [],
            "evidence_ids": ["ref-1", "ref-2"],
        }
    }
    result = RepoBriefL3WorkflowAdapter().expand(ctx)

    for stage in result.stages:
        if stage["requires_evidence_refs"]:
            assert "ref-1" in stage["injected_evidence_refs"]
            assert "ref-2" in stage["injected_evidence_refs"]
        else:
            assert stage["injected_evidence_refs"] == []


# ---------------------------------------------------------------------------
# Test 10: spine_handoff calls expand() fail-soft
# ---------------------------------------------------------------------------

def test_spine_handoff_expand_fail_soft() -> None:
    from apps_repo_brief.integrations.spine_handoff import run_repo_brief_via_spine

    request = SimpleNamespace(
        trace_id="trace-l3-test",
        brief_type="executive",
        audience="engineers",
        emphasis_areas=[],
        c0_required=True,
        depth_profile="REPO_BRIEF_STANDARD",
        policy_hash="",
        blueprint_hash="",
        repo_snapshot_id="",
        replay_key="",
        normalized_request_hash="",
        persona_schema_version="",
    )
    mock_runner = MagicMock()
    mock_runner.run.return_value = {"trace_id": "trace-l3-test", "c0_fec": None}

    with patch(
        "apps_repo_brief.integrations.repo_brief_l3_workflow_adapter.RepoBriefL3WorkflowAdapter.expand",
        side_effect=RuntimeError("adapter exploded"),
    ):
        result = run_repo_brief_via_spine(request, runner=mock_runner)

    mock_runner.run.assert_called_once()
    assert result is not None
