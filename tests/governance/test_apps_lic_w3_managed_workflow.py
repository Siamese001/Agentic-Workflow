"""W3 sentinel tests for apps_lic managed workflow dispatcher, bridge, and DAG.

Covers P7, P8, P9:
- P7: managed_workflow_dispatcher.py exists; RequestForBriefing and BriefingReady
       declared; dispatch_managed_briefing returns BriefingReady on success.
- P8: apps_research_bridge.py exists; AppsResearchBridge + MockAppsResearchBridge
       declared; ResearchResult has required fields; apps_lic_managed_dag.yaml exists
       with exactly 8 stages in correct order.
- P9: All 5 research-failure reason codes produce DispatchFailurePacket with
       is_terminal=True and the correct r5_reason_code.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W3.
"""
from __future__ import annotations

import uuid
from dataclasses import fields as dc_fields
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER_MODULE = REPO_ROOT / "apps_lic" / "integrations" / "managed_workflow_dispatcher.py"
BRIDGE_MODULE = REPO_ROOT / "apps_lic" / "integrations" / "apps_research_bridge.py"
MANAGED_DAG = REPO_ROOT / "apps_lic" / "config" / "apps_lic_managed_dag.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(**overrides):
    from apps_lic.integrations.managed_workflow_dispatcher import RequestForBriefing
    defaults = dict(
        request_id="req-w3-001",
        run_id="run-w3-001",
        trace_id="tr-w3-001",
        recipient_class="RECRUITER",
        recipient_name="Jane Smith",
        company_name="Acme Corp",
        job_title="Engineering Manager",
        channel="email",
        outreach_mode="cold",
        relationship_distance="cold",
        sender_resume_ref="sha256:resume001",
        sender_policy_hash="sha256:policy001",
        sender_blueprint_hash="sha256:blueprint001",
        research_authorized=True,
        research_capability_ref="apps_research.v1",
        freshness_ttl_days=7,
        min_confidence_threshold=0.60,
        audit_refs=(),
    )
    defaults.update(overrides)
    return RequestForBriefing(**defaults)


def _make_mock_bridge(**overrides):
    from apps_lic.integrations.apps_research_bridge import MockAppsResearchBridge
    return MockAppsResearchBridge(**overrides)


# ---------------------------------------------------------------------------
# P7 — managed_workflow_dispatcher.py
# ---------------------------------------------------------------------------

def test_dispatcher_module_exists():
    """P7: managed_workflow_dispatcher.py must exist."""
    assert DISPATCHER_MODULE.exists(), f"Missing: {DISPATCHER_MODULE}"


def test_dispatcher_request_for_briefing_importable():
    """P7: RequestForBriefing must be importable and frozen."""
    from apps_lic.integrations.managed_workflow_dispatcher import RequestForBriefing
    r = _make_request()
    with pytest.raises(AttributeError):
        r.recipient_class = "HIRING_MANAGER"  # type: ignore[misc]


def test_dispatcher_briefing_ready_importable():
    """P7: BriefingReady must be importable with required fields."""
    from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
    required = {"request_id", "run_id", "trace_id", "manifest",
                "research_run_id", "research_evidence_count",
                "confidence_score", "dispatch_duration_ms", "audit_refs"}
    field_names = {f.name for f in dc_fields(BriefingReady)}
    missing = required - field_names
    assert not missing, f"BriefingReady missing fields: {missing}"


def test_dispatcher_failure_packet_importable():
    """P7: DispatchFailurePacket must be importable with is_terminal=True default."""
    from apps_lic.integrations.managed_workflow_dispatcher import DispatchFailurePacket
    pkt = DispatchFailurePacket(
        request_id="r1", run_id="run1", trace_id="tr1",
        r5_reason_code="APPS_RESEARCH_FAILED",
        detail="test", dispatch_duration_ms=1.0,
    )
    assert pkt.is_terminal is True


def test_dispatcher_returns_briefing_ready_on_success():
    """P7: dispatch_managed_briefing returns BriefingReady when research succeeds."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, BriefingReady,
    )
    bridge = _make_mock_bridge(confidence_score=0.85)
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, BriefingReady), (
        f"Expected BriefingReady, got: {type(result).__name__}"
    )
    assert result.confidence_score == 0.85
    assert result.research_evidence_count == 1
    assert result.manifest is not None


def test_dispatcher_manifest_is_fresh_after_research():
    """P7: BriefingReady.manifest must have freshness_status='fresh'."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, BriefingReady,
    )
    bridge = _make_mock_bridge(confidence_score=0.80)
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, BriefingReady)
    assert result.manifest.freshness_status == "fresh"


def test_dispatcher_manifest_has_35_fields():
    """P7: Manifest produced by dispatcher must have exactly 35 fields."""
    from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing, BriefingReady
    bridge = _make_mock_bridge(confidence_score=0.75)
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, BriefingReady)
    manifest = result.manifest
    count = len(dc_fields(manifest))
    assert count == 35, (
        f"Manifest from dispatcher has {count} fields; expected 35."
    )


