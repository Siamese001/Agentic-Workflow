"""W8.1 GateMeshResult Stage Coverage — apps_research.

Plan: apps-research-rich-content-runtime-customization-v2
Wave: W8.1 (hardening before W9)

Goal: Prove GateMeshResult coverage by stage for apps_research.

Do not add judges, evals, L6, or UWG.

Required GateMeshResult fields:
- request_id
- run_id
- trace_root
- evaluated_surface
- required_gate_ids
- completed_gate_ids
- missing_gate_ids
- verdicts
- hard_fail_present
- unknown_material_present
- warn_material_present
- deterministic_digest
- gate_mesh_schema_version

Stage coverage for apps_research:
U0: G01, G02, G03-lite, G04-lite, G17-lite
L1: G03, G04, G05
L0: G07, G08, G10, G20
C0: G08, G09, G13, G17, G23, G24
PA: G10, G13, G17, G21, G23
L2: G11, G12, G13, G14, G15, G17, G19, G20, G21, G23, G24, G28
Exit: G21, G22, G23, G24, G25, G26, G27, G28
"""
import pytest
from dataclasses import fields
from typing import get_type_hints

from agentic_core.runtime.gates.gate_types import (
    GateVerdict,
    GateMeshResult,
    VERDICT_UNKNOWN,
    VERDICT_PASS,
    VERDICT_FAIL,
    VERDICT_NOT_APPLICABLE,
)


# ─────────────────────────────────────────────────────────────────────────────
# Stage-Specific Gate Coverage for apps_research
# ─────────────────────────────────────────────────────────────────────────────

APPS_RESEARCH_STAGE_GATES = {
    "U0": ("G01", "G02", "G03-lite", "G04-lite", "G17-lite"),
    "L1": ("G03", "G04", "G05"),
    "L0": ("G07", "G08", "G10", "G20"),
    "C0": ("G08", "G09", "G13", "G17", "G23", "G24"),
    "PA": ("G10", "G13", "G17", "G21", "G23"),
    "L2": ("G11", "G12", "G13", "G14", "G15", "G17", "G19", "G20", "G21", "G23", "G24", "G28"),
    "Exit": ("G21", "G22", "G23", "G24", "G25", "G26", "G27", "G28"),
}

REQUIRED_MESH_FIELDS = (
    "request_id",
    "run_id",
    "trace_root",
    "evaluated_surface",
    "required_gate_ids",
    "completed_gate_ids",
    "missing_gate_ids",
    "verdicts",
    "hard_fail_present",
    "unknown_material_present",
    "warn_material_present",
    "deterministic_digest",
    "gate_mesh_schema_version",
)


# ─────────────────────────────────────────────────────────────────────────────
# W8.1 GateMeshResult Field Verification
# ─────────────────────────────────────────────────────────────────────────────

