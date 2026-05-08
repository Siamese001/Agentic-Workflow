"""W2 — Online Judge Contract Binding Tests.

Verifies the W2 Online Judge Runtime Contract:
- JudgeVerdict normalization to core contract
- Required fields: judge_id, judge_version, rubric_version, threshold_profile_id
- Judges evaluate but do not authorize writes
- Malformed verdicts normalize to UNKNOWN
- Runtime normalization into GateVerdicts

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W2)
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import Any, Dict, List

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates.definitions import (
    JudgeVerdict as CoreJudgeVerdict,
    GatePlacement,
)

from apps_eval.engines.narrative_judge_scorer import JudgeVerdict as NarrativeJudgeVerdict

from apps_rg.integrations.gates.online_judges import (
    NARRATIVE_JUDGE_ID,
    NARRATIVE_JUDGE_VERSION,
    DEFAULT_RUBRIC_VERSION,
    DEFAULT_THRESHOLD_PROFILE_ID,
    JudgeRuntimeContext,
    normalize_narrative_judge_verdict,
    OnlineJudgeContractValidator,
    judge_verdict_to_gate_bundle_entry,
)
from apps_rg.integrations.gates.narrative_integration import (
    evaluate_with_online_judge,
    get_judge_provenance,
)


# Mock GateResult for testing
@dataclass
class MockGateResult:
    gate_id: str
    passed: bool
    detail: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {"gate_id": self.gate_id, "passed": self.passed, "detail": self.detail}


class TestJudgeVerdictNormalization:
    """Test normalization of narrative judge verdicts to core contract."""

    def test_normalize_accepted_verdict(self) -> None:
        """Accepted narrative verdict normalizes to PASS."""
        narrative_verdict = NarrativeJudgeVerdict(
            accepted=True,
            composite=0.92,
            hard_gates=[MockGateResult("length", True), MockGateResult("buzzword", True)],
            soft_scores={"tone": 0.9},
        )
        context = JudgeRuntimeContext(
            section_id="executive_summary",
            rubric_version="2.1.0",
            threshold_profile_id="strict",
        )

        core_verdict = normalize_narrative_judge_verdict(narrative_verdict, context)

        assert core_verdict.judge_id == NARRATIVE_JUDGE_ID
        assert core_verdict.judge_version == NARRATIVE_JUDGE_VERSION
        assert core_verdict.rubric_version == "2.1.0"
        assert core_verdict.threshold_profile_id == "strict"
        assert core_verdict.result == Result.PASS
        assert core_verdict.accepted is True
        assert core_verdict.score == 0.92

    def test_normalize_rejected_verdict_hard_gate_fail(self) -> None:
        """Rejected verdict (hard gate fail) normalizes to FAIL."""
        narrative_verdict = NarrativeJudgeVerdict(
            accepted=False,
            composite=0.95,
            hard_gates=[
                MockGateResult("length", False, "too short"),
                MockGateResult("buzzword", True),
            ],
            soft_scores={"tone": 0.9},
        )
        context = JudgeRuntimeContext(section_id="executive_summary")

        core_verdict = normalize_narrative_judge_verdict(narrative_verdict, context)

        assert core_verdict.result == Result.FAIL
        assert core_verdict.accepted is False
        assert "hard_gate_fail:length" in core_verdict.reason_codes
        assert "length" in core_verdict.reason_codes

    def test_normalize_rejected_verdict_low_composite(self) -> None:
        """Rejected verdict (low composite, gates passed) normalizes to WARN."""
        narrative_verdict = NarrativeJudgeVerdict(
            accepted=False,
            composite=0.72,
            hard_gates=[MockGateResult("length", True)],
            soft_scores={"tone": 0.6},
        )
        context = JudgeRuntimeContext(section_id="executive_summary")

        core_verdict = normalize_narrative_judge_verdict(narrative_verdict, context)

        # Composite below threshold but gates passed → WARN (not FAIL)
        assert core_verdict.result == Result.WARN
        assert core_verdict.accepted is False

    def test_deterministic_digest_generation(self) -> None:
        """Normalized verdicts include deterministic digest."""
        narrative_verdict = NarrativeJudgeVerdict(
            accepted=True,
            composite=0.85,
        )
        context = JudgeRuntimeContext(section_id="headline")

        core_verdict = normalize_narrative_judge_verdict(narrative_verdict, context)

        assert core_verdict.deterministic_digest != ""
        assert len(core_verdict.deterministic_digest) == 16

    def test_digest_changes_with_input(self) -> None:
        """Digest changes when inputs change."""
        v1 = NarrativeJudgeVerdict(accepted=True, composite=0.85)
        v2 = NarrativeJudgeVerdict(accepted=True, composite=0.86)
        context = JudgeRuntimeContext(section_id="headline")

        d1 = normalize_narrative_judge_verdict(v1, context).deterministic_digest
        d2 = normalize_narrative_judge_verdict(v2, context).deterministic_digest

        assert d1 != d2


class TestOnlineJudgeContractValidator:
    """Test the Online Judge Contract Validator."""

    def test_valid_verdict_passes(self) -> None:
        """Valid verdict passes validation."""
        verdict = CoreJudgeVerdict(
            judge_id="test_judge",
            judge_version="1.0.0",
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="test_gate",
            placement=GatePlacement.PER_CAND,
            score=0.85,
        )

        is_valid, errors = OnlineJudgeContractValidator.validate(verdict)

        assert is_valid is True
        assert errors == []

    def test_validator_checks_all_required_fields(self) -> None:
        """Validator checks all required fields."""
        # Since CoreJudgeVerdict validates in __post_init__, test validator logic directly
        # by checking the REQUIRED_FIELDS set
        required = OnlineJudgeContractValidator.REQUIRED_FIELDS

        assert "judge_id" in required
        assert "judge_version" in required
        assert "rubric_version" in required
        assert "threshold_profile_id" in required
        assert "gate_id" in required

    def test_score_out_of_range_raises_in_init(self) -> None:
        """Score outside [0,1] raises ValueError in __post_init__."""
        with pytest.raises(ValueError, match="score must be in \\[0,1\\]"):
            CoreJudgeVerdict(
                judge_id="test",
                judge_version="1.0.0",
                rubric_version="2.0.0",
                threshold_profile_id="default",
                gate_id="test_gate",
                placement=GatePlacement.PER_CAND,
                score=1.5,  # Out of range
            )

    def test_invalid_version_format_fails(self) -> None:
        """Non-semver version format fails validation."""
        verdict = CoreJudgeVerdict(
            judge_id="test",
            judge_version="invalid",  # Not semver
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="test_gate",
            placement=GatePlacement.PER_CAND,
        )

        is_valid, errors = OnlineJudgeContractValidator.validate(verdict)

        assert is_valid is False
        assert any("invalid_version_format" in e for e in errors)

    def test_normalize_or_unknown_returns_unknown_for_invalid(self) -> None:
        """Invalid verdict normalizes to UNKNOWN result."""
        context = JudgeRuntimeContext(section_id="test")

        result = OnlineJudgeContractValidator.normalize_or_unknown(None, context)

        assert result.result == Result.UNKNOWN
        assert result.accepted is False
        assert "null_verdict" in result.reason_codes

    def test_normalize_or_unknown_returns_original_for_valid(self) -> None:
        """Valid verdict is returned unchanged."""
        verdict = CoreJudgeVerdict(
            judge_id="test",
            judge_version="1.0.0",
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="test_gate",
            placement=GatePlacement.PER_CAND,
            score=0.85,
        )
        context = JudgeRuntimeContext(section_id="test")

        result = OnlineJudgeContractValidator.normalize_or_unknown(verdict, context)

        assert result is verdict  # Same object returned


class TestGateBundleEntry:
    """Test conversion to gate bundle entry format."""

    def test_judge_verdict_to_bundle_entry(self) -> None:
        """Core verdict converts to bundle entry dict."""
        verdict = CoreJudgeVerdict(
            judge_id="narrative_judge",
            judge_version="1.0.0",
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="exec_summary_judge",
            placement=GatePlacement.PER_CAND,
            score=0.88,
            accepted=True,
            result=Result.PASS,
            reason_codes=("gate_pass",),
            evidence_refs=("section:exec_summary",),
            deterministic_digest="abc123",
        )

        entry = judge_verdict_to_gate_bundle_entry(verdict)

        assert entry["gate_id"] == "exec_summary_judge"
        assert entry["judge_id"] == "narrative_judge"
        assert entry["score"] == 0.88
        assert entry["accepted"] is True
        assert entry["result"] == "PASS"
        assert entry["deterministic_digest"] == "abc123"


class TestJudgeProvenance:
    """Test judge provenance reporting."""

    def test_get_judge_provenance(self) -> None:
        """Provenance includes all required W2 contract fields."""
        provenance = get_judge_provenance("executive_summary")

        assert provenance["judge_id"] == NARRATIVE_JUDGE_ID
        assert provenance["judge_version"] == NARRATIVE_JUDGE_VERSION
        assert provenance["rubric_version"] == DEFAULT_RUBRIC_VERSION
        assert provenance["threshold_profile_id"] == DEFAULT_THRESHOLD_PROFILE_ID
        assert provenance["section_id"] == "executive_summary"
        assert provenance["contract_version"] == "W2.0"


class TestRuntimeNormalization:
    """Test runtime normalization into GateVerdict for engine aggregation."""

    def test_normalized_verdict_converts_to_gate_verdict(self) -> None:
        """Normalized JudgeVerdict converts to GateVerdict via to_gate_verdict."""
        narrative_verdict = NarrativeJudgeVerdict(
            accepted=True,
            composite=0.90,
            hard_gates=[MockGateResult("length", True)],
        )
        context = JudgeRuntimeContext(
            section_id="executive_summary",
            gate_id="exec_summary_judge",
        )

        core_verdict = normalize_narrative_judge_verdict(narrative_verdict, context)
        gate_verdict = core_verdict.to_gate_verdict()

        assert gate_verdict.gate_id == "exec_summary_judge"
        assert gate_verdict.result == Result.PASS
        assert "narrative_judge_scorer" in gate_verdict.reason
        assert "judge:narrative_judge_scorer" in gate_verdict.evidence_refs


class TestJudgesDoNotAuthorizeWrites:
    """P0 contract test: judges evaluate but do not authorize writes."""

    def test_judge_verdict_has_no_write_authority(self) -> None:
        """Judge verdicts contain no write authorization field."""
        # JudgeVerdict only has evaluation fields, not write authority
        verdict = CoreJudgeVerdict(
            judge_id="test",
            judge_version="1.0.0",
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="test_gate",
            placement=GatePlacement.PER_CAND,
            accepted=True,
        )

        # No writeable field in JudgeVerdict
        assert not hasattr(verdict, "writeable")
        assert not hasattr(verdict, "write_authorized")

    def test_write_authority_in_gate_bundle_and_guard(self) -> None:
        """Write authority lives in GateBundle + WriteAdmissionGuard, not judge."""
        from agentic_core.runtime_gates import GateBundle, WriteAdmissionGuard
        from agentic_core.runtime_gates.definitions import GateDefinition, GateEnforcement

        # Judge produces verdict
        judge_verdict = CoreJudgeVerdict(
            judge_id="judge",
            judge_version="1.0.0",
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="gate",
            placement=GatePlacement.PER_CAND,
            accepted=True,
            result=Result.PASS,
        ).to_gate_verdict()

        # GateBundle aggregates
        bundle = GateBundle.from_verdicts("apps_rg", GatePlacement.PER_CAND, [judge_verdict])
        assert bundle.overall_result == Result.PASS

        # WriteAdmissionGuard authorizes
        guard = WriteAdmissionGuard({
            "gate": GateDefinition("gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED)
        })
        receipt = guard.evaluate("section", bundle, {})

        # Guard decides writeability, not judge
        assert receipt.writeable is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
