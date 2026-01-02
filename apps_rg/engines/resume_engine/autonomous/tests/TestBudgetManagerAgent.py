from __future__ import annotations
"""
Unit Tests for ResumeEngineContext

Tests the core context class including:
- Initialization
- Signal management
- Section backup/rollback
- Budget tracking
- Dependency graph
"""

import pytest

from ..context import BudgetManager, ResumeEngineContext, SectionDependencyGraph


class TestBudgetManager:
    """Tests for BudgetManager class."""

    def test_init_default(self):
        """Test default initialization."""
        budget = BudgetManager()
        assert budget.max_cost == 2.0
        assert budget.current_cost == 0.0
        assert budget.check_budget() is True

    def test_init_custom_limit(self):
        """Test custom budget limit."""
        budget = BudgetManager(max_cost_usd=5.0)
        assert budget.max_cost == 5.0

    def test_track_tokens(self):
        """Test token tracking."""
        budget = BudgetManager()
        cost = budget.track_tokens("gemini-3-flash-preview", 1000, 500)

        assert cost > 0
        assert budget.total_input_tokens == 1000
        assert budget.total_output_tokens == 500
        assert budget.call_count == 1
        assert budget.current_cost == cost

    def test_budget_exhaustion(self):
        """Test budget exhaustion detection."""
        budget = BudgetManager(max_cost_usd=0.001)

        # Track enough tokens to exceed budget
        budget.track_tokens("gpt-4", 10000, 5000)

        assert budget.check_budget() is False
        assert budget.get_remaining_budget() == 0.0

    def test_get_stats(self):
        """Test statistics retrieval."""
        budget = BudgetManager()
        budget.track_tokens("gemini-3-flash-preview", 100, 50)

        stats = budget.get_stats()

        assert "current_cost_usd" in stats
        assert "max_cost_usd" in stats
        assert "remaining_usd" in stats
        assert "total_input_tokens" in stats
        assert "total_output_tokens" in stats
        assert "call_count" in stats
        assert stats["call_count"] == 1


class TestSectionDependencyGraph:
    """Tests for SectionDependencyGraph class."""

    def test_default_graph(self):
        """Test default graph initialization."""
        graph = SectionDependencyGraph()

        assert "experience" in graph.graph
        assert "skills" in graph.graph
        assert "summary" in graph.graph

    def test_get_impact_radius(self):
        """Test impact radius calculation."""
        graph = SectionDependencyGraph()

        # Experience impacts skills and achievements
        impacted = graph.get_impact_radius("experience")
        assert "skills" in impacted or "achievements" in impacted

    def test_get_dependencies(self):
        """Test dependency retrieval."""
        graph = SectionDependencyGraph()

        # Summary depends on experience, skills, education
        deps = graph.get_dependencies("summary")
        assert len(deps) > 0

    def test_add_dependency(self):
        """Test adding custom dependency."""
        graph = SectionDependencyGraph()
        graph.add_dependency("custom_section", "experience")

        assert "experience" in graph.graph["custom_section"]


