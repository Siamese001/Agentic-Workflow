"""Phase F Integration Tests - V6 Prompts + Hybrid Search + Temporal KG

This module tests the full integration of:
- V6 prompts with L1/L2 agents
- Hybrid search with metadata filtering
- Temporal KG integration
- End-to-end workflows
"""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, MagicMock, patch

from l1.v6_prompt_adapter import (
    build_v6_strategy_prompt,
    build_v6_rag_prompt,
    build_v6_qa_prompt,
    build_v6_safety_prompt,
    V6PromptConfig,
)
from l4.hybrid_search import (
    HybridSearchExecutor,
    HybridSearchConfig,
    SearchFilter,
    TemporalFilter,
    SearchResult,
    create_category_filter,
    create_recent_filter,
)
from l4.temporal_kg import (
    TemporalKG,
    TemporalFact,
    TemporalQuery,
    create_skill_fact,
    create_experience_fact,
    create_application_fact,
)
from core.models.models import ExecutionContext, JobInput, ResumeInput, WorkflowConfig


def _create_test_context(**kwargs):
    """Helper to create ExecutionContext with required fields for tests."""
    defaults = {
        "job": JobInput(
            title="Software Engineer",
            role_type="engineering", 
            seniority="mid",
            posting_text="Looking for a software engineer"
        ),
        "resume": ResumeInput(
            full_text="John Doe\nSoftware Engineer\nPython, JavaScript",
            sections={}
        ),
        "config": WorkflowConfig(),
        "prompt_registry": {},
        "user_id": "user_123",
        "job_id": "job_456",
        "workflow_id": "wf_789",
    }
    defaults.update(kwargs)
    return ExecutionContext(**defaults)


class TestV6PromptIntegration:
    """Test v6 prompt integration with L1 planners."""
    
    def test_build_v6_strategy_prompt(self):
        """Test v6 strategy prompt building."""
        # Create mock context
        ctx = _create_test_context(
        )
        
        job = Mock()
        job.title = "Senior Engineer"
        job.company = "TechCo"
        
        resume = Mock()
        resume.name = "John Doe"
        
        config = Mock()
        
        # Build prompt
        prompt = build_v6_strategy_prompt(
            ctx=ctx,
            job=job,
            resume=resume,
            config=config,
        )
        
        # Verify prompt structure
        assert "AGENT IDENTITY" in prompt
        assert "Strategy Planner" in prompt
        assert "CURRENT CONTEXT" in prompt
        assert "Senior Engineer" in prompt
        assert "TechCo" in prompt
        assert "John Doe" in prompt
    
    def test_build_v6_rag_prompt(self):
        """Test v6 RAG prompt building."""
        ctx = _create_test_context()
        rag_plan = Mock()
        rag_plan.top_k = 10
        
        prompt = build_v6_rag_prompt(ctx=ctx, rag_plan=rag_plan)
        
        assert "RAG Planner" in prompt
        assert "EXTENSIONS" in prompt
        assert "RAG INTEGRATION" in prompt
    
    def test_v6_prompt_with_examples(self):
        """Test v6 prompts include examples."""
        ctx = _create_test_context()
        job = Mock()
        resume = Mock()
        config = Mock()
        
        v6_config = V6PromptConfig(include_examples=True)
        
        prompt = build_v6_strategy_prompt(
            ctx=ctx,
            job=job,
            resume=resume,
            config=config,
            v6_config=v6_config,
        )
        
        assert "## EXAMPLES" in prompt
        assert "**Input:**" in prompt
        assert "**Expected Output:**" in prompt
    
    def test_v6_prompt_without_examples(self):
        """Test v6 prompts can exclude examples."""
        ctx = _create_test_context()
        job = Mock()
        resume = Mock()
        config = Mock()
        
        v6_config = V6PromptConfig(include_examples=False)
        
        prompt = build_v6_strategy_prompt(
            ctx=ctx,
            job=job,
            resume=resume,
            config=config,
            v6_config=v6_config,
        )
        
        assert "## EXAMPLES" not in prompt


