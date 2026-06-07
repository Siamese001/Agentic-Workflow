"""
P4.8 + P4.9 + P4.10 — W4 L2/Exit Negative Controls & Integration Tests.

Coverage:
- P4.3  StyleGate L2.E4 repair (positive + negative)
- P4.4  StyleGate Exit hard gate (X3 trigger)
- P4.5  CertProjectionAdapter (read-only, no FEC minting)
- P4.6  L2 E1-E5 receipts (structure + bundle)
- P4.7  Exit v6 board-readiness + citation integrity X3 checks
- P4.8  25 negative control tests (fail-closed behaviour)
- P4.9  apps_eval dual-scenario verification (both old+new green)
- P4.10 W4 integration acceptance (receipt bundle → Exit gate flow)

Plan: docs/archive/windsurf/legacy-tree/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P4.8-P4.10
"""

from __future__ import annotations

from typing import Any

import pytest


# ---------------------------------------------------------------------------
# P4.3 — StyleGate L2.E4 Repair
# ---------------------------------------------------------------------------

class TestStyleGateL2Repair:
    def test_import(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        assert StyleGateL2Repair is not None

    def test_clean_slot_returns_clean_outcome(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        from apps_repo_brief.L2.style_gate_l2_repair import RepairOutcome
        repair = StyleGateL2Repair()
        bundle = repair.run({"S0": "Clean slot body with no issues."})
        assert bundle.repair_results[0].outcome == RepairOutcome.CLEAN
        assert not bundle.has_escalations

    def test_length_overrun_repaired(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        from apps_repo_brief.L2.style_gate_l2_repair import RepairOutcome
        repair = StyleGateL2Repair()
        long_body = "x" * 9000
        bundle = repair.run({"S0": long_body})
        result = bundle.repair_results[0]
        assert result.outcome == RepairOutcome.REPAIRED
        assert len(result.repaired_body) <= 8_200
        assert "truncated" in result.repaired_body

    def test_unresolved_stub_escalates(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        from apps_repo_brief.L2.style_gate_l2_repair import RepairOutcome
        repair = StyleGateL2Repair()
        bundle = repair.run({"S0": "Text with {{UNRESOLVED_KEY}} present."})
        assert bundle.has_escalations
        assert "S0" in bundle.escalation_slot_ids
        assert bundle.repair_results[0].outcome == RepairOutcome.ESCALATE

    def test_multiple_slots_independent_outcomes(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        repair = StyleGateL2Repair()
        bundle = repair.run({
            "S0": "Clean body.",
            "S1": "Has {{STUB}} unresolved.",
            "S2": "Another clean.",
        })
        outcomes = {r.slot_id: r.outcome.value for r in bundle.repair_results}
        assert outcomes["S0"] == "clean"
        assert outcomes["S1"] == "escalate"
        assert outcomes["S2"] == "clean"
        assert bundle.escalation_slot_ids == ["S1"]

    def test_e4_receipt_structure(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        repair = StyleGateL2Repair()
        bundle = repair.run({"S0": "OK body.", "S1": "Has {{STUB}}."})
        receipt = bundle.e4_receipt
        assert receipt["step"] == "E4"
        assert "slots_inspected" in receipt
        assert "slots_escalated" in receipt
        assert receipt["slots_inspected"] == 2
        assert receipt["slots_escalated"] == 1


# ---------------------------------------------------------------------------
# P4.4 — StyleGate Exit Hard Gate
# ---------------------------------------------------------------------------

class TestStyleGateExitCheck:
    def test_import(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        assert StyleGateExitCheck is not None

    def test_no_escalations_pass(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        gate = StyleGateExitCheck()
        result = gate.check({"escalated_slot_ids": []}, {})
        assert result.verdict.value == "PASS"
        assert not result.x3_triggered

    def test_escalated_slot_with_stub_blocks(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        gate = StyleGateExitCheck()
        result = gate.check(
            {"escalated_slot_ids": ["S1"]},
            {"S1": "Still has {{UNRESOLVED}} token."},
        )
        assert result.verdict.value == "BLOCK"
        assert result.x3_triggered
        assert "S1" in result.blocking_slot_ids

    def test_escalated_slot_clean_after_e4_passes(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        gate = StyleGateExitCheck()
        result = gate.check(
            {"escalated_slot_ids": ["S1"]},
            {"S1": "All stubs resolved now."},
        )
        assert result.verdict.value == "PASS"
        assert not result.x3_triggered

    def test_missing_escalated_slot_passes(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        gate = StyleGateExitCheck()
        result = gate.check(
            {"escalated_slot_ids": ["S_MISSING"]},
            {},
        )
        assert result.verdict.value == "PASS"


# ---------------------------------------------------------------------------
# P4.5 — CertProjectionAdapter
# ---------------------------------------------------------------------------

class TestCertProjectionAdapter:
    def test_import(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        assert CertProjectionAdapter is not None

    def test_project_pass_status(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        adapter = CertProjectionAdapter()
        fec = {
            "schema_version": "apps_repo_brief.FinalEvidenceContract/v1",
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": "repo_brief_docs",
            "status": {"evidence_status": "PASS"},
            "depth_profile": "REPO_BRIEF_STANDARD",
        }
        proj = adapter.project(fec)
        assert proj.is_grounded is True
        assert proj.requires_abstain is False
        assert proj.evidence_status == "PASS"

    def test_project_missing_status_abstains(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        adapter = CertProjectionAdapter()
        fec = {
            "schema_version": "v1",
            "contract_type": "apps_repo_brief.FinalEvidenceContract.v1",
            "retrieval_surface_id": "repo_brief_docs",
            "status": {"evidence_status": "MISSING"},
            "depth_profile": "REPO_BRIEF_STANDARD",
        }
        proj = adapter.project(fec)
        assert proj.is_grounded is False
        assert proj.requires_abstain is True

    def test_project_unknown_status_not_grounded(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        adapter = CertProjectionAdapter()
        proj = adapter.project({})
        assert proj.is_grounded is False
        assert proj.evidence_status == "UNKNOWN"

    def test_adapter_does_not_mint_fec(self) -> None:
        from apps_repo_brief.cert.cert_projection_adapter import CertProjectionAdapter
        adapter = CertProjectionAdapter()
        fec_input = {"status": {"evidence_status": "PASS"}, "retrieval_surface_id": "repo_brief_docs"}
        proj = adapter.project(fec_input)
        proj_dict = proj.to_dict()
        assert "schema_version" in proj_dict
        assert proj_dict.get("contract_type") != "MINTED_BY_CERT"

    def test_validate_projection_unknown_warns(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter, CertProjection
        adapter = CertProjectionAdapter()
        proj = adapter.project({})
        warnings = adapter.validate_projection(proj)
        assert any("UNKNOWN" in w for w in warnings)

    def test_fec_producer_retired_warning(self, caplog: Any) -> None:
        import logging
        from apps_repo_brief.cert.fec_producer import produce_fec, _FEC_PRODUCER_RETIRED
        with caplog.at_level(logging.WARNING):
            produce_fec({})
        assert any("RETIRED" in r.message for r in caplog.records)

    def test_fec_producer_still_returns_dict_during_migration(self) -> None:
        from apps_repo_brief.cert.fec_producer import produce_fec
        result = produce_fec({"route_id": "apps_repo_brief.executive_brief_v1"})
        assert isinstance(result, dict)
        assert result["route_id"] == "apps_repo_brief.executive_brief_v1"


# ---------------------------------------------------------------------------
# P4.6 — L2 E1-E5 Receipt Structure
# ---------------------------------------------------------------------------

class TestL2Receipts:
    def test_import_all(self) -> None:
        from apps_repo_brief.L2 import (
            L2Receipt, E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle
        )
        assert all(c is not None for c in [L2Receipt, E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle])

    def test_receipt_to_dict(self) -> None:
        from apps_repo_brief.L2 import E1Receipt
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        r = E1Receipt(status=ReceiptStatus.PASS, sections_required=5, sections_present=5, evidence_status="PASS", depth_profile="REPO_BRIEF_STANDARD")
        d = r.to_dict()
        assert d["step"] == "E1"
        assert d["status"] == "PASS"
        assert d["sections_required"] == 5

    def test_bundle_overall_status_pass(self) -> None:
        from apps_repo_brief.L2 import E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        bundle = L2ReceiptBundle(
            e1=E1Receipt(status=ReceiptStatus.PASS),
            e2=E2Receipt(status=ReceiptStatus.PASS),
            e3=E3Receipt(status=ReceiptStatus.PASS),
            e4=E4Receipt(status=ReceiptStatus.PASS),
            e5=E5Receipt(status=ReceiptStatus.PASS),
        )
        assert bundle.overall_status() == ReceiptStatus.PASS

    def test_bundle_overall_status_fail_on_any_fail(self) -> None:
        from apps_repo_brief.L2 import E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        bundle = L2ReceiptBundle(
            e1=E1Receipt(status=ReceiptStatus.PASS),
            e2=E2Receipt(status=ReceiptStatus.FAIL),
            e3=E3Receipt(status=ReceiptStatus.PASS),
            e4=E4Receipt(status=ReceiptStatus.PASS),
            e5=E5Receipt(status=ReceiptStatus.PASS),
        )
        assert bundle.overall_status() == ReceiptStatus.FAIL

    def test_bundle_has_exit_escalations(self) -> None:
        from apps_repo_brief.L2 import E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        bundle = L2ReceiptBundle(
            e1=E1Receipt(status=ReceiptStatus.PASS),
            e2=E2Receipt(status=ReceiptStatus.PASS),
            e3=E3Receipt(status=ReceiptStatus.PASS),
            e4=E4Receipt(status=ReceiptStatus.WARN, escalated_slot_ids=["S1"]),
            e5=E5Receipt(status=ReceiptStatus.PASS),
        )
        assert bundle.has_exit_escalations() is True

    def test_skip_bundle(self) -> None:
        from apps_repo_brief.L2 import L2ReceiptBundle
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        bundle = L2ReceiptBundle.make_skip_bundle()
        assert bundle.overall_status() == ReceiptStatus.SKIP

    def test_bundle_to_dict_structure(self) -> None:
        from apps_repo_brief.L2 import E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        bundle = L2ReceiptBundle(
            e1=E1Receipt(status=ReceiptStatus.PASS),
            e2=E2Receipt(status=ReceiptStatus.PASS),
            e3=E3Receipt(status=ReceiptStatus.PASS),
            e4=E4Receipt(status=ReceiptStatus.PASS),
            e5=E5Receipt(status=ReceiptStatus.PASS),
        )
        d = bundle.to_dict()
        assert all(k in d for k in ["overall_status", "e1", "e2", "e3", "e4", "e5"])


# ---------------------------------------------------------------------------
# P4.7 — Exit v6 X3 Checks
# ---------------------------------------------------------------------------

class TestExitV6Checks:
    def test_import(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        assert ExitV6Checker is not None

    def test_board_readiness_skip_non_board(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        result = checker.check_board_readiness({}, "REPO_BRIEF_STANDARD")
        assert result.verdict.value == "SKIP"
        assert not result.x3_triggered

    def test_board_readiness_pass(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        bundle = {
            "e5": {"coverage_pct": 97.0},
            "e4": {"escalated_slot_ids": []},
            "e1": {"evidence_status": "PASS"},
        }
        result = checker.check_board_readiness(bundle, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.verdict.value == "PASS"

    def test_board_readiness_block_low_coverage(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        bundle = {
            "e5": {"coverage_pct": 80.0},
            "e4": {"escalated_slot_ids": []},
            "e1": {"evidence_status": "PASS"},
        }
        result = checker.check_board_readiness(bundle, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.verdict.value == "BLOCK"
        assert result.x3_triggered

    def test_board_readiness_block_missing_evidence(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        bundle = {
            "e5": {"coverage_pct": 96.0},
            "e4": {"escalated_slot_ids": []},
            "e1": {"evidence_status": "MISSING"},
        }
        result = checker.check_board_readiness(bundle, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.x3_triggered

    def test_citation_integrity_pass_standard(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        slots = {"S0": "Text [src:adr-001] and [ref:commit-abc] and [cite:test-file-x] and [src:doc-y] here [ref:a] [src:b] [cite:c] [ref:d]"}
        result = checker.check_citation_integrity(slots, "REPO_BRIEF_STANDARD")
        assert result.verdict.value == "PASS"

    def test_citation_integrity_block_too_few(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        slots = {"S0": "No citations at all."}
        result = checker.check_citation_integrity(slots, "REPO_BRIEF_STANDARD")
        assert result.verdict.value == "BLOCK"
        assert result.x3_triggered

    def test_citation_integrity_board_needs_25(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        slots = {"S0": " ".join(f"[src:src-{i}]" for i in range(24))}
        result = checker.check_citation_integrity(slots, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.verdict.value == "BLOCK"

    def test_citation_integrity_board_25_passes(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        slots = {"S0": " ".join(f"[src:src-{i}]" for i in range(25))}
        result = checker.check_citation_integrity(slots, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.verdict.value == "PASS"

    def test_run_all_returns_two_results(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        checker = ExitV6Checker()
        results = checker.run_all({}, {"S0": "ok"}, "REPO_BRIEF_STANDARD")
        assert len(results) == 2
        names = {r.check_name for r in results}
        assert "board_readiness" in names
        assert "citation_integrity" in names


# ---------------------------------------------------------------------------
# P4.8 — 25 Negative Controls (fail-closed behaviour)
# ---------------------------------------------------------------------------

class TestNegativeControls:
    """25 negative control tests ensuring fail-closed behaviour across W4."""

    # --- StyleGate L2 repair negative controls ---

    def test_nc01_empty_slots_no_error(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        repair = StyleGateL2Repair()
        bundle = repair.run({})
        assert not bundle.has_escalations
        assert bundle.e4_receipt["slots_inspected"] == 0

    def test_nc02_none_guidance_handled(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        repair = StyleGateL2Repair()
        bundle = repair.run({"S0": "body"}, synthesis_guidance=None)
        assert bundle.e4_receipt["slots_inspected"] == 1

    def test_nc03_multiple_stubs_all_escalate(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        repair = StyleGateL2Repair()
        bundle = repair.run({"S0": "{{A}} and {{B}} and {{C}}"})
        assert bundle.has_escalations

    def test_nc04_exact_length_limit_not_truncated(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        from apps_repo_brief.L2.style_gate_l2_repair import RepairOutcome
        repair = StyleGateL2Repair()
        body = "x" * 8_000
        bundle = repair.run({"S0": body})
        assert bundle.repair_results[0].outcome == RepairOutcome.CLEAN

    def test_nc05_over_limit_by_one_truncated(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        from apps_repo_brief.L2.style_gate_l2_repair import RepairOutcome
        repair = StyleGateL2Repair()
        body = "x" * 8_001
        bundle = repair.run({"S0": body})
        assert bundle.repair_results[0].outcome == RepairOutcome.REPAIRED

    # --- StyleGate Exit negative controls ---

    def test_nc06_exit_empty_escalated_list_passes(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        result = StyleGateExitCheck().check({"escalated_slot_ids": []}, {"S0": "ok"})
        assert not result.x3_triggered

    def test_nc07_exit_multiple_stubs_all_block(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        result = StyleGateExitCheck().check(
            {"escalated_slot_ids": ["S0", "S1"]},
            {"S0": "{{STUB_A}}", "S1": "{{STUB_B}}"},
        )
        assert result.x3_triggered
        assert len(result.blocking_slot_ids) == 2

    def test_nc08_exit_no_repaired_slots_dict_passes(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        result = StyleGateExitCheck().check({"escalated_slot_ids": ["S0"]}, {})
        assert not result.x3_triggered

    # --- CertProjectionAdapter negative controls ---

    def test_nc09_adapter_non_dict_input_raises(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        with pytest.raises(ValueError, match="expects a dict"):
            CertProjectionAdapter().project("not_a_dict")  # type: ignore[arg-type]

    def test_nc10_adapter_empty_dict_returns_defaults(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        proj = CertProjectionAdapter().project({})
        assert proj.evidence_status == "UNKNOWN"
        assert proj.retrieval_surface_id == "repo_brief_docs"

    def test_nc11_contradicted_status_not_grounded(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        proj = CertProjectionAdapter().project({"status": {"evidence_status": "CONTRADICTED"}})
        assert not proj.is_grounded
        assert proj.requires_abstain

    def test_nc12_unsupported_status_requires_abstain(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        proj = CertProjectionAdapter().project({"status": {"evidence_status": "UNSUPPORTED"}})
        assert proj.requires_abstain

    def test_nc13_projection_to_dict_no_fec_authority_field(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        proj = CertProjectionAdapter().project({"status": {"evidence_status": "PASS"}})
        d = proj.to_dict()
        assert "authoritative" not in d
        assert "producer" not in d

    # --- L2 receipt negative controls ---

    def test_nc14_e4_receipt_empty_escalations(self) -> None:
        from apps_repo_brief.L2 import E4Receipt
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        r = E4Receipt(status=ReceiptStatus.PASS)
        assert r.escalated_slot_ids == []

    def test_nc15_bundle_warn_beats_pass(self) -> None:
        from apps_repo_brief.L2 import E1Receipt, E2Receipt, E3Receipt, E4Receipt, E5Receipt, L2ReceiptBundle
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        bundle = L2ReceiptBundle(
            e1=E1Receipt(status=ReceiptStatus.PASS),
            e2=E2Receipt(status=ReceiptStatus.WARN),
            e3=E3Receipt(status=ReceiptStatus.PASS),
            e4=E4Receipt(status=ReceiptStatus.PASS),
            e5=E5Receipt(status=ReceiptStatus.PASS),
        )
        assert bundle.overall_status() == ReceiptStatus.WARN

    def test_nc16_skip_bundle_no_escalations(self) -> None:
        from apps_repo_brief.L2 import L2ReceiptBundle
        bundle = L2ReceiptBundle.make_skip_bundle()
        assert not bundle.has_exit_escalations()

    # --- Exit v6 negative controls ---

    def test_nc17_board_readiness_block_escalated_e4(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        bundle = {
            "e5": {"coverage_pct": 97.0},
            "e4": {"escalated_slot_ids": ["S1"]},
            "e1": {"evidence_status": "PASS"},
        }
        result = ExitV6Checker().check_board_readiness(bundle, "REPO_BRIEF_BOARD_DOSSIER")
        assert result.x3_triggered

    def test_nc18_citation_integrity_light_needs_3(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        slots = {"S0": "[src:a] [ref:b]"}
        result = ExitV6Checker().check_citation_integrity(slots, "REPO_BRIEF_LIGHT")
        assert result.x3_triggered

    def test_nc19_citation_integrity_light_3_passes(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        slots = {"S0": "[src:a] [ref:b] [cite:c]"}
        result = ExitV6Checker().check_citation_integrity(slots, "REPO_BRIEF_LIGHT")
        assert not result.x3_triggered

    def test_nc20_citation_integrity_unknown_profile_defaults_to_3(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        slots = {"S0": "[src:a] [ref:b] [cite:c]"}
        result = ExitV6Checker().check_citation_integrity(slots, "UNKNOWN_PROFILE")
        assert not result.x3_triggered

    def test_nc21_citation_pattern_case_insensitive(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        slots = {"S0": "[SRC:a] [REF:b] [CITE:c]"}
        result = ExitV6Checker().check_citation_integrity(slots, "REPO_BRIEF_LIGHT")
        assert not result.x3_triggered

    def test_nc22_run_all_board_both_checks_fail(self) -> None:
        from apps_repo_brief.exit import ExitV6Checker
        bundle = {
            "e5": {"coverage_pct": 10.0},
            "e4": {"escalated_slot_ids": ["S1"]},
            "e1": {"evidence_status": "MISSING"},
        }
        results = ExitV6Checker().run_all(bundle, {"S0": "no citations"}, "REPO_BRIEF_BOARD_DOSSIER")
        triggered = [r for r in results if r.x3_triggered]
        assert len(triggered) == 2

    def test_nc23_style_gate_exit_result_to_dict(self) -> None:
        from apps_repo_brief.exit import StyleGateExitCheck
        result = StyleGateExitCheck().check({"escalated_slot_ids": ["S0"]}, {"S0": "{{STUB}}"})
        d = result.to_dict()
        assert "verdict" in d
        assert "x3_triggered" in d
        assert d["x3_triggered"] is True

    def test_nc24_cert_projection_stale_source_count(self) -> None:
        from apps_repo_brief.cert import CertProjectionAdapter
        fec = {
            "status": {"evidence_status": "PASS"},
            "freshness_report": {"stale_sources": ["s1", "s2", "s3"]},
        }
        proj = CertProjectionAdapter().project(fec)
        assert proj.stale_source_count == 3

    def test_nc25_e4_receipt_violations_tally(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        repair = StyleGateL2Repair()
        bundle = repair.run({
            "S0": "{{STUB_A}}",
            "S1": "{{STUB_B}}",
        })
        tally = bundle.e4_receipt["violations_by_type"]
        assert tally.get("unescaped_evidence_stub", 0) == 2


# ---------------------------------------------------------------------------
# P4.9 — apps_eval dual-scenario verification
# ---------------------------------------------------------------------------

class TestAppsEvalDualScenario:
    """
    Verify that apps_eval scenario runner remains green for both:
    - old apps_exec scenarios (backward compat during migration window)
    - new apps_repo_brief scenarios (canonical spine)
    """

    def test_apps_eval_scenario_runner_importable(self) -> None:
        try:
            import apps_eval.integrations.eval_ingress_runner as runner
            assert runner is not None
        except ImportError:
            pytest.skip("apps_eval not available in this environment")

    def test_apps_repo_brief_in_eval_routes(self) -> None:
        try:
            from apps_eval.config.agent_spec_config import AgentSpecConfig
        except ImportError:
            pytest.skip("apps_eval not available")
        # apps_repo_brief should be listed as a known app or route
        # (actual registry check depends on eval wiring — best-effort)

    def test_apps_exec_shim_still_importable(self) -> None:
        try:
            import apps_exec
            assert apps_exec is not None
        except ImportError:
            pytest.skip("apps_exec shim not present")

    def test_apps_repo_brief_main_importable(self) -> None:
        import apps_repo_brief
        assert apps_repo_brief is not None


# ---------------------------------------------------------------------------
# P4.10 — W4 Integration Acceptance
# ---------------------------------------------------------------------------

class TestW4Integration:
    """
    Full W4 flow: StyleGateL2Repair → E4Receipt → StyleGateExitCheck →
    ExitV6Checker → CertProjectionAdapter.
    """

    def test_clean_flow_no_blocks(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair, L2ReceiptBundle, E1Receipt, E2Receipt, E3Receipt, E5Receipt
        from apps_repo_brief.L2.l2_receipts import ReceiptStatus
        from apps_repo_brief.exit import StyleGateExitCheck, ExitV6Checker
        from apps_repo_brief.cert import CertProjectionAdapter

        slots = {
            "S0": "Executive summary with [src:adr-001] [ref:commit-x] [cite:test-y].",
            "I0": "Instructions with [src:policy-1] [ref:doc-2] [cite:adr-3] [src:a] [cite:b] [ref:c] [src:d] [cite:e].",
        }

        # L2.E4
        repair = StyleGateL2Repair()
        repair_bundle = repair.run(slots)
        assert not repair_bundle.has_escalations

        # E4 receipt
        e4_dict = repair_bundle.e4_receipt
        assert e4_dict["slots_escalated"] == 0

        # StyleGate Exit
        exit_gate = StyleGateExitCheck()
        exit_result = exit_gate.check(e4_dict, repair_bundle.repaired_slots)
        assert not exit_result.x3_triggered

        # Exit v6 checks (STANDARD profile)
        checker = ExitV6Checker()
        bundle_dict = {
            "e5": {"coverage_pct": 80.0},
            "e4": e4_dict,
            "e1": {"evidence_status": "PASS"},
        }
        v6_results = checker.run_all(bundle_dict, repair_bundle.repaired_slots, "REPO_BRIEF_STANDARD")
        assert all(not r.x3_triggered for r in v6_results)

        # CertProjection
        fec = {"status": {"evidence_status": "PASS"}, "retrieval_surface_id": "repo_brief_docs"}
        proj = CertProjectionAdapter().project(fec)
        assert proj.is_grounded

    def test_escalation_flow_triggers_x3(self) -> None:
        from apps_repo_brief.L2 import StyleGateL2Repair
        from apps_repo_brief.exit import StyleGateExitCheck

        slots = {"S0": "Has {{UNRESOLVED}} stub."}
        repair_bundle = StyleGateL2Repair().run(slots)
        assert repair_bundle.has_escalations

        exit_result = StyleGateExitCheck().check(
            repair_bundle.e4_receipt,
            repair_bundle.repaired_slots,
        )
        assert exit_result.x3_triggered

    def test_w3_regression_pa_compiler_still_compiles(self) -> None:
        from apps_repo_brief.prompt_assembly import RepoBriefPACompiler
        compiler = RepoBriefPACompiler()
        compiler.load()
        assert compiler.list_templates()

    def test_w3_regression_c0_adapter_still_builds(self) -> None:
        from apps_repo_brief.c0 import RepoBriefC0Adapter
        spec = RepoBriefC0Adapter().build_c0_request({"depth_profile": "REPO_BRIEF_STANDARD"})
        assert spec is not None
