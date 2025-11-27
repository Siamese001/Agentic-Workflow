"""
Test KG Retrieval Executor

Tests knowledge graph retrieval execution functionality extracted from working legacy tests.
"""

import pytest

# L2 Components
from l2.kg_retrieval_executor import (
    KGRetrievalResult,
    execute_entity_query,
    execute_multi_hop_query,
)

# L4 Components (for storage)
from l4.triplet_store import (
    TripletStore,
    create_triplet,
)

# Mark all tests as L2 execution tests
pytestmark = [pytest.mark.unit, pytest.mark.l2, pytest.mark.execution]


class TestKGRetrievalExecutor:
    """Test L2 KG Retrieval Executor."""
    
    def test_execute_entity_query(self):
        """Test executing entity fact query."""
        store = TripletStore()
        
        # Add some triplets
        store.add_triplet(create_triplet("user_1", "has_skill", "Python"))
        store.add_triplet(create_triplet("user_1", "has_skill", "AWS"))
        store.add_triplet(create_triplet("user_1", "worked_at", "Google"))
        
        # Execute query
        result = execute_entity_query(store, "user_1")
        
        assert isinstance(result, KGRetrievalResult)
        assert result.total_triplets == 3
        assert "user_1" in result.entities
    
    def test_execute_multi_hop(self):
        """Test multi-hop neighborhood query."""
        store = TripletStore()
        
        # Build a small graph
        store.add_triplet(create_triplet("user_1", "has_skill", "Python"))
        store.add_triplet(create_triplet("job_1", "requires_skill", "Python"))
        
        result = execute_multi_hop_query(
            store,
            start_entity="user_1",
            max_hops=2,
        )
        
        assert result.total_triplets >= 1