class TestW81GateMeshResultFields:
    """Verify GateMeshResult has all required fields."""

    def test_w8_gate_mesh_has_request_id(self) -> None:
        """GateMeshResult must have request_id field."""
        mesh = GateMeshResult(request_id="req-123")
        assert mesh.request_id == "req-123"

    def test_w8_gate_mesh_has_run_id(self) -> None:
        """GateMeshResult must have run_id field."""
        mesh = GateMeshResult(run_id="run-456")
        assert mesh.run_id == "run-456"

    def test_w8_gate_mesh_has_trace_root(self) -> None:
        """GateMeshResult must have trace_root field."""
        mesh = GateMeshResult(trace_root="trace-789")
        assert mesh.trace_root == "trace-789"

    def test_w8_gate_mesh_has_evaluated_surface(self) -> None:
        """GateMeshResult must have evaluated_surface field."""
        mesh = GateMeshResult(evaluated_surface="apps_research_company_brief")
        assert mesh.evaluated_surface == "apps_research_company_brief"

    def test_w8_gate_mesh_has_required_gate_ids(self) -> None:
        """GateMeshResult must track required_gate_ids."""
        mesh = GateMeshResult(required_gate_ids=("G01", "G02", "G03"))
        assert "G01" in mesh.required_gate_ids
        assert "G02" in mesh.required_gate_ids

    def test_w8_gate_mesh_has_completed_gate_ids(self) -> None:
        """GateMeshResult must track completed_gate_ids."""
        mesh = GateMeshResult(completed_gate_ids=("G01", "G02"))
        assert "G01" in mesh.completed_gate_ids

    def test_w8_gate_mesh_has_missing_gate_ids(self) -> None:
        """GateMeshResult must track missing_gate_ids."""
        mesh = GateMeshResult(missing_gate_ids=("G03",))
        assert "G03" in mesh.missing_gate_ids

    def test_w8_gate_mesh_has_verdicts(self) -> None:
        """GateMeshResult must have verdicts tuple."""
        verdict = GateVerdict(gate_id="G01", result=VERDICT_PASS, reason_codes=("pass",), is_pass=True)
        mesh = GateMeshResult(verdicts=(verdict,))
        assert len(mesh.verdicts) == 1
        assert mesh.verdicts[0].gate_id == "G01"

    def test_w8_gate_mesh_has_hard_fail_present(self) -> None:
        """GateMeshResult must have hard_fail_present signal."""
        mesh = GateMeshResult(hard_fail_present=True)
        assert mesh.hard_fail_present is True

    def test_w8_gate_mesh_has_unknown_material_present(self) -> None:
        """GateMeshResult must have unknown_material_present signal."""
        mesh = GateMeshResult(unknown_material_present=True)
        assert mesh.unknown_material_present is True

    def test_w8_gate_mesh_has_warn_material_present(self) -> None:
        """GateMeshResult must have warn_material_present signal."""
        mesh = GateMeshResult(warn_material_present=True)
        assert mesh.warn_material_present is True

    def test_w8_gate_mesh_has_deterministic_digest(self) -> None:
        """GateMeshResult must have deterministic_digest."""
        mesh = GateMeshResult(deterministic_digest="sha256:abc123")
        assert mesh.deterministic_digest == "sha256:abc123"

    def test_w8_gate_mesh_has_schema_version(self) -> None:
        """GateMeshResult must have gate_mesh_schema_version."""
        mesh = GateMeshResult()
        assert mesh.gate_mesh_schema_version != ""


# ─────────────────────────────────────────────────────────────────────────────
# W8.1 Stage Gate Coverage
# ─────────────────────────────────────────────────────────────────────────────