class TestResumeEngineContext:
    """Tests for ResumeEngineContext class."""

    def test_init(self):
        """Test context initialization."""
        ctx = ResumeEngineContext()

        assert ctx.model_id is not None
        assert ctx.signals == set()
        assert ctx.modified_sections == set()
        assert ctx.results == {}
        assert ctx.budget is not None
        assert ctx.section_graph is not None

    def test_signal_management(self):
        """Test signal add/remove/check."""
        ctx = ResumeEngineContext()

        ctx.add_signal("TEST_SIGNAL")
        assert ctx.has_signal("TEST_SIGNAL")
        assert "TEST_SIGNAL" in ctx.signals

        ctx.remove_signal("TEST_SIGNAL")
        assert not ctx.has_signal("TEST_SIGNAL")

    def test_section_backup_rollback(self):
        """Test section backup and rollback."""
        ctx = ResumeEngineContext()
        ctx.current_resume = {"summary": "Original summary"}

        # Backup
        ctx.backup_section("summary", "Original summary")

        # Modify
        ctx.current_resume["summary"] = "Modified summary"

        # Rollback
        result = ctx.rollback_section("summary")

        assert result is True
        assert ctx.current_resume["summary"] == "Original summary"

    def test_update_section_with_backup(self):
        """Test update_section creates backup."""
        ctx = ResumeEngineContext()
        ctx.current_resume = {"summary": "Original"}

        ctx.update_section("summary", "Updated")

        assert ctx.current_resume["summary"] == "Updated"
        assert "summary" in ctx.modified_sections
        assert "summary" in ctx.section_backups
        assert ctx.section_backups["summary"] == "Original"

    def test_rollback_all(self):
        """Test rollback all sections."""
        ctx = ResumeEngineContext()
        ctx.current_resume = {
            "summary": "Original summary",
            "skills": "Original skills",
        }

        ctx.update_section("summary", "New summary")
        ctx.update_section("skills", "New skills")

        ctx.rollback_all()

        assert ctx.current_resume["summary"] == "Original summary"
        assert ctx.current_resume["skills"] == "Original skills"
        assert len(ctx.modified_sections) == 0

    def test_record_result(self):
        """Test result recording."""
        ctx = ResumeEngineContext()

        ctx.record_result("TestAgent", passed=True, details="All good")

        assert "TestAgent" in ctx.results
        assert ctx.results["TestAgent"]["passed"] is True
        assert ctx.results["TestAgent"]["details"] == "All good"

    def test_get_failed_results(self):
        """Test failed results retrieval."""
        ctx = ResumeEngineContext()

        ctx.record_result("Agent1", passed=True)
        ctx.record_result("Agent2", passed=False, details="Failed")
        ctx.record_result("Agent3", passed=False, details="Also failed")

        failed = ctx.get_failed_results()

        assert len(failed) == 2
        assert "Agent1" not in failed
        assert "Agent2" in failed
        assert "Agent3" in failed

    def test_is_converged_success(self):
        """Test convergence detection - success case."""
        ctx = ResumeEngineContext()

        ctx.record_result("Agent1", passed=True)
        ctx.record_result("Agent2", passed=True)

        assert ctx.is_converged() is True

    def test_is_converged_failure(self):
        """Test convergence detection - failure case."""
        ctx = ResumeEngineContext()

        ctx.record_result("Agent1", passed=True)
        ctx.record_result("Agent2", passed=False)

        assert ctx.is_converged() is False

    def test_is_converged_with_critical_signal(self):
        """Test convergence detection with critical signal."""
        ctx = ResumeEngineContext()

        ctx.record_result("Agent1", passed=True)
        ctx.add_signal("QUALITY_FAILURE")

        assert ctx.is_converged() is False

    def test_record_success(self):
        """Test success recording for learning."""
        ctx = ResumeEngineContext()
        ctx.JobDescription = "Software Engineer role"

        resume_data = {"summary": "Test", "experience": "Test exp"}
        ctx.record_success(resume_data, quality_score=0.95)

        assert ctx.generation_stats["success"] == 1
        assert len(ctx.successful_generations) == 1
        assert ctx.successful_generations[0]["quality_score"] == 0.95

    def test_get_stats(self):
        """Test comprehensive stats retrieval."""
        ctx = ResumeEngineContext()
        ctx.add_signal("TEST")
        ctx.modified_sections.add("summary")

        stats = ctx.get_stats()

        assert "generation_stats" in stats
        assert "budget_stats" in stats
        assert "signals" in stats
        assert "modified_sections" in stats
        assert "TEST" in stats["signals"]
        assert "summary" in stats["modified_sections"]


def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path = None):
    """Test file - operational stub only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "TestBudgetManager"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Test file - operational stub only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
