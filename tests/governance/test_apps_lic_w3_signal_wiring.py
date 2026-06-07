"""apps_lic calibration-holdout W3 — signal engine wiring tests.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-calibration-holdout-e8f1c4.md W3
Covers DS2-P1 (5 signal engines wired into managed_workflow_dispatcher)
and DS8-P1 (uwg_submit injectable on CampaignBatchOrchestrator).

Tests verify:
  DS2-P1:
  - BriefingReady carries 5 optional signal engine decision fields.
  - dispatch_managed_briefing wires all 5 engines non-blocking.
  - When engines are disabled (no env var), fields are disabled sentinels.
  - When engines are enabled, fields are populated on success path.
  - Signal engine exception does NOT abort dispatch (non-blocking).
  - DispatchFailurePacket is unaffected (no signal fields).

  DS8-P1:
  - CampaignBatchOrchestrator accepts uwg_submit kwarg.
  - uwg_submit is called with BatchAdmissionReceipt after dispatch.
  - uwg_submit exception does NOT abort dispatch or raise to caller.
  - Receipt returned even when uwg_submit raises.
  - uwg_submit=None (default) behaves exactly as before.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, call

import pytest


# ===========================================================================
# Fixtures / helpers
# ===========================================================================

def _make_good_research_result(evidence_count: int = 2):
    """Minimal stub that passes all 5 P9 checks."""
    @dataclass
    class _EvidenceItem:
        label: str = "test"
        uri: str = "https://example.com/ev"
        field_ref: str = "recipient_brief_ref"

    @dataclass
    class _ResearchResult:
        is_blocked: bool = False
        is_stale: bool = False
        confidence_score: float = 0.85
        evidence_items: list = None
        run_id: str = "rr-001"
        trace_id: str = "tr-001"

        def __post_init__(self):
            if self.evidence_items is None:
                self.evidence_items = [_EvidenceItem() for _ in range(evidence_count)]

    return _ResearchResult()


def _make_request(**kwargs):
    from apps_lic.integrations.managed_workflow_dispatcher import RequestForBriefing
    defaults = dict(
        request_id="req-001",
        run_id="run-001",
        trace_id="tr-001",
        recipient_class="HIRING_MANAGER",
        recipient_name="Alice",
        company_name="Acme",
        job_title="Eng",
        channel="email",
        outreach_mode="cold",
        relationship_distance="cold",
        sender_resume_ref="sha256:abc",
        sender_policy_hash="sha256:def",
        sender_blueprint_hash="sha256:ghi",
        research_authorized=True,
        research_capability_ref="cap-001",
    )
    defaults.update(kwargs)
    return RequestForBriefing(**defaults)


def _make_bridge(research_result=None):
    bridge = MagicMock()
    bridge.fetch.return_value = research_result or _make_good_research_result()
    return bridge


# ===========================================================================
# DS2-P1: BriefingReady signal engine fields present
# ===========================================================================

class TestBriefingReadySignalFields:
    def test_briefing_ready_has_arc_decision_field(self):
        from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BriefingReady)}
        assert "arc_decision" in field_names

    def test_briefing_ready_has_tone_decision_field(self):
        from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BriefingReady)}
        assert "tone_decision" in field_names

    def test_briefing_ready_has_touch_decision_field(self):
        from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BriefingReady)}
        assert "touch_decision" in field_names

    def test_briefing_ready_has_resurfacing_decision_field(self):
        from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BriefingReady)}
        assert "resurfacing_decision" in field_names

    def test_briefing_ready_has_mutual_network_signal_field(self):
        from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BriefingReady)}
        assert "mutual_network_signal" in field_names

    def test_all_signal_fields_default_none(self):
        from apps_lic.integrations.managed_workflow_dispatcher import BriefingReady
        import dataclasses
        fields_with_defaults = {
            f.name: f.default
            for f in dataclasses.fields(BriefingReady)
            if f.name in (
                "arc_decision", "tone_decision", "touch_decision",
                "resurfacing_decision", "mutual_network_signal",
            )
        }
        for name, default in fields_with_defaults.items():
            assert default is None, f"{name} default should be None"


# ===========================================================================
# DS2-P1: dispatch_managed_briefing wires all 5 engines
# ===========================================================================

class TestDispatchSignalEngineWiring:
    def test_engines_disabled_result_has_none_fields(self, monkeypatch):
        """All 5 env vars absent → engines disabled → all signal fields None."""
        for env in (
            "ARC_ENGINE_ENABLED", "ARCHETYPE_TONE_ENABLED",
            "MULTI_TOUCH_ENABLED", "RESURFACING_ENABLED", "MUTUAL_NETWORK_ENABLED",
            "BRIEFING_QUALITY_BYPASS",
        ):
            monkeypatch.delenv(env, raising=False)

        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing
        result = dispatch_managed_briefing(
            _make_request(), bridge=_make_bridge()
        )
        # All engines disabled → decisions have enabled=False (not None — disabled sentinel)
        assert result.arc_decision is not None          # disabled sentinel, not None
        assert result.arc_decision.enabled is False
        assert result.tone_decision is not None
        assert result.tone_decision.enabled is False
        assert result.touch_decision is not None
        assert result.touch_decision.enabled is False
        assert result.resurfacing_decision is not None
        assert result.resurfacing_decision.enabled is False
        assert result.mutual_network_signal is not None
        assert result.mutual_network_signal.enabled is False

    def test_arc_engine_enabled_populates_field(self, monkeypatch):
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")
        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing
        result = dispatch_managed_briefing(_make_request(), bridge=_make_bridge())
        assert result.arc_decision is not None
        assert result.arc_decision.enabled is True
        assert result.arc_decision.arc_name != ""

    def test_tone_engine_enabled_populates_field(self, monkeypatch):
        monkeypatch.setenv("ARCHETYPE_TONE_ENABLED", "1")
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")
        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing
        result = dispatch_managed_briefing(_make_request(), bridge=_make_bridge())
        assert result.tone_decision is not None
        assert result.tone_decision.enabled is True
        assert result.tone_decision.archetype != ""

    def test_touch_engine_enabled_populates_field(self, monkeypatch):
        monkeypatch.setenv("MULTI_TOUCH_ENABLED", "1")
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")
        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing
        result = dispatch_managed_briefing(_make_request(), bridge=_make_bridge())
        assert result.touch_decision is not None
        assert result.touch_decision.enabled is True
        assert result.touch_decision.next_touch_number >= 1

    def test_resurfacing_engine_enabled_populates_field(self, monkeypatch):
        monkeypatch.setenv("RESURFACING_ENABLED", "1")
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")
        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing
        result = dispatch_managed_briefing(_make_request(), bridge=_make_bridge())
        assert result.resurfacing_decision is not None
        assert result.resurfacing_decision.enabled is True

    def test_mutual_network_enabled_populates_field(self, monkeypatch):
        monkeypatch.setenv("MUTUAL_NETWORK_ENABLED", "1")
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")
        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing
        result = dispatch_managed_briefing(_make_request(), bridge=_make_bridge())
        assert result.mutual_network_signal is not None
        assert result.mutual_network_signal.enabled is True

    def test_signal_engine_exception_does_not_abort(self, monkeypatch):
        """If an engine raises, dispatch still returns BriefingReady."""
        monkeypatch.setenv("ARC_ENGINE_ENABLED", "1")
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")

        import apps_lic.engines.narrative_arc_engine as _arc_mod
        original_cls = _arc_mod.NarrativeArcEngine

        class _BrokenEngine:
            def __init__(self, *a, **kw): pass
            def select(self, **kw): raise RuntimeError("boom")

        monkeypatch.setattr(_arc_mod, "NarrativeArcEngine", _BrokenEngine)
        # also patch the dispatcher's reference
        import apps_lic.integrations.managed_workflow_dispatcher as _disp_mod
        monkeypatch.setattr(_disp_mod, "NarrativeArcEngine", _BrokenEngine)

        from apps_lic.integrations.managed_workflow_dispatcher import dispatch_managed_briefing, BriefingReady
        result = dispatch_managed_briefing(_make_request(), bridge=_make_bridge())
        assert isinstance(result, BriefingReady)
        # arc_decision should be None when engine raised
        assert result.arc_decision is None

    def test_dispatch_failure_packet_unaffected(self, monkeypatch):
        """research_authorized=False → DispatchFailurePacket (no signal fields)."""
        from apps_lic.integrations.managed_workflow_dispatcher import (
            dispatch_managed_briefing, DispatchFailurePacket,
        )
        result = dispatch_managed_briefing(
            _make_request(research_authorized=False), bridge=_make_bridge()
        )
        assert isinstance(result, DispatchFailurePacket)
        assert not hasattr(result, "arc_decision")


# ===========================================================================
# DS8-P1: CampaignBatchOrchestrator uwg_submit wiring
# ===========================================================================

class TestCampaignBatchOrchestratorUwgSubmit:
    def _make_batch_request(self, n: int = 2):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            BatchCampaignRequest, BatchRecipientRequest,
        )
        entries = [
            BatchRecipientRequest(
                recipient_id=f"r{i}",
                campaign_request=MagicMock(),
                manifest_hash=f"sha256:abc{i:06d}",
            )
            for i in range(n)
        ]
        return BatchCampaignRequest(
            batch_id="batch-001",
            sender_id="sender-001",
            entries=tuple(entries),
        )

    def _make_run_fn(self):
        def run_fn(req):
            m = MagicMock()
            m.run_id = "rr-001"
            return m
        return run_fn

    def test_uwg_submit_called_with_receipt(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            CampaignBatchOrchestrator, BatchAdmissionReceipt,
        )
        submitted = []
        def uwg_submit(receipt): submitted.append(receipt)

        orch = CampaignBatchOrchestrator(
            run_fn=self._make_run_fn(),
            uwg_submit=uwg_submit,
            config={"max_recipients_per_batch": 10},
        )
        receipt = orch.dispatch(self._make_batch_request(2))
        assert len(submitted) == 1
        assert submitted[0] is receipt
        assert isinstance(submitted[0], BatchAdmissionReceipt)

    def test_uwg_submit_receives_correct_batch_id(self):
        from apps_lic.integrations.campaign_batch_orchestrator import CampaignBatchOrchestrator
        submitted = []
        orch = CampaignBatchOrchestrator(
            run_fn=self._make_run_fn(),
            uwg_submit=lambda r: submitted.append(r.batch_id),
            config={"max_recipients_per_batch": 10},
        )
        orch.dispatch(self._make_batch_request(1))
        assert submitted == ["batch-001"]

    def test_uwg_submit_exception_does_not_raise(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            CampaignBatchOrchestrator, BatchAdmissionReceipt,
        )
        def bad_uwg(receipt): raise RuntimeError("UWG down")

        orch = CampaignBatchOrchestrator(
            run_fn=self._make_run_fn(),
            uwg_submit=bad_uwg,
            config={"max_recipients_per_batch": 10},
        )
        receipt = orch.dispatch(self._make_batch_request(1))
        assert isinstance(receipt, BatchAdmissionReceipt)

    def test_uwg_submit_none_default_behavior_unchanged(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            CampaignBatchOrchestrator, BatchAdmissionReceipt,
        )
        orch = CampaignBatchOrchestrator(
            run_fn=self._make_run_fn(),
            config={"max_recipients_per_batch": 10},
        )
        receipt = orch.dispatch(self._make_batch_request(2))
        assert isinstance(receipt, BatchAdmissionReceipt)
        assert receipt.total_dispatched == 2

    def test_uwg_submit_called_once_per_dispatch(self):
        from apps_lic.integrations.campaign_batch_orchestrator import CampaignBatchOrchestrator
        call_count = [0]
        def uwg_submit(receipt): call_count[0] += 1

        orch = CampaignBatchOrchestrator(
            run_fn=self._make_run_fn(),
            uwg_submit=uwg_submit,
            config={"max_recipients_per_batch": 10},
        )
        orch.dispatch(self._make_batch_request(3))
        orch.dispatch(self._make_batch_request(1))
        assert call_count[0] == 2  # once per dispatch(), not per recipient

    def test_uwg_submit_accepts_callable_kwarg(self):
        from apps_lic.integrations.campaign_batch_orchestrator import CampaignBatchOrchestrator
        import inspect
        sig = inspect.signature(CampaignBatchOrchestrator.__init__)
        assert "uwg_submit" in sig.parameters

    def test_receipt_returned_even_after_uwg_failure(self):
        from apps_lic.integrations.campaign_batch_orchestrator import (
            CampaignBatchOrchestrator, BatchAdmissionReceipt,
        )
        orch = CampaignBatchOrchestrator(
            run_fn=self._make_run_fn(),
            uwg_submit=lambda r: (_ for _ in ()).throw(ValueError("gone")),
            config={"max_recipients_per_batch": 10},
        )
        result = orch.dispatch(self._make_batch_request(2))
        assert isinstance(result, BatchAdmissionReceipt)
        assert result.total_requested == 2
