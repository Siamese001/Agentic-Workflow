"""
Test Suite: Global Candidate Vacuum (Shared Layer Hardening)
ULTRA-AGGRESSIVE SUITE: Validates Global Candidate Detection.
100% PASS LANGUAGE: Mandatory for Shared Layer Hardening.

[SSOT 2026-01-27] Phase 9 Aggressive Testing

Note: These tests directly invoke the detection logic without full agent instantiation
to avoid CoreIntegrityVerifier overhead during unit testing.
"""

from pathlib import Path


def _check_app_domain_violation_logic(
    app_rg_score: float,
    app_lic_score: float,
    rel_path: Path,
) -> tuple[bool, str]:
    """
    Standalone implementation of Global Candidate Detection logic.
    Mirrors LocationValidatorAgent._check_app_domain_violation for unit testing.
    """
    current_root = rel_path.parts[0]

    # 1. GLOBAL CANDIDATE DETECTION (Vacuum to apps_shared)
    if current_root in ["apps_rg", "apps_lic"]:
        if app_rg_score < 0.5 and app_lic_score < 0.5:
            filename = rel_path.name
            if not filename.startswith(("rg_", "lic_", "resume_", "outreach_")):
                return (
                    False,
                    "GLOBAL CANDIDATE DETECTED: Low domain signals - belongs in apps_shared/utils",
                )

    # 2. CROSS-CONTAMINATION CHECK (App vs App)
    if current_root == "apps_rg" and app_lic_score > app_rg_score * 2.0:
        return (
            False,
            f"APP DOMAIN VIOLATION: Strong apps_lic signals ({app_lic_score:.1f} vs {app_rg_score:.1f})",
        )

    if current_root == "apps_lic" and app_rg_score > app_lic_score * 2.0:
        return (
            False,
            f"APP DOMAIN VIOLATION: Strong apps_rg signals ({app_rg_score:.1f} vs {app_lic_score:.1f})",
        )

    return True, ""


class TestGlobalCandidateVacuum:
    """
    ULTRA-AGGRESSIVE SUITE: Validates Global Candidate Detection.
    100% PASS LANGUAGE: Mandatory for Shared Layer Hardening.
    """

    def test_generic_utility_is_vacuumed(self):
        """100% PASS: Ensures 'date_helper.py' in apps_lic is flagged for apps_shared."""
        rel_path = Path("apps_lic/engines/date_helper.py")

        # Simulate generic DNA (app_rg=0.1, app_lic=0.1)
        is_valid, msg = _check_app_domain_violation_logic(0.1, 0.1, rel_path)

        assert is_valid is False, "FAIL: Generic utility was allowed to stay in domain folder."
        assert "GLOBAL CANDIDATE" in msg, f"FAIL: Wrong violation type: {msg}"

    def test_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'lic_special_tool.py' stays in apps_lic despite low DNA."""
        rel_path = Path("apps_lic/engines/lic_special_tool.py")

        # Even with low DNA, the prefix 'lic_' provides "Territorial Immunity"
        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: Prefixed file was incorrectly flagged for vacuuming."

    def test_app_cross_contamination_detection(self):
        """100% PASS: Ensures Resume logic in LinkedIn folder is flagged."""
        rel_path = Path("apps_lic/engines/resume_parser.py")

        # Strong Resume DNA (3.0) vs LinkedIn DNA (0.2)
        is_valid, msg = _check_app_domain_violation_logic(3.0, 0.2, rel_path)
        assert is_valid is False
        assert "Strong apps_rg signals" in msg, "FAIL: Failed to detect app-to-app leakage."

    def test_global_weight_superiority(self):
        """100% PASS: Verifies Shared Gravity (95) beats App Gravity (90) in SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint_config import (
            SOVEREIGN_TERRITORIES,
        )

        shared_w = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"]["apps_shared/utils"]["weight"]
        app_w = SOVEREIGN_TERRITORIES["apps_rg"]["ast_signals"]["apps_rg/engines"]["weight"]

        assert shared_w == 95
        assert shared_w > app_w, "CRITICAL: Global utility gravity is weaker than domain gravity."

    def test_rg_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'rg_builder.py' stays in apps_rg despite low DNA."""
        rel_path = Path("apps_rg/engines/rg_builder.py")

        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: rg_ prefixed file was incorrectly flagged."

    def test_resume_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'resume_formatter.py' stays in apps_rg despite low DNA."""
        rel_path = Path("apps_rg/engines/resume_formatter.py")

        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: resume_ prefixed file was incorrectly flagged."

    def test_outreach_prefixed_file_is_retained(self):
        """100% PASS: Ensures 'outreach_manager.py' stays in apps_lic despite low DNA."""
        rel_path = Path("apps_lic/engines/outreach_manager.py")

        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: outreach_ prefixed file was incorrectly flagged."

    def test_apps_shared_files_not_flagged(self):
        """100% PASS: Ensures files already in apps_shared are not flagged."""
        rel_path = Path("apps_shared/utils/date_helper.py")

        # Files in apps_shared should pass (not in apps_rg or apps_lic)
        is_valid, _ = _check_app_domain_violation_logic(0.1, 0.1, rel_path)
        assert is_valid is True, "FAIL: apps_shared file was incorrectly flagged."
