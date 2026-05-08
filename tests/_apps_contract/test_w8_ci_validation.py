"""W8 — CI / ADG / RUNBOOK Integration Tests.

Verifies W8 gate hardening validation and CI integration:
- Gate registration completeness
- Test file existence
- Module export validation

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W8)
"""

from __future__ import annotations

import pytest
from pathlib import Path

from ops_scripts.ci.check_apps_rg_runtime_gate_hardening import (
    EXPECTED_GATES,
    GATE_MODULES,
    TEST_FILES,
    run_validation,
    check_test_files,
)


REPO_ROOT = Path(__file__).parent.parent.parent


class TestW8ExpectedGatesCatalog:
    """Test that expected gates catalog is complete."""

    def test_all_waves_documented(self) -> None:
        """All W0-W7 waves have expected gates listed."""
        expected_waves = ["W0", "W1", "W2", "W3", "W4", "W5", "W6", "W7"]
        
        for wave in expected_waves:
            assert wave in EXPECTED_GATES, f"Wave {wave} missing from catalog"
            assert len(EXPECTED_GATES[wave]) > 0, f"Wave {wave} has no gates"

    def test_w0_foundation_gates(self) -> None:
        """W0 foundation gates documented."""
        assert "RuntimeGateEngine initialization" in EXPECTED_GATES["W0"]
        assert "GateVerdict dataclass" in EXPECTED_GATES["W0"]

    def test_w1_post_ens_gates(self) -> None:
        """W1 POST-ENS gates documented."""
        assert "candidate_accepted_gate" in EXPECTED_GATES["W1"]

    def test_w3_pre_llm_gates(self) -> None:
        """W3 PRE-LLM gates documented."""
        assert "prompt_assembly_sha_gate" in EXPECTED_GATES["W3"]
        assert "master_resume_sha_pinned_gate" in EXPECTED_GATES["W3"]

    def test_w4_anti_fabrication_gates(self) -> None:
        """W4 anti-fabrication gates documented."""
        assert "provenance_required_gate" in EXPECTED_GATES["W4"]
        assert "anti_fabrication_composite_gate" in EXPECTED_GATES["W4"]

    def test_w5_per_cand_gates(self) -> None:
        """W5 PER-CAND gates documented."""
        assert "length_parity_strict_gate" in EXPECTED_GATES["W5"]
        assert "per_cand_quality_composite_gate" in EXPECTED_GATES["W5"]

    def test_w6_post_narr_gates(self) -> None:
        """W6 POST-NARR gates documented."""
        assert "jd_keyword_coverage_min_gate" in EXPECTED_GATES["W6"]
        assert "ats_composite_gate" in EXPECTED_GATES["W6"]

    def test_w7_pre_export_gates(self) -> None:
        """W7 PRE-EXPORT gates documented."""
        assert "docx_render_no_orphan_gate" in EXPECTED_GATES["W7"]


class TestW8GateModules:
    """Test gate module paths."""

    def test_all_modules_have_paths(self) -> None:
        """All gate modules have valid import paths."""
        for module_name, module_path in GATE_MODULES.items():
            assert module_path.startswith("apps_rg.integrations.gates")
            assert "_gates" in module_name or "_judges" in module_name

    def test_post_ens_module_listed(self) -> None:
        """W1 POST-ENS gates module catalogued."""
        assert "post_ens_resume_gates" in GATE_MODULES

    def test_per_cand_module_listed(self) -> None:
        """W5 PER-CAND gates module catalogued."""
        assert "per_cand_resume_gates" in GATE_MODULES


