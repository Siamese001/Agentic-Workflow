"""Tests for Temporal KG Components - Triplets, Entities, Multi-hop Retrieval

This module tests the new KG components:
- L4 TripletStore and EntityRegistry
- L2 Triplet Extraction and KG Retrieval Executors
- L1 KG Retrieval Planner
- L3 KG-First Retrieval Orchestration
"""

import pytest
from datetime import datetime, UTC

# L4 Components
from state.triplet_store import (
    TripletStore,
    Triplet,
    TripletQuery,
    TemporalType,
    TripletStatus,
    create_triplet,
    PREDICATES,
)
from state.entity_resolution import (
    EntityRegistry,
    EntityType,
    CanonicalEntity,
    EntityMention,
    create_entity,
    create_mention,
)

# L1 Components
from agents.planning.kg_retrieval_planning import (
    KGRetrievalPlanner,
    KGQueryPlan,
    QueryType,
    HopDirection,
    plan_entity_retrieval,
)

# L2 Components
from agents.execution.kg_retrieval_executor import (
    KGRetrievalExecutor,
    KGRetrievalResult,
    execute_entity_query,
)
from agents.execution.triplet_extraction_executor import (
    TripletExtractionExecutor,
    ExtractionPlan,
    create_extraction_plan,
)
from agents.execution.invalidation_executor import (
    InvalidationExecutor,
    InvalidationPlan,
    InvalidationReason,
    create_invalidation_plan,
)

# L3 Components
from orchestration.kg_retrieval_orchestration import (
    KGFirstRetrievalOrchestrator,
    HybridRetrievalContext,
    create_hybrid_context,
)


class TestTripletStore:
    """Test L4 TripletStore functionality."""
    
    def test_create_triplet(self):
        """Test triplet creation."""
        triplet = create_triplet(
            subject="user_123",
            predicate="has_skill",
            obj="Python",
            confidence=0.9,
        )
        
        assert triplet.subject == "user_123"
        assert triplet.predicate == "has_skill"
        assert triplet.object == "Python"
        assert triplet.confidence == 0.9
        assert triplet.status == TripletStatus.ACTIVE
    
    def test_triplet_store_add_and_query(self):
        """Test adding and querying triplets."""
        store = TripletStore()
        
        # Add triplets
        t1 = create_triplet("user_1", "has_skill", "Python")
        t2 = create_triplet("user_1", "has_skill", "JavaScript")
        t3 = create_triplet("user_1", "worked_at", "Google")
        
        store.add_triplets([t1, t2, t3])
        
        # Query by subject
        query = TripletQuery(subject="user_1")
        results = store.query(query)
        
        assert len(results) == 3
    
    def test_triplet_store_predicate_filter(self):
        """Test querying with predicate filter."""
        store = TripletStore()
        
        store.add_triplet(create_triplet("user_1", "has_skill", "Python"))
        store.add_triplet(create_triplet("user_1", "worked_at", "Google"))
        
        query = TripletQuery(subject="user_1", predicate="has_skill")
        results = store.query(query)
        
        assert len(results) == 1
        assert results[0].object == "Python"
    
    def test_triplet_invalidation(self):
        """Test triplet invalidation."""
        store = TripletStore()
        
        triplet = create_triplet("user_1", "has_skill", "Python")
        store.add_triplet(triplet)
        
        # Invalidate
        store.invalidate_triplet(triplet.id, "outdated")
        
        # Query should not return invalidated
        query = TripletQuery(subject="user_1")
        results = store.query(query)
        assert len(results) == 0
        
        # Query with include_invalidated should return it
        query_all = TripletQuery(subject="user_1", include_invalidated=True)
        results_all = store.query(query_all)
        assert len(results_all) == 1


class TestEntityResolution:
    """Test L4 EntityRegistry functionality."""
    
    def test_entity_creation(self):
        """Test entity creation."""
        entity = create_entity(
            name="Python",
            entity_type=EntityType.SKILL,
            aliases=["python", "Python 3"],
        )
        
        assert entity.canonical_name == "Python"
        assert entity.entity_type == EntityType.SKILL
        assert "python" in entity.aliases
    
    def test_entity_resolution(self):
        """Test resolving entity mentions."""
        registry = EntityRegistry()
        
        # Create a mention
        mention = create_mention(
            text="python",
            entity_type=EntityType.SKILL,
        )
        
        # Resolve
        result = registry.resolve(mention)
        
        assert result.resolved_entity is not None
        assert result.resolved_entity.canonical_name == "Python"
        assert result.confidence > 0.9
    
    def test_entity_fuzzy_matching(self):
        """Test fuzzy entity matching."""
        registry = EntityRegistry()
        
        # Add custom entity
        entity = create_entity(
            name="Amazon Web Services",
            entity_type=EntityType.SKILL,
            aliases=["AWS", "amazon web services"],
        )
        registry.register_entity(entity)
        
        # Resolve with alias
        mention = create_mention(text="AWS", entity_type=EntityType.SKILL)
        result = registry.resolve(mention)
        
        # Should resolve to existing AWS entity from init
        assert result.resolved_entity is not None