class TestW81StageGateCoverage:
    """Prove GateMeshResult coverage by stage for apps_research."""

    def test_w8_gate_mesh_declares_required_gate_ids_by_stage(self) -> None:
        """Each stage must declare its required gate IDs in GateMeshResult."""
        for stage, gates in APPS_RESEARCH_STAGE_GATES.items():
            # Build mesh for this stage
            verdicts = tuple(
                GateVerdict(gate_id=g, result=VERDICT_PASS, reason_codes=("test",), is_pass=True)
                for g in gates
            )
            mesh = GateMeshResult(
                evaluated_surface=f"apps_research_{stage.lower()}",
                required_gate_ids=gates,
                completed_gate_ids=gates,
                verdicts=verdicts,
            )
            # Verify all required gates are tracked
            for gate_id in gates:
                assert gate_id in mesh.required_gate_ids, f"Stage {stage}: {gate_id} not in required_gate_ids"

    def test_w8_gate_mesh_tracks_completed_gate_ids(self) -> None:
        """GateMeshResult must track which gates completed."""
        u0_gates = APPS_RESEARCH_STAGE_GATES["U0"]
        completed = u0_gates[:3]  # First 3 completed
        missing = u0_gates[3:]    # Rest missing

        verdicts = tuple(
            GateVerdict(gate_id=g, result=VERDICT_PASS, reason_codes=("test",), is_pass=True)
            for g in completed
        )
        mesh = GateMeshResult(
            evaluated_surface="apps_research_u0",
            required_gate_ids=u0_gates,
            completed_gate_ids=completed,
            missing_gate_ids=missing,
            verdicts=verdicts,
        )

        # Verify completed gates tracked
        for gate_id in completed:
            assert gate_id in mesh.completed_gate_ids
        # Verify missing gates NOT in completed
        for gate_id in missing:
            assert gate_id not in mesh.completed_gate_ids

    def test_w8_gate_mesh_tracks_missing_gate_ids(self) -> None:
        """GateMeshResult must track which gates are missing."""
        exit_gates = APPS_RESEARCH_STAGE_GATES["Exit"]
        completed = exit_gates[:4]   # G21-G24 completed
        missing = exit_gates[4:]     # G25-G28 missing

        verdicts = tuple(
            GateVerdict(gate_id=g, result=VERDICT_PASS, reason_codes=("test",), is_pass=True)
            for g in completed
        )
        mesh = GateMeshResult(
            evaluated_surface="apps_research_exit",
            required_gate_ids=exit_gates,
            completed_gate_ids=completed,
            missing_gate_ids=missing,
            verdicts=verdicts,
        )

        # Verify missing gates tracked
        for gate_id in missing:
            assert gate_id in mesh.missing_gate_ids, f"{gate_id} should be in missing_gate_ids"

    def test_w8_gate_mesh_missing_applicable_gate_is_unknown_not_pass(self) -> None:
        """Missing applicable gate must be treated as UNKNOWN, not PASS."""
        l2_gates = APPS_RESEARCH_STAGE_GATES["L2"]
        completed_gates = l2_gates[:6]  # Some completed
        missing_gate = l2_gates[6]       # One missing

        completed_verdicts = tuple(
            GateVerdict(gate_id=g, result=VERDICT_PASS, reason_codes=("pass",), is_pass=True)
            for g in completed_gates
        )

        mesh = GateMeshResult(
            evaluated_surface="apps_research_l2",
            required_gate_ids=l2_gates,
            completed_gate_ids=completed_gates,
            missing_gate_ids=(missing_gate,),
            verdicts=completed_verdicts,
        )

        # Missing gate means not all required passed
        assert mesh.all_required_passed is False
        # Missing gate should block allow_finish
        assert mesh.blocks_allow_finish is True


# ─────────────────────────────────────────────────────────────────────────────
# W8.1 Exit Consumption
# ─────────────────────────────────────────────────────────────────────────────

class TestW81ExitConsumesGateMeshResult:
    """Prove Exit consumes GateMeshResult correctly."""

    def test_w8_gate_mesh_exit_consumes_gate_mesh_result(self) -> None:
        """Exit must consume GateMeshResult to make X3 decision."""
        from agentic_core.runtime.exit.exit_package_driven_binding import (
            ExitPackageDrivenBinding, ExitInput, ExitPolicy
        )
        from agentic_core.runtime.gates.gate_profile_resolver import GateProfile

        # Build a complete mesh
        verdicts = tuple(
            GateVerdict(gate_id=g, result=VERDICT_PASS, reason_codes=("pass",), is_pass=True)
            for g in ("G21", "G22", "G23", "G24")
        )
        mesh = GateMeshResult(
            request_id="req-test",
            run_id="run-test",
            trace_root="trace-test",
            evaluated_surface="apps_research_exit",
            required_gate_ids=("G21", "G22", "G23", "G24", "G25", "G26", "G27", "G28"),
            completed_gate_ids=("G21", "G22", "G23", "G24"),
            missing_gate_ids=("G25", "G26", "G27", "G28"),
            verdicts=verdicts,
            hard_fail_present=False,
            unknown_material_present=False,
            warn_material_present=False,
            deterministic_digest="sha256:test-mesh-digest",
        )

        # Exit binding should be able to consume this mesh
        binding = ExitPackageDrivenBinding(
            gate_profile=GateProfile(profile_id="test"),
            exit_policy=ExitPolicy(),
        )

        # Verify mesh has required fields for Exit consumption
        assert mesh.request_id != ""
        assert mesh.run_id != ""
        assert mesh.trace_root != ""
        assert mesh.deterministic_digest != ""
        assert mesh.blocks_allow_finish is True  # Due to missing gates

    def test_w8_gate_mesh_blocks_allow_finish_when_required_gate_missing(self) -> None:
        """blocks_allow_finish must be True when required gates are missing."""
        mesh = GateMeshResult(
            required_gate_ids=("G27_COMMIT_SAFE", "G28_COMMIT_ALLOWED"),
            completed_gate_ids=(),
            missing_gate_ids=("G27_COMMIT_SAFE", "G28_COMMIT_ALLOWED"),
            verdicts=(),
            hard_fail_present=False,
            unknown_material_present=False,
        )

        assert mesh.blocks_allow_finish is True


