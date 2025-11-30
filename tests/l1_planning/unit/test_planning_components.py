"""
L1 Planning Unit Tests
Tests for individual planning components
"""

import pytest
from agentic_core.l1_planning import StrategyPlanner, MessagePlanner, ResearchPlanner, RefinementPlanner, SafetyPlanner


class TestStrategyPlanner:
    """Test StrategyPlanner functionality"""
    
    def test_strategy_planner_init(self):
        """Test StrategyPlanner initialization"""
        planner = StrategyPlanner()
        assert planner is not None
    
    def test_basic_strategy_creation(self):
        """Test basic strategy creation"""
        planner = StrategyPlanner()
        # Add basic strategy creation test here
        assert True


class TestMessagePlanner:
    """Test MessagePlanner functionality"""
    
    def test_message_planner_init(self):
        """Test MessagePlanner initialization"""
        planner = MessagePlanner()
        assert planner is not None


class TestResearchPlanner:
    """Test ResearchPlanner functionality"""
    
    def test_research_planner_init(self):
        """Test ResearchPlanner initialization"""
        planner = ResearchPlanner()
        assert planner is not None


class TestRefinementPlanner:
    """Test RefinementPlanner functionality"""
    
    def test_refinement_planner_init(self):
        """Test RefinementPlanner initialization"""
        planner = RefinementPlanner()
        assert planner is not None


class TestSafetyPlanner:
    """Test SafetyPlanner functionality"""
    
    def test_safety_planner_init(self):
        """Test SafetyPlanner initialization"""
        planner = SafetyPlanner()
        assert planner is not None
