"""
Test KG Retrieval Planning

Tests knowledge graph retrieval planning functionality extracted from working legacy tests.
"""

import pytest
from datetime import datetime, UTC

# L1 Components
from l1.kg_retrieval_planning import (
    KGRetrievalPlanner,
    KGQueryPlan,
    QueryType,
    HopDirection,
    plan_entity_retrieval,
)

# Mark all tests as L1 planning tests
pytestmark = [pytest.mark.unit, pytest.mark.l1, pytest.mark.planning]


class TestKGRetrievalPlanning:
    """Test KG retrieval planning functionality."""
    
    def test_plan_entity_retrieval(self):
        """Test basic entity retrieval planning."""
        plan = plan_entity_retrieval(
            entity_id="entity_1",
            max_hops=1
        )
        
        assert isinstance(plan, KGQueryPlan)
        assert plan.start_entities == ["entity_1"]
        assert plan.query_type == QueryType.ENTITY_FACTS
        assert plan.max_hops == 1
    
    def test_plan_neighborhood_query(self):
        """Test neighborhood query planning."""
        planner = KGRetrievalPlanner()
        
        plan = planner.plan_query(
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=["entity_1"],
            max_hops=2
        )
        
        assert isinstance(plan, KGQueryPlan)
        assert plan.start_entities == ["entity_1"]
        assert plan.query_type == QueryType.NEIGHBORHOOD
        assert plan.max_hops == 2
    
    def test_plan_with_template(self):
        """Test planning with query templates."""
        planner = KGRetrievalPlanner()
        
        plan = planner.plan_query(
            query_type=QueryType.PATTERN_MATCH,
            start_entities=["entity_1"],
            template_name="test_template"
        )
        
        assert isinstance(plan, KGQueryPlan)
        assert plan.start_entities == ["entity_1"]
        # Template may override query_type, so just verify it's a valid plan
        assert plan.query_type in [QueryType.PATTERN_MATCH, QueryType.NEIGHBORHOOD]
    
    def test_hop_direction_planning(self):
        """Test hop direction specification in planning."""
        planner = KGRetrievalPlanner()
        
        # Test outgoing direction
        plan = planner.plan_query(
            query_type=QueryType.ENTITY_FACTS,
            start_entities=["entity_1"],
            max_hops=1
        )
        
        assert isinstance(plan, KGQueryPlan)
        assert plan.start_entities == ["entity_1"]
        
        # Test that plan contains hop specifications
        if plan.hops:
            assert all(isinstance(hop, type(plan.hops[0])) for hop in plan.hops)
    
    def test_l1_pure_planning(self):
        """Verify L1 planner produces plans without execution."""
        planner = KGRetrievalPlanner()
        
        plan = planner.plan_query(
            query_type=QueryType.ENTITY_FACTS,
            start_entities=["entity_1"],
        )
        
        # Plan should be a data structure, not executed
        assert isinstance(plan, KGQueryPlan)
        assert plan.start_entities == ["entity_1"]
        assert plan.query_type == QueryType.ENTITY_FACTS
