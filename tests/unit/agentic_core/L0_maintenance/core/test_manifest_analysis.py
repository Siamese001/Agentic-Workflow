"""
File: tests/unit/agentic_core/L0_maintenance/test_manifest_analysis.py
Description: Tests for the Dry-Run Verification Tool.
Mandate: 100% Pass.
"""

from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.scripts.general_scripts.verify_manifest import analyze_impact


class TestManifestAnalysis:
    @pytest.fixture
    def safe_report(self):
        """A standard, safe dry-run report."""
        return {
            "meta": {"dry_run": True, "territory": "tests"},
            "phase1": {
                "violations_found": [
                    {"type": "NAMING", "file": "a.py"},
                    {"type": "IMPORT", "file": "b.py"},
                ]
            },
            "phase2": {
                "modifications": [
                    {"action": "would_fix", "target": "a.py", "agent": "Fixer"},
                    {"action": "would_fix", "target": "b.py", "agent": "Fixer"},
                ],
                "failures": [],
            },
        }

    @pytest.fixture
    def dangerous_report(self):
        """A report indicating mass deletion (unsafe)."""
        orphans = [{"type": "ORPHANED_FILE", "file": f"del_{i}.py"} for i in range(50)]
        mods = [{"action": "would_delete", "target": f"del_{i}.py"} for i in range(50)]

        return {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": orphans},
            "phase2": {"modifications": mods, "failures": []},
        }

    def test_analysis_passes_safe_run(self, safe_report):
        """Scenario: Normal operation should pass analysis."""
        with patch("logging.info") as mock_info:
            result = analyze_impact(safe_report)
            assert result is True
            # Verify that impact analysis was logged
            mock_info.assert_any_call("--- IMPACT ANALYSIS: tests ---")

    def test_analysis_flags_mass_deletion(self, dangerous_report):
        """Scenario: >10 orphans triggers warning."""
        with patch("logging.warning") as mock_warning:
            result = analyze_impact(dangerous_report)
            assert result is False
            # Verify that mass deletion warning was logged
            mock_warning.assert_any_call(
                "🚨 MASS DELETION RISK: 50 orphan files identified for deletion."
            )

    def test_analysis_flags_blast_radius(self):
        """Scenario: Too many files modified."""
        # Create 100 modifications
        mods = [{"target": f"file_{i}.py"} for i in range(100)]
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {"modifications": mods, "failures": []},
        }

        with patch("logging.warning") as mock_warning:
            result = analyze_impact(report)
            assert result is False
            # Verify that high blast radius warning was logged
            mock_warning.assert_any_call(
                "🚨 HIGH BLAST RADIUS: 100 files would be modified. Manual review required."
            )

    def test_analysis_warns_on_live_run(self, safe_report):
        """Scenario: Analyzing a live run report should warn but might pass if metrics are ok."""
        safe_report["meta"]["dry_run"] = False

        with patch("logging.warning") as mock_warning:
            result = analyze_impact(safe_report)
            assert result is True  # Still passes metrics, but warns
            # Verify that live run warning was logged
            mock_warning.assert_any_call("⚠️  This report is from a LIVE RUN, not a dry-run.")

    def test_analysis_handles_budget_blocks(self):
        """Scenario: Actions blocked by safety budget should trigger warnings."""
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {
                "modifications": [],
                "failures": [
                    {"status": "blocked_by_safety"},
                    {"status": "blocked_by_safety"},
                    {"status": "other_error"},
                ],
            },
        }

        with patch("logging.warning") as mock_warning:
            result = analyze_impact(report)
            assert result is True  # Still passes, but warns about budget blocks
            # Verify that budget block warning was logged
            mock_warning.assert_any_call("⚠️  2 actions were blocked by safety budget limits.")

    def test_analysis_handles_empty_report(self):
        """Scenario: Empty report should not crash."""
        empty_report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {"modifications": [], "failures": []},
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(empty_report)
            assert result is True
            # Verify that zero violations was logged
            mock_info.assert_any_call("Total Violations Detected: 0")

    def test_analysis_groups_by_type(self):
        """Scenario: Violations should be grouped by type correctly."""
        report = {
            "meta": {"dry_run": True, "territory": "test_territory"},
            "phase1": {
                "violations_found": [
                    {"type": "NAMING", "file": "a.py"},
                    {"type": "NAMING", "file": "b.py"},
                    {"type": "IMPORT", "file": "c.py"},
                    {"type": "UNKNOWN", "file": "d.py"},
                ]
            },
            "phase2": {"modifications": [], "failures": []},
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(report)
            assert result is True
            # Verify type grouping
            mock_info.assert_any_call("  - NAMING: 2")
            mock_info.assert_any_call("  - IMPORT: 1")
            mock_info.assert_any_call("  - UNKNOWN: 1")

    def test_analysis_calculates_unique_files(self):
        """Scenario: Should count unique files, not total modifications."""
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {
                "modifications": [
                    {"target": "file1.py"},  # Same file modified twice
                    {"target": "file1.py"},
                    {"target": "file2.py"},  # Different file
                ],
                "failures": [],
            },
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(report)
            assert result is True
            # Should count unique files (2), not total modifications (3)
            mock_info.assert_any_call("Files to be Modified: 2")

    def test_analysis_calculates_agents_engaged(self):
        """Scenario: Should count unique agents engaged."""
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {
                "modifications": [
                    {"agent": "Fixer"},  # Same agent used twice
                    {"agent": "Fixer"},
                    {"agent": "Mover"},  # Different agent
                    {"agent": "Cleaner"},  # Another different agent
                ],
                "failures": [],
            },
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(report)
            assert result is True
            # Should count unique agents (3), not total modifications (4)
            mock_info.assert_any_call("Agents Engaged: 3")
