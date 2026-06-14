"""Wave 5 ADG testing-hotspots — apps_underwriting_ai.decision_packet_assembler.

The assembler's verdict path is 100% deterministic (legally-binding in the
regulated domain); the LLM only enriches the rationale paragraph and falls
through to deterministic text on any failure. With
``APPS_UW_RATIONALE_LLM_DISABLED=1`` the cascade is skipped entirely, making
``assemble`` fully testable with real DeterministicRiskScorer inputs. This
module covers: module guard constants, the no-request INSUFFICIENT_EVIDENCE
branch, the legacy fallback bundle invariant, the rubric-identity fallback,
firewall-gate fail-soft, and a full deterministic assemble() path.
"""

from __future__ import annotations

import pytest

from apps_underwriting_ai.engines.decision_packet_assembler import (
    _MAX_RATIONALE_CHARS,
    _REGULATOR_TOKENS,
    DecisionPacketAssembler,
    _load_rubric_identity_safe,
)
from apps_underwriting_ai.types.underwriting_types import (
    DecisionVerdict,
    EvidenceRecord,
    EvidenceRegister,
    ReconciliationResult,
    RiskFeatures,
    UnderwritingRequest,
)


@pytest.fixture(autouse=True)
def _disable_llm(monkeypatch):
    # Keep the deterministic compliance floor; never reach a live provider.
    monkeypatch.setenv("APPS_UW_RATIONALE_LLM_DISABLED", "1")


@pytest.fixture
def assembler() -> DecisionPacketAssembler:
    return DecisionPacketAssembler()


class TestModuleGuards:
    def test_regulator_tokens(self):
        assert "FCA" in _REGULATOR_TOKENS
        assert "SEC" in _REGULATOR_TOKENS

    def test_max_rationale_chars_bound(self):
        assert _MAX_RATIONALE_CHARS == 600


class TestNoRequestBranch:
    def test_returns_insufficient_evidence(self, assembler):
        packet = assembler.assemble(request=None)
        assert packet.verdict == DecisionVerdict.INSUFFICIENT_EVIDENCE
        assert "No UnderwritingRequest provided" in packet.rationale
        assert packet.request_id == ""

    def test_carries_evidence_refs_when_register_supplied(self, assembler):
        register = EvidenceRegister(
            request_id="r1",
            records=(EvidenceRecord(evidence_id="E1", source="doc", kind="pdf"),),
        )
        packet = assembler.assemble(request=None, register=register)
        assert packet.evidence_refs == ("E1",)

    def test_carries_feature_summary_when_features_supplied(self, assembler):
        features = RiskFeatures(feature_vector={"score": 0.5})
        packet = assembler.assemble(request=None, features=features)
        assert packet.feature_summary == {"score": 0.5}


class TestLegacyFallbackBundle:
    def test_invariants(self):
        bundle = DecisionPacketAssembler._legacy_fallback_bundle()
        assert bundle["__legacy_fallback_bundle__"] is True
        assert bundle["open_web_blocked"] is True
        # No evidence IDs — firewall cannot accept any LLM evidence citation.
        assert bundle["evidence_ids"] == []
        assert bundle["c0_mode"] == "SUBMITTED_DOCUMENT_EVIDENCE_ONLY"


class TestRubricIdentity:
    def test_returns_tuple_of_id_and_version(self):
        rubric_id, version = _load_rubric_identity_safe()
        assert isinstance(rubric_id, str) and rubric_id
        assert isinstance(version, int)


class TestFirewallGateFailSoft:
    def test_returns_fallback_result_on_bad_bundle(self, assembler):
        # An empty/invalid bundle must never raise — fail-soft to deterministic.
        result = assembler.run_pa_firewall(
            verdict="approve",
            reason_codes=[],
            c0_bundle={},
            deterministic_rationale="deterministic text",
        )
        assert hasattr(result, "rationale")
        # Either the real firewall blocked or the import/init fell through;
        # in both cases the deterministic rationale must survive.
        if getattr(result, "deterministic_fallback_used", False):
            assert result.rationale == "deterministic text"


class TestDeterministicAssemble:
    def _request(self) -> UnderwritingRequest:
        return UnderwritingRequest(
            request_id="req-1",
            applicant_id="app-1",
            product_class="auto",
            documents=({"type": "application"},),
        )

    def test_full_path_produces_packet_with_risk_keys(self, assembler):
        register = EvidenceRegister(
            request_id="req-1",
            records=(EvidenceRecord(evidence_id="E1", source="doc", kind="pdf"),),
        )
        features = RiskFeatures(feature_vector={"base": 0.4})
        reconciliation = ReconciliationResult(reconciled_count=1, unresolved_count=0)
        packet = assembler.assemble(
            request=self._request(),
            register=register,
            features=features,
            reconciliation=reconciliation,
        )
        assert packet.request_id == "req-1"
        assert isinstance(packet.verdict, DecisionVerdict)
        # Scorer breakdown surfaced under stable risk_* keys for audit.
        assert "risk_score" in packet.feature_summary
        assert "risk_product_tier" in packet.feature_summary
        assert packet.evidence_refs == ("E1",)

    def test_verdict_is_deterministic_across_runs(self, assembler):
        req = self._request()
        a = assembler.assemble(request=req)
        b = assembler.assemble(request=req)
        assert a.verdict == b.verdict
        assert a.feature_summary["risk_score"] == b.feature_summary["risk_score"]

    def test_firewall_flags_present_in_summary(self, assembler):
        packet = assembler.assemble(request=self._request())
        assert "firewall_passed" in packet.feature_summary
        assert "deterministic_rationale_fallback_used" in packet.feature_summary