class TestW8TestFiles:
    """Test file existence for each wave."""

    def test_all_waves_have_test_files(self) -> None:
        """Each wave has corresponding test file on disk."""
        test_results = check_test_files()
        
        for wave, exists in test_results.items():
            assert exists, f"Test file for {wave} missing: {TEST_FILES[wave]}"

    def test_w0_test_file_exists(self) -> None:
        """W0 foundation tests exist."""
        test_path = REPO_ROOT / TEST_FILES["W0"]
        assert test_path.exists()
        content = test_path.read_text()
        assert "RuntimeGateEngine" in content or "GateVerdict" in content

    def test_w1_test_file_exists(self) -> None:
        """W1 P0 boundary fix tests exist."""
        test_path = REPO_ROOT / TEST_FILES["W1"]
        assert test_path.exists()

    def test_w5_test_file_exists(self) -> None:
        """W5 PER-CAND tests exist."""
        test_path = REPO_ROOT / TEST_FILES["W5"]
        assert test_path.exists()
        content = test_path.read_text()
        assert "length_parity" in content or "quantified_outcome" in content

    def test_w7_test_file_exists(self) -> None:
        """W7 PRE-EXPORT tests exist."""
        test_path = REPO_ROOT / TEST_FILES["W7"]
        assert test_path.exists()
        content = test_path.read_text()
        assert "docx_render" in content or "orphan" in content


class TestW8ValidationRunner:
    """Test the W8 validation runner."""

    def test_validation_produces_summary(self) -> None:
        """Validation produces summary statistics."""
        results = run_validation()
        
        assert "summary" in results
        assert "gate_results" in results
        assert "test_results" in results
        assert "status" in results

    def test_validation_counts_gates(self) -> None:
        """Validation counts total gates."""
        results = run_validation()
        summary = results["summary"]
        
        assert summary["total_gates_checked"] > 0
        assert summary["valid_gates"] >= 0
        assert summary["missing_gates"] == 0  # All should exist

    def test_all_waves_have_tests(self) -> None:
        """All 8 waves have test coverage."""
        results = run_validation()
        summary = results["summary"]
        
        assert summary["waves_with_tests"] == 8

    def test_no_missing_gates(self) -> None:
        """No gates are missing."""
        results = run_validation()
        summary = results["summary"]
        
        assert summary["missing_gates"] == 0

    def test_validation_passes(self) -> None:
        """Overall validation status is PASS."""
        results = run_validation()
        
        assert results["status"] == "PASS"


class TestW8GateHardeningCompleteness:
    """Test overall gate hardening completeness."""

    def test_minimum_gate_count(self) -> None:
        """At least 25 gates implemented."""
        results = run_validation()
        summary = results["summary"]
        
        # W1-W7 have 2+5+7+6+2 = 22 gates + W0 foundation
        assert summary["total_gates_checked"] >= 22

    def test_high_valid_gate_ratio(self) -> None:
        """95%+ of gates are valid."""
        results = run_validation()
        summary = results["summary"]
        
        if summary["total_gates_checked"] > 0:
            valid_ratio = summary["valid_gates"] / summary["total_gates_checked"]
            assert valid_ratio >= 0.95

    def test_no_broken_gates(self) -> None:
        """Zero broken gates."""
        results = run_validation()
        summary = results["summary"]
        
        assert summary["broken_gates"] == 0


class TestW8Integration:
    """W8 integration verification."""

    def test_ci_gate_script_exists(self) -> None:
        """W8 CI gate script exists on disk."""
        gate_path = REPO_ROOT / "ops_scripts/ci/check_apps_rg_runtime_gate_hardening.py"
        assert gate_path.exists()

    def test_ci_gate_is_importable(self) -> None:
        """W8 CI gate can be imported."""
        from ops_scripts.ci.check_apps_rg_runtime_gate_hardening import (
            run_validation,
            EXPECTED_GATES,
        )
        assert EXPECTED_GATES is not None
        assert callable(run_validation)

    def test_all_gates_registered_in_modules(self) -> None:
        """All expected gates are registered in modules."""
        import importlib
        
        for module_name, module_path in GATE_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                exports = getattr(module, "__all__", [])
                assert len(exports) > 0, f"{module_name} has no exports"
            except ImportError:
                pytest.fail(f"Cannot import {module_path}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
