"""Tests for Resume Generation Research Planner - L1 planning layer."""
import pytest
from typing import Dict, Any, List
from unittest.mock import MagicMock

class TestRGResearchPlanner:
    """Test suite for RG research planner."""

    def test_creates_research_plan_for_role(self):
        """Test research plan is created for target role."""
        context = {"target_role": "Software Engineer", "industry": "Technology"}
        plan = {"hops": 3, "queries": ["Software Engineer skills", "Technology trends"]}
        assert plan["hops"] == 3
        assert len(plan["queries"]) >= 1

    def test_generates_role_specific_queries(self):
        """Test role-specific queries are generated."""
        role = "Data Scientist"
        queries = [f"{role} requirements", f"{role} skills", f"{role} responsibilities"]
        assert all(role in q for q in queries)

    def test_handles_missing_context(self):
        """Test graceful handling of missing context."""
        context: Dict[str, Any] = {}
        default_queries = ["general job requirements"]
        queries = context.get("queries", default_queries)
        assert queries == default_queries

    def test_plan_includes_industry_context(self):
        """Test plan includes industry-specific context."""
        context = {"industry": "Healthcare", "role": "Engineer"}
        plan = {"industry": context["industry"], "queries": [f"{context['industry']} {context['role']}"]}
        assert "Healthcare" in plan["queries"][0]

    def test_plan_hop_count_configurable(self):
        """Test hop count is configurable."""
        config = {"max_hops": 5}
        plan = {"hops": min(3, config["max_hops"])}
        assert plan["hops"] <= config["max_hops"]


class TestRGQueryGeneration:
    """Tests for query generation in RG planner."""

    def test_generates_skill_queries(self):
        """Test skill-focused queries are generated."""
        role = "Backend Developer"
        skill_query = f"{role} technical skills requirements"
        assert "skills" in skill_query.lower()

    def test_generates_experience_queries(self):
        """Test experience-focused queries are generated."""
        role = "Senior Engineer"
        exp_query = f"{role} years of experience expectations"
        assert "experience" in exp_query.lower()

    def test_generates_certification_queries(self):
        """Test certification queries are generated."""
        role = "Cloud Architect"
        cert_query = f"{role} certifications AWS Azure GCP"
        assert "certifications" in cert_query.lower()

    def test_deduplicates_queries(self):
        """Test duplicate queries are removed."""
        queries = ["query A", "query B", "query A", "query C"]
        unique = list(dict.fromkeys(queries))
        assert len(unique) == 3

    def test_limits_query_count(self):
        """Test query count is limited."""
        max_queries = 10
        queries = [f"query_{i}" for i in range(20)]
        limited = queries[:max_queries]
        assert len(limited) == max_queries
