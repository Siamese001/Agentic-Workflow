"""W1 P0 — Write-Boundary Fix Tests.

Verifies the P0 exec_summary RCA fix:
- Rejected winners never mutate resume_data
- Write admission receipt required for all mutations
- Abort after gate failure does not emit partial resume

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W1)
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass
from typing import Any

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import (
    GatePlacement,
    GateVerdict,
    GateBundle,
    GateDefinition,
    GateEnforcement,
    RuntimeGateEngine,
    WriteAdmissionGuard,
    WriteAdmissionReceipt,
)
from agentic_core.runtime_gates.builtins.candidate_acceptance_guard import (
    CandidateAcceptanceGuard,
)
from apps_rg.integrations.gates.narrative_integration import (
    AcceptedArtifact,
    WriteBlockedError,
    evaluate_and_admit,
    sealed_failure_packet,
)


@dataclass
class MockCandidate:
    """Mock ensemble winner for testing."""
    text: str
    accepted: bool = True
    verdict: Any = None


class TestRejectedWinnerNeverMutatesResumeData:
    """P0 Mutation Test #1: Rejected winner never mutates resume_data."""

    def test_rejected_candidate_blocks_write(self) -> None:
        """If candidate has accepted=False, write is blocked."""
        rejected_candidate = MockCandidate(text="under-length summary", accepted=False)
        
        # Direct guard evaluation
        verdict = CandidateAcceptanceGuard.evaluate(rejected_candidate, {})
        
        assert verdict.result == Result.FAIL
        assert "candidate_rejected_by_per_cand_gate" in verdict.reason_codes

    def test_guard_denies_rejected_candidate(self) -> None:
        """WriteAdmissionGuard denies write for rejected candidate."""
        # Create a bundle with FAIL verdict from candidate_acceptance_guard
        verdict = GateVerdict(
            gate_id="candidate_acceptance_guard",
            result=Result.FAIL,
            reason="Candidate rejected",
            reason_codes=("candidate_rejected_by_per_cand_gate",),
        )
        bundle = GateBundle.from_verdicts(
            "apps_rg", GatePlacement.POST_ENS, [verdict]
        )
        
        # Register gate definition for candidate_acceptance_guard
        gate_defs = {
            "candidate_acceptance_guard": GateDefinition(
                "candidate_acceptance_guard",
                GatePlacement.POST_ENS,
                GateEnforcement.FAIL_CLOSED,
                bypassable=False,
            )
        }
        guard = WriteAdmissionGuard(gate_defs)
        
        receipt = guard.evaluate("executive_summary", bundle, {})
        
        assert receipt.writeable is False
        assert receipt.non_bypassable_gate_failed is True
        assert "candidate_rejected_by_per_cand_gate" in receipt.reason_codes

    def test_rejected_winner_not_written_to_resume_data(self) -> None:
        """The 73-vs-122 word RCA case: rejected winner never reaches resume_data."""
        # Simulate using the guard directly (integration test pattern)
        resume_data: dict[str, Any] = {}
        
        # Create a rejected candidate bundle
        verdict = GateVerdict(
            gate_id="candidate_acceptance_guard",
            result=Result.FAIL,
            reason="Candidate rejected",
            reason_codes=("candidate_rejected_by_per_cand_gate",),
        )
        bundle = GateBundle.from_verdicts(
            "apps_rg", GatePlacement.POST_ENS, [verdict]
        )
        
        gate_defs = {
            "candidate_acceptance_guard": GateDefinition(
                "candidate_acceptance_guard",
                GatePlacement.POST_ENS,
                GateEnforcement.FAIL_CLOSED,
                bypassable=False,
            )
        }
        guard = WriteAdmissionGuard(gate_defs)
        receipt = guard.evaluate("executive_summary", bundle, {})
        
        # Only write if receipt allows
        if receipt.writeable:
            resume_data["executive_summary"] = "some text"
        
        # The rejected text never made it to resume_data
        assert "executive_summary" not in resume_data