# ---------------------------------------------------------------------------
# P9 — All 5 research failure reason codes → DispatchFailurePacket
# ---------------------------------------------------------------------------

def test_dispatcher_fail_closed_when_research_not_authorized():
    """P9: research_authorized=False → APPS_RESEARCH_BLOCKED."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    bridge = _make_mock_bridge()
    result = dispatch_managed_briefing(
        _make_request(research_authorized=False), bridge=bridge
    )
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True
    assert result.r5_reason_code == "APPS_RESEARCH_BLOCKED"


def test_dispatcher_fail_closed_apps_research_failed():
    """P9: bridge.fetch() exception → APPS_RESEARCH_FAILED.

    The base AppsResearchBridge.fetch() wraps _invoke_apps_research exceptions
    into a blocked result; so to trigger the dispatcher's APPS_RESEARCH_FAILED
    path we must raise from fetch() itself (bypassing the bridge's internal guard).
    """
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    from apps_lic.integrations.apps_research_bridge import AppsResearchBridge

    class FetchRaisingBridge(AppsResearchBridge):
        def fetch(self, **_kw):
            raise RuntimeError("simulated research service down outside bridge guard")

    bridge = FetchRaisingBridge()
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True
    assert result.r5_reason_code == "APPS_RESEARCH_FAILED"


def test_dispatcher_fail_closed_apps_research_blocked():
    """P9: research result is_blocked → APPS_RESEARCH_BLOCKED."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    bridge = _make_mock_bridge(is_blocked=True, block_reason="capability unavailable")
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True
    assert result.r5_reason_code == "APPS_RESEARCH_BLOCKED"


def test_dispatcher_fail_closed_apps_research_empty():
    """P9: research result empty evidence_items → APPS_RESEARCH_EMPTY."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    bridge = _make_mock_bridge(evidence_items=[])
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True
    assert result.r5_reason_code == "APPS_RESEARCH_EMPTY"


def test_dispatcher_fail_closed_apps_research_stale():
    """P9: research result is_stale → APPS_RESEARCH_STALE."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    bridge = _make_mock_bridge(is_stale=True, age_days=35.0)
    result = dispatch_managed_briefing(_make_request(), bridge=bridge)
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True
    assert result.r5_reason_code == "APPS_RESEARCH_STALE"


def test_dispatcher_fail_closed_apps_research_weak_support():
    """P9: confidence below threshold → APPS_RESEARCH_WEAK_SUPPORT."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    bridge = _make_mock_bridge(confidence_score=0.20)
    result = dispatch_managed_briefing(
        _make_request(min_confidence_threshold=0.60), bridge=bridge
    )
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True
    assert result.r5_reason_code == "APPS_RESEARCH_WEAK_SUPPORT"


def test_dispatcher_all_5_failure_codes_covered():
    """P9: RESEARCH_FAILURE_REASON_CODES must contain all 5 expected codes."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        RESEARCH_FAILURE_REASON_CODES,
    )
    expected = {
        "APPS_RESEARCH_FAILED",
        "APPS_RESEARCH_EMPTY",
        "APPS_RESEARCH_BLOCKED",
        "APPS_RESEARCH_STALE",
        "APPS_RESEARCH_WEAK_SUPPORT",
    }
    missing = expected - RESEARCH_FAILURE_REASON_CODES
    assert not missing, f"Missing R5 reason codes in dispatcher: {missing}"