class TestHybridSearch:
    """Test hybrid search functionality."""
    
    def test_hybrid_search_config(self):
        """Test hybrid search configuration."""
        config = HybridSearchConfig(
            dense_weight=0.7,
            sparse_weight=0.3,
            final_top_k=10,
            score_threshold=0.75,
        )
        
        assert config.dense_weight == 0.7
        assert config.sparse_weight == 0.3
        assert config.final_top_k == 10
        assert config.score_threshold == 0.75
    
    def test_search_filter_creation(self):
        """Test search filter creation."""
        filter1 = create_category_filter("technical_skills")
        assert filter1.field == "category"
        assert filter1.operator == "eq"
        assert filter1.value == "technical_skills"
        
        filter2 = SearchFilter(field="score", operator="gte", value=0.8)
        assert filter2.field == "score"
        assert filter2.operator == "gte"
        assert filter2.value == 0.8
    
    def test_temporal_filter_creation(self):
        """Test temporal filter creation."""
        # Recent filter
        recent_filter = create_recent_filter(days=30)
        assert recent_filter.recent_only is True
        assert recent_filter.recent_days == 30
        
        # Date range filter
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        range_filter = TemporalFilter(start_time=start, end_time=end)
        assert range_filter.start_time == start
        assert range_filter.end_time == end
    
    @patch('l4.hybrid_search.HybridSearchExecutor._dense_search')
    @patch('l4.hybrid_search.HybridSearchExecutor._sparse_search')
    def test_hybrid_search_execution(self, mock_sparse, mock_dense):
        """Test hybrid search execution."""
        # Mock adapter
        mock_adapter = Mock()
        executor = HybridSearchExecutor(mock_adapter)
        
        # Mock search results
        mock_dense.return_value = [
            SearchResult(id="doc1", score=0.9, text="result 1", dense_score=0.9),
            SearchResult(id="doc2", score=0.8, text="result 2", dense_score=0.8),
        ]
        mock_sparse.return_value = []
        
        # Execute search
        # Note: RRF produces small scores (e.g., 0.7 / 61 ≈ 0.011), so use low threshold
        config = HybridSearchConfig(final_top_k=5, score_threshold=0.001)
        results = executor.search(
            query="Python AWS",
            namespace="test_ns",
            config=config,
        )
        
        # Verify results
        assert len(results) > 0
        assert all(r.fused_score >= 0.001 for r in results)
        mock_dense.assert_called_once()
    
    def test_hybrid_search_with_metadata_filter(self):
        """Test hybrid search with metadata filtering."""
        mock_adapter = Mock()
        executor = HybridSearchExecutor(mock_adapter)
        
        # Create config with filters
        config = HybridSearchConfig(
            filters=[
                create_category_filter("technical_skills"),
                SearchFilter(field="confidence", operator="gte", value=0.8),
            ]
        )
        
        # Build metadata filter
        metadata_filter = executor._build_metadata_filter(config)
        
        assert metadata_filter is not None
        assert "category" in metadata_filter
        assert "confidence" in metadata_filter


