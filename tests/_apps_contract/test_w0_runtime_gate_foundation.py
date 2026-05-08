"""W0 — Runtime Gate Foundation Tests.

Verifies the fused RuntimeGateEngine authority foundation:
- GateDefinition, GateVerdict, JudgeVerdict contracts
- GateBundle aggregation
- WriteAdmissionGuard authority
- RuntimeGateEngine execution
- apps_rg gate pack registration

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W0)
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import (
    GateDefinition,
    GateEnforcement,
    GatePlacement,
    GateVerdict,
    JudgeVerdict,
    GateBundle,
    WriteAdmissionGuard,
    WriteAdmissionReceipt,
    RuntimeGateEngine,
)
from agentic_core.runtime_gates.builtins.candidate_acceptance_guard import (
    CandidateAcceptanceGuard,
    candidate_acceptance_guard_callable,
)
from apps_rg.integrations.gates.registry import (
    RESUME_GATE_DEFINITIONS,
    register_apps_rg_gate_pack,
)


class TestGateContracts:
    """Test core gate contract dataclasses."""

    def test_gate_definition_creation(self) -> None:
        """GateDefinition requires gate_id, placement, enforcement."""
        gd = GateDefinition(
            gate_id="test_gate",
            placement=GatePlacement.PER_CAND,
            enforcement=GateEnforcement.FAIL_CLOSED,
        )
        assert gd.gate_id == "test_gate"
        assert gd.placement == GatePlacement.PER_CAND
        assert gd.enforcement == GateEnforcement.FAIL_CLOSED
        assert gd.bypassable is False  # default

    def test_gate_verdict_blocking(self) -> None:
        """GateVerdict.is_blocking respects enforcement."""
        fail_closed = GateEnforcement.FAIL_CLOSED
        warn = GateEnforcement.WARN

        fail_verdict = GateVerdict("g1", Result.FAIL)
        unknown_verdict = GateVerdict("g1", Result.UNKNOWN)
        pass_verdict = GateVerdict("g1", Result.PASS)

        assert fail_verdict.is_blocking(fail_closed) is True
        assert unknown_verdict.is_blocking(fail_closed) is True
        assert pass_verdict.is_blocking(fail_closed) is False
        assert fail_verdict.is_blocking(warn) is False  # WARN doesn't block

    def test_judge_verdict_to_gate_verdict(self) -> None:
        """JudgeVerdict normalizes to GateVerdict."""
        jv = JudgeVerdict(
            judge_id="narrative_judge",
            judge_version="1.0.0",
            rubric_version="2.0.0",
            threshold_profile_id="default",
            gate_id="length_parity",
            placement=GatePlacement.PER_CAND,
            score=0.85,
            accepted=True,
            result=Result.PASS,
        )
        gv = jv.to_gate_verdict()
        assert gv.gate_id == "length_parity"
        assert gv.result == Result.PASS
        assert "narrative_judge" in gv.reason

    def test_judge_verdict_requires_versions(self) -> None:
        """JudgeVerdict requires judge_version, rubric_version, threshold_profile_id."""
        with pytest.raises(ValueError, match="judge_version"):
            JudgeVerdict(
                judge_id="test",
                judge_version="",  # Missing
                rubric_version="1.0.0",
                threshold_profile_id="default",
                gate_id="g1",
                placement=GatePlacement.PER_CAND,
            )


class TestGateBundle:
    """Test GateBundle aggregation."""

    def test_bundle_from_verdicts_computes_overall(self) -> None:
        """GateBundle.from_verdicts computes overall_result correctly."""
        verdicts = [
            GateVerdict("g1", Result.PASS),
            GateVerdict("g2", Result.PASS),
        ]
        bundle = GateBundle.from_verdicts("apps_rg", GatePlacement.PER_CAND, verdicts)
        assert bundle.overall_result == Result.PASS

    def test_bundle_fail_priority(self) -> None:
        """FAIL > UNKNOWN > WARN > PASS in overall_result."""
        verdicts = [
            GateVerdict("g1", Result.PASS),
            GateVerdict("g2", Result.WARN),
            GateVerdict("g3", Result.FAIL),
        ]
        bundle = GateBundle.from_verdicts("apps_rg", GatePlacement.PER_CAND, verdicts)
        assert bundle.overall_result == Result.FAIL

    def test_bundle_unknown_priority(self) -> None:
        """UNKNOWN > WARN > PASS when no FAIL."""
        verdicts = [
            GateVerdict("g1", Result.PASS),
            GateVerdict("g2", Result.UNKNOWN),
            GateVerdict("g3", Result.WARN),
        ]
        bundle = GateBundle.from_verdicts("apps_rg", GatePlacement.PER_CAND, verdicts)
        assert bundle.overall_result == Result.UNKNOWN

    def test_has_critical_failure(self) -> None:
        """has_critical_failure detects non-bypassable FAIL_CLOSED failures."""
        gate_defs = {
            "fail_closed_gate": GateDefinition(
                "fail_closed_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED, bypassable=False
            ),
            "bypassable_gate": GateDefinition(
                "bypassable_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED, bypassable=True
            ),
        }
        verdicts = [GateVerdict("fail_closed_gate", Result.FAIL)]
        bundle = GateBundle.from_verdicts("apps_rg", GatePlacement.PER_CAND, verdicts)
        assert bundle.has_critical_failure(gate_defs) is True

    def test_bypassable_gate_not_critical(self) -> None:
        """Bypassable gate with WARN enforcement doesn't trigger critical failure."""
        gate_defs = {
            "bypassable_gate": GateDefinition(
                "bypassable_gate", GatePlacement.PER_CAND, GateEnforcement.WARN, bypassable=True
            ),
        }
        verdicts = [GateVerdict("bypassable_gate", Result.FAIL)]
        bundle = GateBundle.from_verdicts("apps_rg", GatePlacement.PER_CAND, verdicts)
        # WARN enforcement doesn't block even on FAIL
        assert bundle.has_critical_failure(gate_defs) is False