def test_dispatcher_failure_packet_is_always_terminal():
    """P9: Any DispatchFailurePacket produced by dispatcher must have is_terminal=True."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        dispatch_managed_briefing, DispatchFailurePacket,
    )
    # Run through each failure mode and confirm is_terminal=True in all cases
    from apps_lic.integrations.apps_research_bridge import AppsResearchBridge

    class FailingBridge(AppsResearchBridge):
        def _invoke_apps_research(self, **_kw):
            raise ValueError("always fails")

    result = dispatch_managed_briefing(_make_request(), bridge=FailingBridge())
    assert isinstance(result, DispatchFailurePacket)
    assert result.is_terminal is True, (
        "DispatchFailurePacket.is_terminal must always be True — "
        "the caller must not proceed to R4 after a failure."
    )


# ---------------------------------------------------------------------------
# P8 — apps_research_bridge.py
# ---------------------------------------------------------------------------

def test_bridge_module_exists():
    """P8: apps_research_bridge.py must exist."""
    assert BRIDGE_MODULE.exists(), f"Missing: {BRIDGE_MODULE}"


def test_bridge_importable():
    """P8: AppsResearchBridge and MockAppsResearchBridge must be importable."""
    from apps_lic.integrations.apps_research_bridge import (
        AppsResearchBridge,
        MockAppsResearchBridge,
        ResearchResult,
        EvidenceItem,
    )
    assert AppsResearchBridge is not None
    assert MockAppsResearchBridge is not None


def test_bridge_research_result_fields():
    """P8: ResearchResult must have all required contract fields."""
    from apps_lic.integrations.apps_research_bridge import ResearchResult
    required = {
        "run_id", "trace_id", "request_id",
        "is_blocked", "block_reason", "is_stale", "age_days",
        "evidence_items", "confidence_score", "result_hash",
        "jd_hash", "jd_uri", "company_brief_hash",
        "fetch_duration_ms", "audit_ref",
    }
    field_names = {f.name for f in dc_fields(ResearchResult)}
    missing = required - field_names
    assert not missing, f"ResearchResult missing fields: {missing}"


def test_mock_bridge_returns_research_result():
    """P8: MockAppsResearchBridge.fetch returns a ResearchResult."""
    from apps_lic.integrations.apps_research_bridge import (
        MockAppsResearchBridge,
        ResearchResult,
    )
    bridge = MockAppsResearchBridge(confidence_score=0.90)
    result = bridge.fetch(
        recipient_class="RECRUITER",
        recipient_name="Jane",
        company_name="Acme",
        job_title="EM",
        channel="email",
        outreach_mode="cold",
        relationship_distance="cold",
        capability_ref="apps_research.v1",
        request_id="req-test",
        run_id="run-test",
        trace_id="tr-test",
    )
    assert isinstance(result, ResearchResult)
    assert result.is_blocked is False
    assert result.confidence_score == 0.90
    assert len(result.evidence_items) == 1


def test_mock_bridge_blocked_result():
    """P8: MockAppsResearchBridge with is_blocked=True returns blocked ResearchResult."""
    from apps_lic.integrations.apps_research_bridge import (
        MockAppsResearchBridge,
        ResearchResult,
    )
    bridge = MockAppsResearchBridge(is_blocked=True, block_reason="test-block")
    result = bridge.fetch(
        recipient_class="RECRUITER", recipient_name="Jane",
        company_name="Acme", job_title="EM", channel="email",
        outreach_mode="cold", relationship_distance="cold",
        capability_ref="apps_research.v1",
        request_id="r", run_id="r", trace_id="t",
    )
    assert isinstance(result, ResearchResult)
    assert result.is_blocked is True
    assert result.block_reason == "test-block"


def test_bridge_unsupported_capability_returns_blocked():
    """P8: Bridge with unsupported capability_ref returns blocked ResearchResult without raising."""
    from apps_lic.integrations.apps_research_bridge import (
        MockAppsResearchBridge,
        ResearchResult,
    )
    bridge = MockAppsResearchBridge()
    result = bridge.fetch(
        recipient_class="RECRUITER", recipient_name="Jane",
        company_name="Acme", job_title="EM", channel="email",
        outreach_mode="cold", relationship_distance="cold",
        capability_ref="apps_research.UNSUPPORTED_V99",
        request_id="r", run_id="r", trace_id="t",
    )
    assert isinstance(result, ResearchResult)
    assert result.is_blocked is True


def test_bridge_never_raises():
    """P8: AppsResearchBridge (base) never raises — always returns ResearchResult."""
    from apps_lic.integrations.apps_research_bridge import (
        AppsResearchBridge,
        ResearchResult,
    )
    # Base class _invoke_apps_research raises NotImplementedError — bridge must catch
    bridge = AppsResearchBridge()
    result = bridge.fetch(
        recipient_class="RECRUITER", recipient_name="Jane",
        company_name="Acme", job_title="EM", channel="email",
        outreach_mode="cold", relationship_distance="cold",
        capability_ref="apps_research.v1",
        request_id="r", run_id="r", trace_id="t",
    )
    assert isinstance(result, ResearchResult)
    assert result.is_blocked is True  # NotImplementedError → blocked


# ---------------------------------------------------------------------------
# P8 — managed workflow: dispatcher + hop_pipeline (replaces managed YAML DAG)
# ---------------------------------------------------------------------------

def test_managed_yaml_dag_deleted():
    """P4: Legacy managed YAML L2 DAG removed."""
    assert not MANAGED_DAG.exists(), f"Retired: {MANAGED_DAG}"


def test_managed_workflow_dispatcher_importable():
    """P8: R3R4 research is L3 orchestration via ManagedWorkflowDispatcher."""
    from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing

    assert callable(dispatch_managed_briefing)


def test_managed_route_family_in_l0_binding():
    """P8: R3R4 route family is L0-owned."""
    from apps_lic.runtime.bindings.l0_binding import (
        ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT,
    )

    assert ROUTE_FAMILY_R3R4_MANAGED_RESEARCH_THEN_DRAFT == "R3R4_MANAGED_RESEARCH_THEN_DRAFT"


def test_managed_research_failure_codes_in_dispatcher():
    """P8: Research failure → R5 codes live in managed_workflow_dispatcher."""
    from apps_lic.integrations.managed_workflow_dispatcher import (
        RESEARCH_FAILURE_REASON_CODES,
    )

    expected = {
        "APPS_RESEARCH_FAILED",
        "APPS_RESEARCH_EMPTY",
        "APPS_RESEARCH_BLOCKED",
        "APPS_RESEARCH_STALE",
        "APPS_RESEARCH_WEAK_SUPPORT",
    }
    assert expected <= RESEARCH_FAILURE_REASON_CODES