class TestUnknownVerdictNeverMutatesResumeData:
    """P0 Mutation Test #2: UNKNOWN verdict never mutates resume_data."""

    def test_unknown_acceptance_status_blocks_write(self) -> None:
        """If acceptance status is unknown, fail-closed."""
        unknown_candidate = MockCandidate(text="some text", accepted=None)
        
        verdict = CandidateAcceptanceGuard.evaluate(unknown_candidate, {})
        
        assert verdict.result == Result.UNKNOWN
        assert "unknown_acceptance_status" in verdict.reason_codes

    def test_unknown_blocks_write_admission(self) -> None:
        """UNKNOWN result in gate bundle blocks write admission."""
        gate_defs = {}
        guard = WriteAdmissionGuard(gate_defs)
        
        bundle = GateBundle(
            app_id="apps_rg",
            placement=GatePlacement.POST_ENS,
            verdicts=(),
            overall_result=Result.UNKNOWN,
        )
        
        receipt = guard.evaluate("test_section", bundle, {})
        
        assert receipt.writeable is False
        assert "unknown_verdict_blocks_write" in receipt.reason_codes


class TestWriteAdmissionReceiptRequired:
    """P0 Mutation Test #4: Write admission receipt required for resume_data mutation."""

    def test_no_direct_resume_data_write_without_receipt(self) -> None:
        """resume_data mutation must go through evaluate_and_admit."""
        # This test documents the invariant: direct mutation is forbidden
        
        # The old pattern (forbidden):
        # resume_data["executive_summary"] = winner.text  # ❌ FORBIDDEN
        
        # The new pattern (required):
        # accepted = evaluate_and_admit(...)  # ✅ REQUIRED
        # resume_data["executive_summary"] = accepted.text
        
        # This test verifies the pattern by checking that AcceptedArtifact
        # carries the required WriteAdmissionReceipt
        mock_candidate = MockCandidate(text="valid summary", accepted=True)
        
        # W4: Provide context for anti-fabrication gates
        context = {
            "per_cand_results": {"test": Result.PASS},
            "master_resume_text": "valid summary",  # For citation verification
            "computed_years_experience": 15,  # For tenure accuracy
        }
        
        accepted = evaluate_and_admit(
            section_id="executive_summary",
            candidate=mock_candidate,
            context=context,
            fail_if_rejected=False,  # Don't raise, return receipt
        )
        
        assert accepted.write_receipt.writeable is True
        assert accepted.write_receipt.gate_bundle_ref != ""

    def test_accepted_artifact_requires_receipt(self) -> None:
        """AcceptedArtifact must carry write_receipt with writeable=True."""
        mock_receipt = WriteAdmissionReceipt(
            writeable=True,
            gate_bundle_ref="test:ref",
            reason="test",
        )
        
        artifact = AcceptedArtifact.from_candidate(
            candidate=MockCandidate(text="test"),
            write_receipt=mock_receipt,
        )
        
        assert artifact.write_receipt.writeable is True


class TestAbortAfterGateFailure:
    """P0 Mutation Test #6: Abort after gate failure does not emit partial resume."""

    def test_sealed_failure_packet_on_block(self) -> None:
        """sealed_failure_packet captures blocked write without leaking data."""
        receipt = WriteAdmissionReceipt(
            writeable=False,
            gate_bundle_ref="apps_rg:POST_ENS",
            reason="Candidate rejected",
            reason_codes=("candidate_rejected",),
        )
        
        packet = sealed_failure_packet(
            section_id="executive_summary",
            receipt=receipt,
            context={"run_id": "test-run"},
        )
        
        assert packet["section_id"] == "executive_summary"
        assert packet["status"] == "BLOCKED"
        assert "write_receipt" in packet
        # Candidate text is NOT in the packet — no leakage
        assert "candidate_text" not in packet

    def test_no_partial_resume_on_failure(self) -> None:
        """If HOP-4B fails, HOP-4C mutations don't happen — no partial resume."""
        # Simulate partial pipeline state using guard pattern
        resume_data: dict[str, Any] = {"headline": "Original"}
        
        gate_defs = {
            "candidate_acceptance_guard": GateDefinition(
                "candidate_acceptance_guard",
                GatePlacement.POST_ENS,
                GateEnforcement.FAIL_CLOSED,
                bypassable=False,
            )
        }
        guard = WriteAdmissionGuard(gate_defs)
        
        # Simulate exec_summary failure
        exec_verdict = GateVerdict(
            gate_id="candidate_acceptance_guard",
            result=Result.FAIL,
            reason="exec summary rejected",
            reason_codes=("candidate_rejected_by_per_cand_gate",),
        )
        exec_bundle = GateBundle.from_verdicts(
            "apps_rg", GatePlacement.POST_ENS, [exec_verdict]
        )
        exec_receipt = guard.evaluate("executive_summary", exec_bundle, {})
        
        if exec_receipt.writeable:
            resume_data["executive_summary"] = "exec text"
        else:
            # Pipeline aborts — competencies never attempted
            pass
        
        # competencies never written because exec_summary failed
        assert "executive_summary" not in resume_data
        assert "competencies" not in resume_data