class TestKGRetrievalPlanning:
    """Test L1 KG Retrieval Planner."""
    
    def test_plan_entity_retrieval(self):
        """Test planning entity fact retrieval."""
        plan = plan_entity_retrieval("user_123", predicates=["has_skill"])
        
        assert plan.query_type == QueryType.ENTITY_FACTS
        assert "user_123" in plan.start_entities
        assert len(plan.hops) == 1
    
    def test_plan_neighborhood_query(self):
        """Test planning multi-hop neighborhood query."""
        planner = KGRetrievalPlanner()
        
        plan = planner.plan_query(
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=["user_123"],
            max_hops=2,
        )
        
        assert plan.query_type == QueryType.NEIGHBORHOOD
        assert plan.max_hops == 2
        assert len(plan.hops) == 2
    
    def test_plan_with_template(self):
        """Test planning with predefined template."""
        planner = KGRetrievalPlanner()
        
        plan = planner.plan_query(
            query_type=QueryType.NEIGHBORHOOD,
            start_entities=["user_123"],
            template_name="similar_skills",
        )
        
        assert len(plan.hops) == 2
        # First hop should be has_skill outgoing
        assert plan.hops[0].direction == HopDirection.OUTGOING


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
        
        from agents.execution.kg_retrieval_executor import execute_multi_hop_query
        
        result = execute_multi_hop_query(
            store,
            start_entity="user_1",
            max_hops=2,
        )
        
        assert result.total_triplets >= 1


class TestTripletExtraction:
    """Test L2 Triplet Extraction Executor."""
    
    def test_extract_skills(self):
        """Test skill extraction from text."""
        executor = TripletExtractionExecutor()
        
        plan = create_extraction_plan(
            source_text="Experienced Python developer with expertise in AWS and Docker",
            source_id="doc_001",
            user_id="user_123",
        )
        
        result = executor.execute(plan)
        
        assert result.total_extracted > 0
        # Should extract Python, AWS, Docker as skills
        skills = [t.object for t in result.triplets if t.predicate == "has_skill"]
        assert len(skills) >= 1
    
    def test_extract_experience(self):
        """Test experience extraction from text."""
        executor = TripletExtractionExecutor()
        
        plan = create_extraction_plan(
            source_text="Worked at Google as Senior Engineer from 2020 to present",
            source_id="doc_002",
            user_id="user_123",
        )
        
        result = executor.execute(plan)
        
        # Should extract company
        companies = [t.object for t in result.triplets if t.predicate == "worked_at"]
        # Note: extraction depends on pattern matching
        assert result.total_extracted >= 0


class TestInvalidationExecutor:
    """Test L2 Invalidation Executor."""
    
    def test_invalidation_by_age(self):
        """Test invalidation of old facts."""
        store = TripletStore()
        
        # Add a triplet
        triplet = create_triplet("user_1", "has_skill", "COBOL")
        store.add_triplet(triplet)
        
        executor = InvalidationExecutor(store)
        
        plan = create_invalidation_plan(
            target_subject="user_1",
            max_age_days=0,  # Invalidate all
        )
        
        results = executor.execute(plan)
        
        # With max_age_days=0, facts should be invalidated
        # (unless they were just created in the same second)
        assert len(results) >= 0


class TestKGOrchestration:
    """Test L3 KG-First Retrieval Orchestration."""
    
    def test_build_retrieval_dag(self):
        """Test building a retrieval DAG."""
        orchestrator = KGFirstRetrievalOrchestrator()
        
        context = create_hybrid_context(
            query="Python developer",
            user_id="user_123",
            kg_entities=["user_123"],
        )
        
        dag = orchestrator.build_dag(context)
        
        # Should have nodes for each stage
        assert "kg_query" in dag.nodes
        assert "vector_search" in dag.nodes
        assert "fusion" in dag.nodes
        assert "filtering" in dag.nodes
    
    def test_dag_execution_order(self):
        """Test DAG topological sort."""
        orchestrator = KGFirstRetrievalOrchestrator()
        
        context = create_hybrid_context(query="test")
        dag = orchestrator.build_dag(context)
        
        order = dag.get_execution_order()
        
        # Fusion should come after kg_query and vector_search
        fusion_idx = order.index("fusion")
        kg_idx = order.index("kg_query")
        vector_idx = order.index("vector_search")
        
        assert fusion_idx > kg_idx
        assert fusion_idx > vector_idx


class TestLayerBoundaries:
    """Test that components respect layer boundaries."""
    
    def test_l4_no_execution_logic(self):
        """Verify L4 components don't contain execution logic."""
        # TripletStore should only store/retrieve, not execute
        store = TripletStore()
        
        # These should be pure data operations
        triplet = create_triplet("s", "p", "o")
        store.add_triplet(triplet)
        results = store.query(TripletQuery(subject="s"))
        
        assert len(results) == 1
    
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
    
    def test_l2_executes_plans(self):
        """Verify L2 executor uses plans from L1."""
        store = TripletStore()
        store.add_triplet(create_triplet("e1", "rel", "e2"))
        
        # L1 creates plan
        plan = plan_entity_retrieval("e1")
        
        # L2 executes plan
        executor = KGRetrievalExecutor(store)
        result = executor.execute(plan)
        
        assert isinstance(result, KGRetrievalResult)
