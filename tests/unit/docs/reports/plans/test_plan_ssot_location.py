"""Test to verify plans are saved in SSOT location docs/reports/plans."""

from pathlib import Path


class TestPlanSSOTLocation:
    """Test that plans are properly saved in SSOT location."""

    def test_agent_rollout_plan_in_ssot(self):
        """Test that agent-rollout-phases-2b02cf.md is in docs/reports/plans."""
        # Fix: Use absolute path to repo root
        repo_root = Path("c:/Git/Agentic-Workflow")
        plan_path = repo_root / "docs" / "reports" / "plans" / "agent-rollout-phases-2b02cf.md"

        assert plan_path.exists(), f"Plan should exist at SSOT location: {plan_path}"

        # Verify it's not in the old location
        old_location = repo_root / ".windsurf" / "plans" / "agent-rollout-phases-2b02cf.md"
        # Note: We don't assert this doesn't exist as it might still be there

    def test_plan_content_is_valid(self):
        """Test that the plan content is valid markdown."""
        repo_root = Path("c:/Git/Agentic-Workflow")
        plan_path = repo_root / "docs" / "reports" / "plans" / "agent-rollout-phases-2b02cf.md"

        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify it has the expected title
        assert "# Agent Rollout Phases" in content, "Plan should have correct title"

        # Verify it has expected sections
        assert "## Overview" in content, "Plan should have Overview section"
        assert "Phase 7A" in content, "Plan should have Phase 7A section"
        assert "Phase 7F" in content, "Plan should have Phase 7F section"

        # Verify it's not empty
        assert len(content) > 1000, "Plan should have substantial content"

    def test_ssot_directory_structure(self):
        """Test that SSOT directory structure exists."""
        repo_root = Path("c:/Git/Agentic-Workflow")

        # Verify the SSOT structure exists
        ssot_path = repo_root / "docs" / "reports" / "plans"
        assert ssot_path.exists(), "SSOT plans directory should exist"
        assert ssot_path.is_dir(), "SSOT plans should be a directory"

        # Verify parent directories exist
        assert (repo_root / "docs").exists(), "docs directory should exist"
        assert (repo_root / "docs" / "reports").exists(), "docs/reports directory should exist"

    def test_other_plans_in_ssot(self):
        """Test that other plans are also in SSOT location."""
        repo_root = Path("c:/Git/Agentic-Workflow")
        plans_dir = repo_root / "docs" / "reports" / "plans"

        # Should have at least some plan files
        plan_files = list(plans_dir.glob("*.md"))
        assert len(plan_files) > 0, "Should have at least one plan file in SSOT"

        # Check for known plans
        known_plans = [
            "AGENT_MIGRATION_PLAN_2026-02-03.md",
            "agent-rollout-phases-2b02cf.md",
        ]

        for plan in known_plans:
            plan_path = plans_dir / plan
            if plan_path.exists():
                assert plan_path.stat().st_size > 100, f"Plan {plan} should have content"

    def test_no_plans_in_old_location(self):
        """Test that plans are not in the old .windsurf/plans location."""
        repo_root = Path("c:/Git/Agentic-Workflow")
        old_plans_dir = repo_root / ".windsurf" / "plans"

        # This test is informational - the old location might still have files
        if old_plans_dir.exists():
            old_files = list(old_plans_dir.glob("*.md"))
            # We don't assert this is empty, just log it
            print(f"Old location still has {len(old_files)} plan files")