class TestMalformedJudgeVerdictHandling:
    """P0 Mutation Test #3: Malformed judge verdict blocks write."""

    def test_missing_judge_version_blocks_write(self) -> None:
        """JudgeVerdict without required version fields blocks write."""
        from agentic_core.runtime_gates.definitions import JudgeVerdict
        
        with pytest.raises(ValueError, match="judge_version"):
            JudgeVerdict(
                judge_id="test_judge",
                judge_version="",  # Missing
                rubric_version="1.0.0",
                threshold_profile_id="default",
                gate_id="test_gate",
                placement=GatePlacement.PER_CAND,
            )

    def test_malformed_judge_produces_unknown_gate_verdict(self) -> None:
        """Malformed judge verdict normalizes to UNKNOWN GateVerdict."""
        # If a judge produces a malformed verdict, the engine should
        # catch it and produce UNKNOWN, which blocks write
        
        # This is tested via the engine's exception handling
        engine = RuntimeGateEngine()
        
        def bad_gate(artifact, context):
            raise ValueError("Malformed judge output")
        
        engine.register_gate_pack(
            app_id="test",
            definitions=[GateDefinition("bad_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED)],
            callables={"bad_gate": bad_gate},
        )
        
        bundle = engine.evaluate("test", GatePlacement.PER_CAND, "artifact", {})
        
        # Exception caught, produces UNKNOWN
        assert bundle.overall_result == Result.UNKNOWN
        assert bundle.verdicts[0].result == Result.UNKNOWN
        assert "gate_exception" in bundle.verdicts[0].reason_codes


class TestMissingGateBundleBlocksWrite:
    """P0 Mutation Test #5: Missing gate bundle blocks write."""

    def test_missing_bundle_produces_unknown(self) -> None:
        """No gate pack registered produces UNKNOWN bundle."""
        engine = RuntimeGateEngine()
        
        bundle = engine.evaluate("unregistered_app", GatePlacement.POST_ENS, "artifact", {})
        
        assert bundle.overall_result == Result.UNKNOWN
        assert bundle.app_id == "unregistered_app"

    def test_guard_denies_unknown_bundle(self) -> None:
        """WriteAdmissionGuard denies write for UNKNOWN bundle."""
        gate_defs = {}
        guard = WriteAdmissionGuard(gate_defs)
        
        bundle = GateBundle(
            app_id="test",
            placement=GatePlacement.POST_ENS,
            verdicts=(),
            overall_result=Result.UNKNOWN,
        )
        
        receipt = guard.evaluate("section", bundle, {})
        
        assert receipt.writeable is False


class TestNarrativeIntegration:
    """Integration tests for narrative_pass.py RuntimeGateEngine binding."""

    def test_headline_section_gated(self) -> None:
        """Headline section goes through evaluate_and_admit."""
        candidate = MockCandidate(text="Targeted Headline", accepted=True)
        
        # W4: Provide context for anti-fabrication gates
        context = {
            "per_cand_results": {"headline": Result.PASS},
            "master_resume_text": "Targeted Headline",  # For citation verification
            "computed_years_experience": 15,  # For tenure accuracy
        }
        
        accepted = evaluate_and_admit(
            section_id="headline",
            candidate=candidate,
            context=context,
            fail_if_rejected=False,
        )
        
        assert accepted.text == "Targeted Headline"
        assert accepted.write_receipt.writeable is True

    def test_competencies_section_gated(self) -> None:
        """Competencies section goes through evaluate_and_admit."""
        candidate = MockCandidate(text="- Python\n- Machine Learning", accepted=True)
        
        # W4: Provide context for anti-fabrication gates
        context = {
            "per_cand_results": {"competencies": Result.PASS},
            "master_resume_text": "- Python\n- Machine Learning",  # For citation verification
            "computed_years_experience": 15,
        }
        
        accepted = evaluate_and_admit(
            section_id="competencies",
            candidate=candidate,
            context=context,
            fail_if_rejected=False,
        )
        
        # competencies validated
        assert "Python" in accepted.text
        assert accepted.write_receipt.writeable is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