class TestTemporalKG:
    """Test temporal knowledge graph functionality."""
    
    def test_temporal_fact_creation(self):
        """Test temporal fact creation."""
        now = datetime.now(UTC)
        fact = TemporalFact(
            id="fact_001",
            subject="user_123",
            predicate="has_skill",
            object="Python",
            timestamp=now,
            confidence=0.95,
        )
        
        assert fact.subject == "user_123"
        assert fact.predicate == "has_skill"
        assert fact.object == "Python"
        assert fact.confidence == 0.95
    
    def test_temporal_fact_to_text(self):
        """Test fact to text conversion."""
        now = datetime.now(UTC)
        fact = TemporalFact(
            id="fact_001",
            subject="user_123",
            predicate="has_skill",
            object="Python",
            timestamp=now,
        )
        
        text = fact.to_text()
        assert "user_123" in text
        assert "has_skill" in text
        assert "Python" in text
    
    def test_create_skill_fact(self):
        """Test skill fact creation helper."""
        fact = create_skill_fact(
            user_id="user_123",
            skill="Python",
            proficiency="expert",
        )
        
        assert fact.subject == "user_123"
        assert fact.predicate == "has_skill"
        assert fact.object == "Python"
        assert fact.metadata["proficiency"] == "expert"
    
    def test_create_experience_fact(self):
        """Test experience fact creation helper."""
        fact = create_experience_fact(
            user_id="user_123",
            company="Google",
            role="Senior Engineer",
        )
        
        assert fact.subject == "user_123"
        assert fact.predicate == "worked_at"
        assert fact.object == "Google"
        assert fact.metadata["role"] == "Senior Engineer"
    
    def test_create_application_fact(self):
        """Test application fact creation helper."""
        fact = create_application_fact(
            user_id="user_123",
            job_id="job_456",
            status="interviewed",
        )
        
        assert fact.subject == "user_123"
        assert fact.predicate == "applied_to"
        assert fact.object == "job_456"
        assert fact.metadata["status"] == "interviewed"
    
    def test_temporal_query(self):
        """Test temporal query construction."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        
        query = TemporalQuery(
            subject="user_123",
            predicate="has_skill",
            start_time=start,
            end_time=end,
            min_confidence=0.8,
        )
        
        assert query.subject == "user_123"
        assert query.predicate == "has_skill"
        assert query.start_time == start
        assert query.end_time == end
        assert query.min_confidence == 0.8
    
    def test_add_fact(self):
        """Test adding a fact to temporal KG."""
        mock_adapter = Mock()
        mock_adapter.upsert_text_records = Mock()
        
        kg = TemporalKG(mock_adapter)
        
        fact = create_skill_fact("user_123", "Python")
        kg.add_fact(fact, user_id="user_123")
        
        # Verify upsert was called
        mock_adapter.upsert_text_records.assert_called_once()
    
    def test_add_facts_batch(self):
        """Test adding multiple facts in batch."""
        mock_adapter = Mock()
        mock_adapter.upsert_text_records = Mock()
        
        kg = TemporalKG(mock_adapter)
        
        facts = [
            create_skill_fact("user_123", "Python"),
            create_skill_fact("user_123", "AWS"),
            create_skill_fact("user_123", "Docker"),
        ]
        
        kg.add_facts(facts, user_id="user_123")
        
        # Verify batch upsert was called
        mock_adapter.upsert_text_records.assert_called_once()
        call_args = mock_adapter.upsert_text_records.call_args
        assert len(call_args[1]["texts"]) == 3


class TestEndToEndIntegration:
    """Test end-to-end integration of Phase F components."""
    
    def test_execution_context_with_l4_adapters(self):
        """Test ExecutionContext with L4 adapters."""
        mock_pinecone = Mock()
        # Set up mock to return a proper namespace string
        mock_pinecone.build_namespace = Mock(return_value="user_123_job_456")
        mock_state_manager = Mock()
        
        ctx = _create_test_context(
            pinecone_adapter=mock_pinecone,
            state_manager=mock_state_manager,
        )
        
        assert ctx.pinecone_adapter is not None
        assert ctx.state_manager is not None
        
        # Test namespace generation
        namespace = ctx.get_pinecone_namespace()
        assert "user_123" in namespace or "job_456" in namespace
    
    def test_v6_prompt_with_l4_context(self):
        """Test v6 prompt generation with L4 context."""
        mock_pinecone = Mock()
        mock_pinecone.build_namespace = Mock(return_value="user_123_job_456")
        
        ctx = _create_test_context(
            pinecone_adapter=mock_pinecone,
            rag_results=[{"id": "doc1"}, {"id": "doc2"}],
            temporal_kg_facts=[{"fact": "user has Python"}],
        )
        
        job = Mock()
        job.title = "Engineer"
        resume = Mock()
        config = Mock()
        
        prompt = build_v6_strategy_prompt(ctx, job, resume, config)
        
        # Verify L4 context is included
        assert "Vector Store Namespace" in prompt or "user_123" in prompt
        assert "Retrieved Evidence" in prompt or "2 items" in prompt
        assert "Temporal Facts" in prompt or "1 facts" in prompt
    
    def test_hybrid_search_with_temporal_filter(self):
        """Test hybrid search with temporal filtering."""
        mock_adapter = Mock()
        executor = HybridSearchExecutor(mock_adapter)
        
        # Create temporal filter
        temporal_filter = create_recent_filter(days=30)
        
        # Create config with temporal filter
        config = HybridSearchConfig(
            temporal_filter=temporal_filter,
            final_top_k=10,
        )
        
        # Build metadata filter
        metadata_filter = executor._build_metadata_filter(config)
        
        assert metadata_filter is not None
        assert "timestamp" in metadata_filter
    
    def test_temporal_kg_recent_facts(self):
        """Test retrieving recent facts from temporal KG."""
        mock_adapter = Mock()
        mock_adapter.query_by_text = Mock(return_value=[])
        
        kg = TemporalKG(mock_adapter)
        
        # Query recent facts
        facts = kg.get_recent_facts(
            subject="user_123",
            days=30,
            user_id="user_123",
        )
        
        # Verify query was called
        mock_adapter.query_by_text.assert_called_once()
        assert isinstance(facts, list)


class TestPhaseFQualityGates:
    """Test quality gates for Phase F implementation."""
    
    def test_all_v6_prompt_builders_exist(self):
        """Test that all v6 prompt builders are implemented."""
        from l1.v6_prompt_adapter import (
            build_v6_strategy_prompt,
            build_v6_rag_prompt,
            build_v6_qa_prompt,
            build_v6_safety_prompt,
        )
        
        # All builders should be callable
        assert callable(build_v6_strategy_prompt)
        assert callable(build_v6_rag_prompt)
        assert callable(build_v6_qa_prompt)
        assert callable(build_v6_safety_prompt)
    
    def test_hybrid_search_components_exist(self):
        """Test that all hybrid search components are implemented."""
        from l4.hybrid_search import (
            HybridSearchExecutor,
            HybridSearchConfig,
            SearchFilter,
            TemporalFilter,
            SearchResult,
        )
        
        # All classes should be instantiable
        assert HybridSearchConfig is not None
        assert SearchFilter is not None
        assert TemporalFilter is not None
        assert SearchResult is not None
        assert HybridSearchExecutor is not None
    
    def test_temporal_kg_components_exist(self):
        """Test that all temporal KG components are implemented."""
        from l4.temporal_kg import (
            TemporalKG,
            TemporalFact,
            TemporalQuery,
            create_skill_fact,
            create_experience_fact,
            create_application_fact,
        )
        
        # All classes and functions should exist
        assert TemporalKG is not None
        assert TemporalFact is not None
        assert TemporalQuery is not None
        assert callable(create_skill_fact)
        assert callable(create_experience_fact)
        assert callable(create_application_fact)
    
    def test_no_import_errors(self):
        """Test that all Phase F modules import without errors."""
        try:
            import l1.v6_prompt_adapter
            import l4.hybrid_search
            import l4.temporal_kg
            import prompts.v6_prompt_integration
            import prompts.instructional_injection_v6
            import prompts.many_shot_examples
        except ImportError as e:
            pytest.fail(f"Import error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])