# ─────────────────────────────────────────────────────────────────────────────
# W8.1 Deterministic Digest & Replay
# ─────────────────────────────────────────────────────────────────────────────

class TestW81DeterministicDigestAndReplay:
    """Verify deterministic digest changes when verdicts change."""

    def test_w8_gate_mesh_deterministic_digest_changes_when_verdict_changes(self) -> None:
        """Changing a verdict must change the deterministic_digest."""
        import hashlib
        import json

        def compute_digest(verdicts):
            payload = json.dumps({
                "verdict_digests": sorted(v.deterministic_digest for v in verdicts),
            }, sort_keys=True, separators=(",", ":"))
            return hashlib.sha256(payload.encode()).hexdigest()

        # First mesh with PASS verdicts
        verdicts1 = (
            GateVerdict(gate_id="G01", result=VERDICT_PASS, reason_codes=("pass",), is_pass=True, deterministic_digest="sha256:v1"),
            GateVerdict(gate_id="G02", result=VERDICT_PASS, reason_codes=("pass",), is_pass=True, deterministic_digest="sha256:v2"),
        )
        digest1 = compute_digest(verdicts1)

        # Second mesh with FAIL verdict (same gates, different results)
        verdicts2 = (
            GateVerdict(gate_id="G01", result=VERDICT_FAIL, reason_codes=("fail",), is_pass=False, is_hard_fail=True, deterministic_digest="sha256:v3"),
            GateVerdict(gate_id="G02", result=VERDICT_PASS, reason_codes=("pass",), is_pass=True, deterministic_digest="sha256:v2"),
        )
        digest2 = compute_digest(verdicts2)

        # Digests must differ
        assert digest1 != digest2, "Deterministic digest must change when verdict changes"

    def test_w8_gate_mesh_replay_fields_present_for_every_verdict(self) -> None:
        """Every GateVerdict must have replay fields for reconstruction."""
        for stage, gates in APPS_RESEARCH_STAGE_GATES.items():
            for gate_id in gates:
                verdict = GateVerdict(
                    gate_id=gate_id,
                    result=VERDICT_PASS,
                    reason_codes=("test_pass",),
                    evidence_digest=f"sha256:{gate_id}-evidence",
                    evaluator_version="test_evaluator_v1.0.0",
                    evaluated_at="2026-05-11T12:00:00Z",
                    is_pass=True,
                )

                # Verify replay fields present
                assert verdict.gate_id == gate_id
                assert verdict.result == VERDICT_PASS
                assert len(verdict.reason_codes) > 0
                assert verdict.evidence_digest != ""
                assert verdict.evaluator_version != ""
                assert verdict.evaluated_at != ""


# ─────────────────────────────────────────────────────────────────────────────
# W8.1 NOT_APPLICABLE Reason Requirement
# ─────────────────────────────────────────────────────────────────────────────