class TestWriteAdmissionGuard:
    """Test WriteAdmissionGuard authority."""

    def test_allows_when_all_pass(self) -> None:
        """Write authorized when all gates pass."""
        gate_defs = {"g1": GateDefinition("g1", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED)}
        guard = WriteAdmissionGuard(gate_defs)
        
        bundle = GateBundle.from_verdicts(
            "apps_rg", GatePlacement.PER_CAND, [GateVerdict("g1", Result.PASS)]
        )
        receipt = guard.evaluate("exec_summary", bundle)
        
        assert receipt.writeable is True
        assert receipt.non_bypassable_gate_failed is False

    def test_denies_on_critical_failure(self) -> None:
        """Write denied when non-bypassable FAIL_CLOSED gate fails."""
        gate_defs = {
            "critical_gate": GateDefinition(
                "critical_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED, bypassable=False
            )
        }
        guard = WriteAdmissionGuard(gate_defs)
        
        bundle = GateBundle.from_verdicts(
            "apps_rg", GatePlacement.PER_CAND, [GateVerdict("critical_gate", Result.FAIL)]
        )
        receipt = guard.evaluate("exec_summary", bundle)
        
        assert receipt.writeable is False
        assert receipt.non_bypassable_gate_failed is True
        assert "candidate_rejected_by_per_cand_gate" in receipt.reason_codes

    def test_unknown_blocks_write(self) -> None:
        """UNKNOWN result blocks write for critical path."""
        gate_defs = {}
        guard = WriteAdmissionGuard(gate_defs)
        
        bundle = GateBundle(
            app_id="apps_rg",
            placement=GatePlacement.PER_CAND,
            verdicts=(),
            overall_result=Result.UNKNOWN,
        )
        receipt = guard.evaluate("exec_summary", bundle)
        
        assert receipt.writeable is False
        assert "unknown_verdict_blocks_write" in receipt.reason_codes


