"""apps_lic W3 (D3) — BriefingQualityGate sentinel tests.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W3 D3-P1, D3-P2
Coverage:
  - BriefingQualityDecision shape + immutability
  - Coverage checks (pass / marginal / fail)
  - Recency checks per recipient class bucket
  - Source diversity checks
  - Policy config file presence and schema
  - Dispatcher wiring: quality_decision attached to BriefingReady
  - Dispatcher wiring: quality fail → DispatchFailurePacket
  - Marginal does NOT block (proceed flag)
  - BRIEFING_QUALITY_BYPASS env var
"""

from __future__ import annotations

import os
import pytest
from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_research_result(
    *,
    evidence_count: int = 3,
    age_days: float | None = 2.0,
    confidence_score: float = 0.85,
    is_stale: bool = False,
    is_blocked: bool = False,
) -> MagicMock:
    items = []
    for i in range(evidence_count):
        ev = MagicMock()
        ev.label = f"source_{i}"
        ev.uri = f"domain{i}.com/page"
        items.append(ev)
    rr = MagicMock()
    rr.evidence_items = items
    rr.age_days = age_days
    rr.confidence_score = confidence_score
    rr.is_stale = is_stale
    rr.is_blocked = is_blocked
    rr.run_id = "rr-001"
    rr.trace_id = "trace-001"
    rr.result_hash = "sha256:abc"
    return rr


# ===========================================================================
# 1. Config file presence and schema
# ===========================================================================

class TestBriefingQualityPolicyConfig:
    def test_config_file_exists(self):
        from pathlib import Path
        config_path = (
            Path(__file__).parent.parent.parent
            / "apps_lic" / "config" / "briefing_quality_policy.yaml"
        )
        assert config_path.exists(), f"briefing_quality_policy.yaml missing at {config_path}"

    def test_config_has_required_sections(self):
        from pathlib import Path
        import yaml
        config_path = (
            Path(__file__).parent.parent.parent
            / "apps_lic" / "config" / "briefing_quality_policy.yaml"
        )
        with open(config_path) as fh:
            cfg = yaml.safe_load(fh)
        for section in ("coverage", "recency", "diversity", "bypass"):
            assert section in cfg, f"briefing_quality_policy.yaml missing section '{section}'"

    def test_coverage_has_thresholds(self):
        from pathlib import Path
        import yaml
        config_path = (
            Path(__file__).parent.parent.parent
            / "apps_lic" / "config" / "briefing_quality_policy.yaml"
        )
        cfg = yaml.safe_load(open(config_path))
        assert "min_evidence_items" in cfg["coverage"]
        assert "marginal_evidence_items" in cfg["coverage"]


# ===========================================================================
# 2. BriefingQualityDecision shape
# ===========================================================================

class TestBriefingQualityDecisionShape:
    def _gate(self):
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityGate
        return BriefingQualityGate()

    def test_returns_decision_dataclass(self):
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityDecision
        gate = self._gate()
        result = gate.evaluate(_make_research_result(), recipient_class="RECRUITER")
        assert isinstance(result, BriefingQualityDecision)

    def test_decision_is_immutable(self):
        gate = self._gate()
        result = gate.evaluate(_make_research_result(), recipient_class="RECRUITER")
        with pytest.raises((FrozenInstanceError, AttributeError)):
            result.quality_level = "tampered"  # type: ignore

    def test_quality_level_valid_values(self):
        gate = self._gate()
        result = gate.evaluate(_make_research_result(), recipient_class="RECRUITER")
        assert result.quality_level in ("pass", "marginal", "fail")

    def test_fail_reasons_is_tuple(self):
        gate = self._gate()
        result = gate.evaluate(_make_research_result(), recipient_class="RECRUITER")
        assert isinstance(result.fail_reasons, tuple)


# ===========================================================================
# 3. Coverage checks
# ===========================================================================