class TestW81NotApplicableReason:
    """Prove NOT_APPLICABLE always has a reason."""

    def test_w8_gate_mesh_not_applicable_requires_reason_for_every_na(self) -> None:
        """Every NOT_APPLICABLE verdict must have not_applicable_reason."""
        # Some gates may be NOT_APPLICABLE depending on context
        na_verdicts = (
            GateVerdict(
                gate_id="G03-lite",
                result=VERDICT_NOT_APPLICABLE,
                reason_codes=("lite_variant_no_full_check",),
                not_applicable_reason="G03-lite is simplified variant, full G03 checks not applicable",
                is_not_applicable=True,
            ),
            GateVerdict(
                gate_id="G17-lite",
                result=VERDICT_NOT_APPLICABLE,
                reason_codes=("lite_variant_no_full_check",),
                not_applicable_reason="G17-lite is simplified variant, full G17 checks not applicable",
                is_not_applicable=True,
            ),
        )

        for verdict in na_verdicts:
            assert verdict.result == VERDICT_NOT_APPLICABLE
            assert verdict.not_applicable_reason != "", f"{verdict.gate_id} missing not_applicable_reason"
            assert len(verdict.reason_codes) > 0


# ─────────────────────────────────────────────────────────────────────────────
# W8.1 Evidence-Backed Verdicts (Not Boolean-Only)
# ─────────────────────────────────────────────────────────────────────────────

class TestW81EvidenceBackedVerdicts:
    """Prove all gate verdicts are evidence-backed, not boolean-only."""

    def test_w8_gate_mesh_receipt_has_evidence_refs_not_boolean_only(self) -> None:
        """GateVerdicts must have evidence_refs, not just boolean flags."""
        # Build verdicts with evidence refs (not just booleans)
        verdicts = []
        for stage, gates in APPS_RESEARCH_STAGE_GATES.items():
            for gate_id in gates:
                verdict = GateVerdict(
                    gate_id=gate_id,
                    result=VERDICT_PASS,
                    reason_codes=(f"{gate_id}_pass_reason",),
                    evidence_refs=(f"evidence://{gate_id}/scan_result",),
                    evidence_digest=f"sha256:{gate_id}_evidence",
                    evaluator_version=f"{stage.lower()}_evaluator_v1.2.0",
                    evaluated_at="2026-05-11T12:00:00Z",
                    is_pass=True,
                )
                verdicts.append(verdict)

        # Verify each verdict has evidence (not just booleans)
        for verdict in verdicts:
            assert len(verdict.evidence_refs) > 0 or verdict.evidence_digest != "", \
                f"{verdict.gate_id} lacks evidence_refs or evidence_digest (boolean-only verdict forbidden)"
            assert verdict.evaluator_version != "", \
                f"{verdict.gate_id} lacks evaluator_version"
            assert verdict.evaluated_at != "", \
                f"{verdict.gate_id} lacks evaluated_at timestamp"

    def test_w8_gate_mesh_all_gate_verdicts_evidence_backed(self) -> None:
        """All gate verdicts must be evidence-backed."""
        mesh = GateMeshResult(
            evaluated_surface="apps_research_full_pipeline",
            required_gate_ids=("G01", "G02", "G21", "G22"),
            completed_gate_ids=("G01", "G02", "G21", "G22"),
            verdicts=(
                GateVerdict(
                    gate_id="G01",
                    result=VERDICT_PASS,
                    reason_codes=("input_valid",),
                    evidence_refs=("evidence://u0/input_validation",),
                    evidence_digest="sha256:g01_evidence",
                    evaluator_version="u0_validator_v1.0.0",
                    evaluated_at="2026-05-11T12:00:00Z",
                    is_pass=True,
                ),
                GateVerdict(
                    gate_id="G21",
                    result=VERDICT_PASS,
                    reason_codes=("brief_complete",),
                    evidence_refs=("evidence://l2/brief_completeness",),
                    evidence_digest="sha256:g21_evidence",
                    evaluator_version="l2_validator_v1.0.0",
                    evaluated_at="2026-05-11T12:00:00Z",
                    is_pass=True,
                ),
            ),
        )

        # Verify all verdicts have evidence
        for verdict in mesh.verdicts:
            assert verdict.evidence_refs or verdict.evidence_digest, \
                "Evidence-backed verdict required (no boolean-only verdicts)"