class TestRuntimeGateEngine:
    """Test RuntimeGateEngine execution."""

    def test_register_gate_pack(self) -> None:
        """Engine can register a gate pack."""
        engine = RuntimeGateEngine()
        
        def mock_gate(artifact, context):
            return GateVerdict("mock_gate", Result.PASS)
        
        engine.register_gate_pack(
            app_id="test_app",
            definitions=[GateDefinition("mock_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED)],
            callables={"mock_gate": mock_gate},
        )
        
        assert "test_app" in engine._gate_packs
        assert "mock_gate" in engine._all_definitions

    def test_evaluate_executes_gates(self) -> None:
        """Engine evaluates gates and produces GateBundle."""
        engine = RuntimeGateEngine()
        
        def pass_gate(artifact, context):
            return GateVerdict("pass_gate", Result.PASS)
        
        engine.register_gate_pack(
            app_id="test_app",
            definitions=[GateDefinition("pass_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED)],
            callables={"pass_gate": pass_gate},
        )
        
        bundle = engine.evaluate("test_app", GatePlacement.PER_CAND, "artifact", {})
        
        assert bundle.app_id == "test_app"
        assert bundle.placement == GatePlacement.PER_CAND
        assert bundle.overall_result == Result.PASS
        assert len(bundle.verdicts) == 1

    def test_evaluate_missing_callable(self) -> None:
        """Missing callable produces UNKNOWN verdict."""
        engine = RuntimeGateEngine()
        
        engine.register_gate_pack(
            app_id="test_app",
            definitions=[GateDefinition("missing_gate", GatePlacement.PER_CAND, GateEnforcement.FAIL_CLOSED)],
            callables={},  # No callable registered
        )
        
        bundle = engine.evaluate("test_app", GatePlacement.PER_CAND, "artifact", {})
        
        assert bundle.overall_result == Result.UNKNOWN
        assert bundle.verdicts[0].result == Result.UNKNOWN
        assert "missing_callable" in bundle.verdicts[0].reason_codes

    def test_evaluate_no_gate_pack(self) -> None:
        """No gate pack produces UNKNOWN bundle."""
        engine = RuntimeGateEngine()
        
        bundle = engine.evaluate("unknown_app", GatePlacement.PER_CAND, "artifact", {})
        
        assert bundle.overall_result == Result.UNKNOWN


class TestAppsRgGatePack:
    """Test apps_rg gate pack registration."""

    def test_resume_gate_definitions_count(self) -> None:
        """apps_rg has expected number of gate definitions."""
        assert len(RESUME_GATE_DEFINITIONS) == 20  # Current count from registry.py

    def test_register_apps_rg_gate_pack(self) -> None:
        """apps_rg gate pack registers with engine."""
        engine = RuntimeGateEngine()
        register_apps_rg_gate_pack(engine)
        
        assert "apps_rg" in engine._gate_packs
        assert "candidate_acceptance_guard" in engine._all_definitions
        assert "length_parity_strict" in engine._all_definitions

    def test_candidate_acceptance_guard_definition(self) -> None:
        """candidate_acceptance_guard is FAIL_CLOSED and non-bypassable."""
        guard_def = next(
            (d for d in RESUME_GATE_DEFINITIONS if d.gate_id == "candidate_acceptance_guard"),
            None
        )
        assert guard_def is not None
        assert guard_def.enforcement == GateEnforcement.FAIL_CLOSED
        assert guard_def.bypassable is False
        assert guard_def.placement == GatePlacement.POST_ENS


class TestCandidateAcceptanceGuard:
    """Test the core candidate acceptance guard."""

    def test_accepts_when_accepted_true(self) -> None:
        """Guard passes when artifact has accepted=True."""
        artifact = type("MockArtifact", (), {"accepted": True})()
        verdict = CandidateAcceptanceGuard.evaluate(artifact, {})
        
        assert verdict.result == Result.PASS
        assert "candidate_accepted" in verdict.reason_codes

    def test_rejects_when_accepted_false(self) -> None:
        """Guard fails when artifact has accepted=False."""
        artifact = type("MockArtifact", (), {"accepted": False})()
        verdict = CandidateAcceptanceGuard.evaluate(artifact, {})
        
        assert verdict.result == Result.FAIL
        assert "candidate_rejected_by_per_cand_gate" in verdict.reason_codes

    def test_rejects_on_per_cand_failure(self) -> None:
        """Guard fails when per_cand_results has failures."""
        artifact = type("MockArtifact", (), {"accepted": True})()
        context = {
            "per_cand_results": {
                "length_parity": Result.FAIL,
            }
        }
        verdict = CandidateAcceptanceGuard.evaluate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "length_parity" in verdict.reason_codes

    def test_unknown_when_accepted_none(self) -> None:
        """Guard returns UNKNOWN when acceptance status unknown."""
        artifact = type("MockArtifact", (), {"accepted": None})()
        verdict = CandidateAcceptanceGuard.evaluate(artifact, {})
        
        assert verdict.result == Result.UNKNOWN
        assert "unknown_acceptance_status" in verdict.reason_codes

    def test_callable_wrapper(self) -> None:
        """callable wrapper works with engine."""
        artifact = {"accepted": True}
        verdict = candidate_acceptance_guard_callable(artifact, {})
        assert verdict.result == Result.PASS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