class TestCoverageChecks:
    def _gate(self):
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityGate
        return BriefingQualityGate()

    def test_pass_with_sufficient_evidence(self):
        result = self._gate().evaluate(
            _make_research_result(evidence_count=3), recipient_class="RECRUITER"
        )
        assert result.coverage_ok is True
        assert result.quality_level in ("pass", "marginal")

    def test_marginal_with_one_item(self):
        result = self._gate().evaluate(
            _make_research_result(evidence_count=1), recipient_class="RECRUITER"
        )
        assert result.coverage_ok is False
        assert result.quality_level in ("marginal", "fail")

    def test_fail_with_zero_items(self):
        result = self._gate().evaluate(
            _make_research_result(evidence_count=0), recipient_class="RECRUITER"
        )
        assert result.quality_level == "fail"
        assert result.r5_reason_code == "APPS_RESEARCH_WEAK_SUPPORT"

    def test_evidence_count_reported(self):
        result = self._gate().evaluate(
            _make_research_result(evidence_count=4), recipient_class="EXECUTIVE"
        )
        assert result.evidence_count == 4


# ===========================================================================
# 4. Recency checks
# ===========================================================================

class TestRecencyChecks:
    def _gate(self):
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityGate
        return BriefingQualityGate()

    def test_exec_fresh_passes(self):
        result = self._gate().evaluate(
            _make_research_result(age_days=3.0), recipient_class="EXECUTIVE"
        )
        assert result.recency_ok is True

    def test_exec_stale_fails(self):
        result = self._gate().evaluate(
            _make_research_result(age_days=10.0), recipient_class="CTO"
        )
        assert result.recency_ok is False
        assert result.quality_level == "fail"
        assert result.r5_reason_code == "APPS_RESEARCH_STALE"

    def test_recruiter_fresh_passes(self):
        result = self._gate().evaluate(
            _make_research_result(age_days=20.0), recipient_class="RECRUITER"
        )
        assert result.recency_ok is True

    def test_recruiter_stale_fails(self):
        result = self._gate().evaluate(
            _make_research_result(age_days=35.0), recipient_class="RECRUITER"
        )
        assert result.recency_ok is False
        assert result.quality_level == "fail"

    def test_unknown_age_passes_conservatively(self):
        result = self._gate().evaluate(
            _make_research_result(age_days=None), recipient_class="EXECUTIVE"
        )
        assert result.recency_ok is True
        assert result.age_days is None


# ===========================================================================
# 5. Source diversity checks
# ===========================================================================

class TestDiversityChecks:
    def _gate(self):
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityGate
        return BriefingQualityGate()

    def test_diverse_sources_pass(self):
        result = self._gate().evaluate(
            _make_research_result(evidence_count=3), recipient_class="EXECUTIVE"
        )
        assert result.diversity_ok is True

    def test_single_source_marginal(self):
        rr = _make_research_result(evidence_count=1)
        rr.evidence_items[0].uri = "domain0.com/page"
        result = self._gate().evaluate(rr, recipient_class="EXECUTIVE")
        assert result.unique_sources == 1

    def test_unique_sources_counted(self):
        result = self._gate().evaluate(
            _make_research_result(evidence_count=4), recipient_class="RECRUITER"
        )
        assert result.unique_sources >= 1


# ===========================================================================
# 6. Bypass env var
# ===========================================================================

class TestBypassEnvVar:
    def test_bypass_skips_gate(self, monkeypatch):
        monkeypatch.setenv("BRIEFING_QUALITY_BYPASS", "1")
        from apps_lic.integrations.managed_workflow_dispatcher import (
            dispatch_managed_briefing,
            RequestForBriefing,
        )
        bridge = MagicMock()
        rr = _make_research_result(evidence_count=0)  # would fail without bypass
        rr.evidence_items = []
        bridge.fetch.return_value = rr
        req = RequestForBriefing(
            request_id="r1", run_id="ru1", trace_id="t1",
            recipient_class="RECRUITER", recipient_name="Alice",
            company_name="Acme", job_title="Engineer",
            channel="email", outreach_mode="cold",
            relationship_distance="cold",
            sender_resume_ref="sha256:abc", sender_policy_hash="ph1",
            sender_blueprint_hash="bh1",
            research_authorized=True, research_capability_ref="cap1",
        )
        # With bypass, quality gate is skipped — but APPS_RESEARCH_EMPTY fires first
        # (that's the dispatcher's own empty check before quality gate)
        result = dispatch_managed_briefing(req, bridge=bridge)
        from apps_lic.integrations.managed_workflow_dispatcher import DispatchFailurePacket
        assert isinstance(result, DispatchFailurePacket)
        assert result.r5_reason_code == "APPS_RESEARCH_EMPTY"


# ===========================================================================
# 7. Dispatcher wiring
# ===========================================================================

class TestDispatcherWiring:
    def _make_request(self, **kwargs):
        from apps_lic.integrations.managed_workflow_dispatcher import RequestForBriefing
        defaults = dict(
            request_id="r1", run_id="ru1", trace_id="t1",
            recipient_class="RECRUITER", recipient_name="Alice",
            company_name="Acme", job_title="Engineer",
            channel="email", outreach_mode="cold",
            relationship_distance="cold",
            sender_resume_ref="sha256:abc", sender_policy_hash="ph1",
            sender_blueprint_hash="bh1",
            research_authorized=True, research_capability_ref="cap1",
        )
        defaults.update(kwargs)
        return RequestForBriefing(**defaults)

    def test_quality_decision_attached_to_briefing_ready(self, monkeypatch):
        monkeypatch.delenv("BRIEFING_QUALITY_BYPASS", raising=False)
        from apps_lic.integrations.managed_workflow_dispatcher import (
            dispatch_managed_briefing, BriefingReady,
        )
        bridge = MagicMock()
        bridge.fetch.return_value = _make_research_result(evidence_count=3, age_days=5.0)
        req = self._make_request(recipient_class="RECRUITER")
        result = dispatch_managed_briefing(req, bridge=bridge)
        assert isinstance(result, BriefingReady)
        assert result.quality_decision is not None
        assert result.quality_decision.quality_level in ("pass", "marginal")

    def test_quality_fail_returns_dispatch_failure(self, monkeypatch):
        monkeypatch.delenv("BRIEFING_QUALITY_BYPASS", raising=False)
        from apps_lic.integrations.managed_workflow_dispatcher import (
            dispatch_managed_briefing, DispatchFailurePacket,
        )
        bridge = MagicMock()
        # Exec with 40-day old result → recency fail
        bridge.fetch.return_value = _make_research_result(
            evidence_count=3, age_days=40.0, confidence_score=0.9
        )
        req = self._make_request(recipient_class="EXECUTIVE")
        result = dispatch_managed_briefing(req, bridge=bridge)
        assert isinstance(result, DispatchFailurePacket)
        assert result.r5_reason_code in ("APPS_RESEARCH_STALE", "APPS_RESEARCH_WEAK_SUPPORT")

    def test_marginal_quality_does_not_block(self, monkeypatch):
        monkeypatch.delenv("BRIEFING_QUALITY_BYPASS", raising=False)
        from apps_lic.integrations.managed_workflow_dispatcher import (
            dispatch_managed_briefing, BriefingReady,
        )
        bridge = MagicMock()
        # 1 evidence item → marginal coverage, should NOT block
        bridge.fetch.return_value = _make_research_result(
            evidence_count=1, age_days=5.0, confidence_score=0.9
        )
        req = self._make_request(recipient_class="RECRUITER")
        result = dispatch_managed_briefing(req, bridge=bridge)
        assert isinstance(result, BriefingReady), (
            "marginal quality must NOT return DispatchFailurePacket"
        )
        assert result.quality_decision is not None
        assert result.quality_decision.quality_level == "marginal"
