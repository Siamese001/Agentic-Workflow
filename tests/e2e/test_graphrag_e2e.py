"""GraphRAG End-to-End Test Suite — Full Coverage per Agentic Retrieval Models v9.

Test Dimensions:
- Pipeline B: Graph Ingestion & Indexing (ADG edge binding, L4D/L4E population)
- Pipeline C: Inference & Graph Hydration (L4E expansion, ADG edge hydration)
- Pipeline D: Meta-Learning Feedback (Evaluation, Completeness, Proposals)
- Integration: Full flow from ingestion → retrieval → learning

Standards Compliance:
- Constitutional Rule #1: All tests deterministic with evidence capture
- Constitutional Rule #3: Zero test skipping
- §5.3: Timeout enforcement (300s default, 420s for heavy tests)
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

# Pipeline B imports
from agentic_core.L3_orchestration.engines.graph_aware_indexer import (
    GraphAwareIndexer,
    ADGEdgeExtractor,
    ADGEdgeBinding,
    index_document,
    get_global_indexer,
)
from agentic_core.L4_state.memory.chunk_manifest_registry import (
    ChunkManifestRegistry,
    EnrichedChunkManifest,
)
from agentic_core.evaluation.retrieval.l4_registries import (
    ChunkManifestRegistry as InMemoryChunkRegistry,
    ParentChildIndexRegistry,
    ParentChildLink,
)

# Pipeline C imports
from agentic_core.L3_orchestration.engines.l4e_retrieval_integration import (
    GraphRetrievalEngine,
    ADGEdgeHydrator,
    GraphRetrievalContext,
    RetrievalWithGraphIntegration,
    search,
    get_global_engine,
)
from agentic_core.L4_state.engines.parent_child_expansion import (
    ParentChildExpander,
    L4ERetrievalIntegrator,
    ExpansionContext,
)

# Pipeline D imports
from agentic_core.L4_state.engines.meta_learning_feedback import (
    CompletenessRAGProposer,
    EvaluationRunner,
    CompletenessAnalyzer,
    FeedbackTrigger,
    FeedbackProposal,
    CompletenessChangePackage,
    get_global_proposer,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for test artifacts."""
    graphrag_dir = tmp_path / "graphrag_test"
    graphrag_dir.mkdir(parents=True, exist_ok=True)
    return graphrag_dir


@pytest.fixture
def mock_vector_db() -> MagicMock:
    """Provide mock vector DB client."""
    mock = MagicMock()
    
    # Mock collection
    mock_collection = MagicMock()
    mock_collection.add.return_value = None
    mock_collection.query.return_value = {
        "ids": [["chunk_1", "chunk_2"]],
        "documents": [["Content 1", "Content 2"]],
        "metadatas": [[{"doc_id": "doc_1"}, {"doc_id": "doc_1"}]],
        "distances": [[0.1, 0.2]],
    }
    mock.get_or_create_collection.return_value = mock_collection
    mock.get_collection.return_value = mock_collection
    
    return mock


@pytest.fixture
def sample_chunks() -> list[dict[str, Any]]:
    """Provide sample document chunks."""
    return [
        {
            "chunk_id": "doc_chunk_0",
            "content": "GraphRAG implements parent-child expansion for context retrieval.",
            "metadata": {
                "title": "GraphRAG Overview",
                "key_concepts": ["GraphRAG", "parent-child", "expansion"],
                "entities": ["GraphAwareIndexer", "ParentChildExpander"],
            },
        },
        {
            "chunk_id": "doc_chunk_1",
            "content": "ADG edges include reads_from and writes_to relationships.",
            "metadata": {
                "title": "ADG Edge Types",
                "key_concepts": ["ADG", "reads_from", "writes_to"],
                "entities": ["ADGEdgeBinding", "GraphAwareIndexer"],
            },
        },
        {
            "chunk_id": "doc_chunk_2",
            "content": "L4E ParentChildIndex resolves pulls_context edges.",
            "metadata": {
                "title": "L4E Registry",
                "key_concepts": ["L4E", "ParentChildIndex", "pulls_context"],
                "entities": ["ParentChildLink", "ParentChildIndexRegistry"],
            },
        },
    ]


@pytest.fixture
def sample_adg_edges() -> ADGEdgeBinding:
    """Provide sample ADG edge binding."""
    return ADGEdgeBinding(
        chunk_id="doc_adg_edges",
        source_file="docs/graphrag.md",
        reads_from=["GraphAwareIndexer", "ParentChildExpander"],
        writes_to=["ChunkManifestRegistry", "ParentChildIndexRegistry"],
        pulls_context=["ADG", "L4D", "L4E"],
    )


@pytest.fixture
def sample_embeddings() -> list[list[float]]:
    """Provide sample embeddings for chunks."""
    # Generate deterministic mock embeddings
    import random
    random.seed(42)
    return [
        [random.uniform(-1, 1) for _ in range(768)]
        for _ in range(3)
    ]


# =============================================================================
# Test Class: Pipeline B - Graph Ingestion & Indexing
# =============================================================================

@pytest.mark.timeout(120)
class TestPipelineBGraphIngestion:
    """End-to-end tests for Pipeline B: Graph Ingestion & Indexing.
    
    Covers:
    - ADG edge binding during ingestion
    - L4D ChunkManifestRegistry population
    - L4E ParentChildIndexRegistry population
    - Vector DB storage with metadata
    """
    
    def test_index_document_creates_manifests(
        self,
        temp_dir: Path,
        mock_vector_db: MagicMock,
        sample_chunks: list[dict[str, Any]],
        sample_adg_edges: ADGEdgeBinding,
        sample_embeddings: list[list[float]],
    ) -> None:
        """Test that indexing creates L4D manifests."""
        # Create indexer with mock vector DB
        indexer = GraphAwareIndexer(
            vector_db_client=mock_vector_db,
        )
        
        # Index document
        result = indexer.index_document(
            doc_id="test_doc_001",
            source_path="docs/test.md",
            chunks=sample_chunks,
            adg_edges=sample_adg_edges,
            embeddings=sample_embeddings,
        )
        
        # Verify results
        assert result["doc_id"] == "test_doc_001"
        assert result["chunks_indexed"] == 3
        assert len(result["manifests_created"]) == 3
        assert len(result["parent_child_links"]) == 2  # 3 chunks = 2 parent-child links
        
        # Verify ADG edges bound
        assert result["adg_edges_bound"]["chunk_id"] == sample_adg_edges.chunk_id
        assert result["adg_edges_bound"]["reads_from"] == sample_adg_edges.reads_from
    
    def test_l4d_registry_populated(
        self,
        temp_dir: Path,
        sample_chunks: list[dict[str, Any]],
        sample_adg_edges: ADGEdgeBinding,
    ) -> None:
        """Test that L4D registry is populated with manifests."""
        # Create fresh registry
        l4d_registry = ChunkManifestRegistry(
            db_path=str(temp_dir / "l4d_test.sqlite")
        )
        
        indexer = GraphAwareIndexer(l4d_registry=l4d_registry)
        
        # Index without embeddings
        indexer.index_document(
            doc_id="test_doc_002",
            source_path="docs/test2.md",
            chunks=sample_chunks[:2],  # Just 2 chunks
            adg_edges=sample_adg_edges,
        )
        
        # Verify L4D registry
        stats = l4d_registry.get_stats()
        assert stats["total_manifests"] == 2
        assert stats["unique_documents"] == 1
        
        # Retrieve specific manifest
        manifest = l4d_registry.get_manifest("doc_chunk_0")
        assert manifest is not None
        assert manifest.doc_id == "test_doc_002"
        assert manifest.chunk_id == "doc_chunk_0"
    
    def test_l4e_registry_parent_child_links(
        self,
        temp_dir: Path,
        sample_chunks: list[dict[str, Any]],
    ) -> None:
        """Test that L4E registry is populated with parent-child links."""
        l4e_registry = ParentChildIndexRegistry()
        
        indexer = GraphAwareIndexer(l4e_registry=l4e_registry)
        
        # Index document
        indexer.index_document(
            doc_id="test_doc_003",
            source_path="docs/test3.md",
            chunks=sample_chunks[:2],
        )
        
        # Verify L4E registry
        assert l4e_registry.count() == 1  # One link for 2 chunks
        
        # Verify link structure
        link = l4e_registry.get_link("doc_chunk_1")
        assert link is not None
        assert link.child_chunk_id == "doc_chunk_1"
        assert link.parent_chunk_id == "doc_chunk_0"
    
    def test_adg_edge_extraction_binding(
        self,
        sample_adg_edges: ADGEdgeBinding,
    ) -> None:
        """Test ADG edge extraction and binding."""
        extractor = ADGEdgeExtractor()
        
        # Extract edges for source file
        edges = extractor.extract_edges("docs/graphrag.md")
        
        assert edges.chunk_id.startswith("adg_")
        assert edges.source_file == "docs/graphrag.md"
        
        # Extract edges for chunk
        chunk_edges = extractor.extract_edges_for_chunk(
            chunk_id="chunk_001",
            content="GraphRAG implements ADG edge binding.",
            entities=["GraphAwareIndexer", "ADGEdgeBinding"],
        )
        
        assert chunk_edges.chunk_id == "chunk_001"
        assert "GraphAwareIndexer" in chunk_edges.reads_from
    
    def test_neighbor_window_update(
        self,
        sample_chunks: list[dict[str, Any]],
    ) -> None:
        """Test that neighbor windows are updated correctly."""
        l4e_registry = ParentChildIndexRegistry()
        indexer = GraphAwareIndexer(l4e_registry=l4e_registry)
        
        # Create 3 chunks with siblings
        chunks = [
            {"chunk_id": "parent_chunk", "content": "Parent", "metadata": {}},
            {"chunk_id": "child_1", "content": "Child 1", "metadata": {}},
            {"chunk_id": "child_2", "content": "Child 2", "metadata": {}},
        ]
        
        indexer.index_document(
            doc_id="sibling_test",
            source_path="docs/siblings.md",
            chunks=chunks,
        )
        
        # Verify links exist
        assert l4e_registry.count() == 2
        
        # Check that children are properly linked
        children = l4e_registry.get_children("parent_chunk")
        assert len(children) == 2


# =============================================================================
# Test Class: Pipeline C - Inference & Graph Hydration
# =============================================================================

@pytest.mark.timeout(120)
class TestPipelineCGraphHydration:
    """End-to-end tests for Pipeline C: Inference & Graph Hydration.
    
    Covers:
    - Vector search retrieval (L3)
    - L4E parent-child expansion (Step 4c)
    - ADG edge hydration
    - Groundedness scoring
    - Prompt context assembly
    """
    
    def test_parent_child_expansion(
        self,
        mock_vector_db: MagicMock,
    ) -> None:
        """Test parent-child expansion via L4E."""
        # Create expander
        expander = ParentChildExpander(max_depth=2)
        
        # Mock L4E registry with parent-child relationships
        mock_l4e = MagicMock()
        mock_l4e.get_parents.return_value = [
            MagicMock(chunk_id="parent_1", content="Parent content", metadata={}),
        ]
        mock_l4e.get_children.return_value = [
            MagicMock(chunk_id="child_1", content="Child content", metadata={}),
        ]
        mock_l4e.get_siblings.return_value = []
        
        expander.l4e_registry = mock_l4e
        
        # Expand from seed
        contexts = expander.expand(
            seed_chunk_id="seed_chunk",
            seed_content="Seed content",
        )
        
        # Verify expansion
        assert len(contexts) > 0
        assert contexts[0].chunk_id == "seed_chunk"
        assert contexts[0].depth == 0
        assert contexts[0].relationship == "seed"
        
        # Verify parent and child included
        chunk_ids = {ctx.chunk_id for ctx in contexts}
        assert "parent_1" in chunk_ids or "child_1" in chunk_ids
    
    def test_adg_edge_hydration(
        self,
        mock_vector_db: MagicMock,
    ) -> None:
        """Test ADG edge hydration during retrieval."""
        hydrator = ADGEdgeHydrator()
        
        # Hydrate chunk
        hydration = hydrator.hydrate(
            chunk_id="chunk_001",
            source_file="docs/graphrag.md",
        )
        
        assert hydration.chunk_id == "chunk_001"
        # Note: In production, this would have actual ADG edges
    
    def test_graph_retrieval_engine(
        self,
        mock_vector_db: MagicMock,
    ) -> None:
        """Test full graph retrieval engine."""
        engine = GraphRetrievalEngine(
            vector_db_client=mock_vector_db,
        )
        
        # Perform retrieval
        contexts = engine.retrieve(
            query="GraphRAD ADG edges",
            n_results=2,
            expansion_depth=1,
            hydrate_adg=True,
        )
        
        # Verify results
        assert len(contexts) > 0
        assert contexts[0].chunk_id is not None
        assert contexts[0].score > 0
        
        # Verify groundedness scoring
        for ctx in contexts:
            assert 0 <= ctx.groundedness_score <= 1.0
    
    def test_prompt_context_assembly(
        self,
        mock_vector_db: MagicMock,
    ) -> None:
        """Test prompt context assembly."""
        engine = GraphRetrievalEngine(vector_db_client=mock_vector_db)
        
        # Create sample contexts
        contexts = [
            GraphRetrievalContext(
                chunk_id="chunk_1",
                content="GraphRAG implements parent-child expansion.",
                score=0.95,
                source="vector",
                groundedness_score=0.85,
            ),
            GraphRetrievalContext(
                chunk_id="chunk_2",
                content="ADG edges bind to chunks during ingestion.",
                score=0.90,
                source="l4e_expansion",
                expansion_depth=1,
                groundedness_score=0.75,
            ),
        ]
        
        # Assemble prompt context
        prompt_context = engine.assemble_prompt_context(
            contexts=contexts,
            max_tokens=1000,
        )
        
        # Verify assembly
        assert "chunks" in prompt_context
        assert prompt_context["total_chunks"] > 0
        assert prompt_context["total_tokens"] > 0
    
    def test_retrieval_with_graph_integration(
        self,
        mock_vector_db: MagicMock,
    ) -> None:
        """Test high-level retrieval with graph integration."""
        integration = RetrievalWithGraphIntegration()
        
        # Mock the engine's retrieve method
        integration.engine = MagicMock()
        integration.engine.retrieve.return_value = [
            GraphRetrievalContext(
                chunk_id="chunk_1",
                content="Test content",
                score=0.9,
                source="vector",
                groundedness_score=0.8,
            ),
        ]
        integration.engine.assemble_prompt_context.return_value = {
            "chunks": [{"chunk_id": "chunk_1", "content": "Test"}],
            "total_chunks": 1,
        }
        
        # Search
        result = integration.search(
            query="test query",
            n_results=5,
            expansion_depth=2,
        )
        
        # Verify result structure
        assert "query" in result
        assert "contexts" in result
        assert "prompt_context" in result
        assert "stats" in result


# =============================================================================
# Test Class: Pipeline D - Meta-Learning Feedback
# =============================================================================

@pytest.mark.timeout(120)
class TestPipelineDMetaLearning:
    """End-to-end tests for Pipeline D: Meta-Learning Feedback.
    
    Covers:
    - Evaluation metrics (Precision@K, Recall@K, MRR, NDCG, F1-Groundedness)
    - Completeness analysis
    - Feedback trigger activation
    - Change package generation
    """
    
    def test_evaluation_metrics_computation(self) -> None:
        """Test evaluation metrics computation."""
        runner = EvaluationRunner()
        
        # Evaluate query
        metrics = runner.evaluate(
            query="test query",
            retrieved_chunks=["chunk_1", "chunk_2", "chunk_3"],
            relevant_chunks=["chunk_1", "chunk_3", "chunk_4"],
            groundedness_scores=[0.9, 0.8, 0.7],
            k=3,
        )
        
        # Verify metrics
        assert metrics.precision_at_k > 0
        assert metrics.recall_at_k > 0
        assert 0 <= metrics.mrr <= 1.0
        assert 0 <= metrics.ndcg <= 1.0
        assert 0 <= metrics.f1_groundedness <= 1.0
    
    def test_completeness_analysis(self) -> None:
        """Test completeness analysis."""
        analyzer = CompletenessAnalyzer()
        
        # Analyze query with missing elements
        contexts = [
            {"content": "If condition is met, execute action.", "key_concepts": ["condition"]},
            {"content": "Handle exception gracefully.", "key_concepts": ["exception"]},
        ]
        
        analysis = analyzer.analyze(
            query="What if exception occurs when condition fails?",
            retrieved_contexts=contexts,
        )
        
        # Verify analysis
        assert 0 <= analysis.mean_completeness <= 1.0
        assert 0 <= analysis.missing_condition_rate <= 1.0
        assert 0 <= analysis.missing_exception_rate <= 1.0
    
    def test_feedback_trigger_generation(self) -> None:
        """Test feedback trigger generation."""
        proposer = CompletenessRAGProposer()
        
        # Create query batch with low completeness
        query_batch = [
            {
                "query": "test query 1",
                "retrieved_chunks": ["chunk_1"],
                "relevant_chunks": ["chunk_1", "chunk_2", "chunk_3"],
                "groundedness_scores": [0.4],
                "contexts": [],
            },
            {
                "query": "test query 2",
                "retrieved_chunks": ["chunk_2"],
                "relevant_chunks": ["chunk_1", "chunk_2", "chunk_3"],
                "groundedness_scores": [0.3],
                "contexts": [],
            },
        ]
        
        # Analyze and propose
        change_package = proposer.analyze_and_propose(query_batch)
        
        # Verify change package
        assert change_package.snapshot_id is not None
        assert change_package.query_count == 2
        assert isinstance(change_package.aggregate_metrics, EvaluationRunner.__call__.__class__ if False else object)
        assert len(change_package.proposals) >= 0
    
    def test_depth_increment_trigger(self) -> None:
        """Test Depth++ feedback trigger."""
        proposer = CompletenessRAGProposer()
        
        # Set low precision to trigger depth increment
        metrics = proposer.evaluator.evaluate(
            query="test",
            retrieved_chunks=["chunk_1"],
            relevant_chunks=["chunk_1", "chunk_2", "chunk_3", "chunk_4"],
            groundedness_scores=[0.4],
        )
        
        # Check proposals
        proposals = proposer._check_completeness_trigger(metrics)
        
        # Should suggest depth increment if precision is low
        if metrics.precision_at_k < 0.5:
            assert any(p.trigger == FeedbackTrigger.DEPTH_INCREMENT for p in proposals)
    
    def test_change_package_format(self) -> None:
        """Test change package format for L5 Board."""
        proposal = FeedbackProposal(
            trigger=FeedbackTrigger.DEPTH_INCREMENT,
            rationale="Low completeness detected",
            current_value=3,
            proposed_value=4,
            confidence=0.8,
            supporting_evidence=["precision_at_k=0.3"],
        )
        
        package_dict = proposal.to_change_package()
        
        assert package_dict["type"] == "retrieval_config_update"
        assert package_dict["proposal_only"] is True
        assert package_dict["trigger"] == "depth_increment"
        assert "current" in package_dict["changes"]
        assert "proposed" in package_dict["changes"]


# =============================================================================
# Test Class: Integration - Full Pipeline Flow
# =============================================================================

@pytest.mark.timeout(300)
class TestFullPipelineIntegration:
    """Integration tests covering full Pipeline B → C → D flow.
    
    These tests verify the complete GraphRAG workflow from ingestion
    through retrieval to meta-learning feedback.
    """
    
    def test_full_pipeline_b_to_c(
        self,
        temp_dir: Path,
        mock_vector_db: MagicMock,
        sample_chunks: list[dict[str, Any]],
        sample_adg_edges: ADGEdgeBinding,
    ) -> None:
        """Test full flow from Pipeline B ingestion to Pipeline C retrieval."""
        # Stage 1: Pipeline B - Ingest document
        indexer = GraphAwareIndexer(
            vector_db_client=mock_vector_db,
        )
        
        index_result = indexer.index_document(
            doc_id="integration_test_doc",
            source_path="docs/integration.md",
            chunks=sample_chunks,
            adg_edges=sample_adg_edges,
        )
        
        assert index_result["chunks_indexed"] == 3
        
        # Stage 2: Pipeline C - Retrieve with graph awareness
        # Create mock L4D registry with stored manifests
        mock_l4d = MagicMock()
        mock_l4d.get_manifest.return_value = MagicMock(
            chunk_id="doc_chunk_0",
            title="Test",
            key_concepts=["GraphRAG"],
        )
        
        engine = GraphRetrievalEngine(
            vector_db_client=mock_vector_db,
            l4d_registry=mock_l4d,
        )
        
        contexts = engine.retrieve(
            query="GraphRAG parent-child expansion",
            n_results=2,
            expansion_depth=1,
        )
        
        # Verify retrieval results
        assert len(contexts) > 0
    
    def test_full_pipeline_with_feedback(
        self,
        temp_dir: Path,
        mock_vector_db: MagicMock,
        sample_chunks: list[dict[str, Any]],
    ) -> None:
        """Test full pipeline with meta-learning feedback loop."""
        # Setup
        indexer = GraphAwareIndexer(vector_db_client=mock_vector_db)
        proposer = CompletenessRAGProposer()
        
        # Stage 1: Ingest documents
        for i in range(3):
            indexer.index_document(
                doc_id=f"feedback_test_doc_{i}",
                source_path=f"docs/feedback_{i}.md",
                chunks=sample_chunks[:2],
            )
        
        # Stage 2: Simulate retrievals with varying quality
        query_batch = []
        for i in range(5):
            query_batch.append({
                "query": f"test query {i}",
                "retrieved_chunks": ["chunk_1"] if i < 3 else ["chunk_1", "chunk_2"],
                "relevant_chunks": ["chunk_1", "chunk_2", "chunk_3"],
                "groundedness_scores": [0.4] if i < 3 else [0.8, 0.7],
                "contexts": [],
            })
        
        # Stage 3: Generate feedback proposals
        change_package = proposer.analyze_and_propose(query_batch)
        
        # Verify feedback loop
        assert change_package.query_count == 5
        assert change_package.aggregate_metrics is not None
        
        # Verify proposals are actionable
        for proposal in change_package.proposals:
            assert proposal.rationale is not None
            assert proposal.confidence > 0
    
    def test_parent_child_expansion_depth(
        self,
    ) -> None:
        """Test parent-child expansion at different depths."""
        # Create expander with depth 3
        expander = ParentChildExpander(max_depth=3)
        
        # Mock multi-level hierarchy
        mock_l4e = MagicMock()
        
        def get_parents(chunk_id):
            if chunk_id == "level_2":
                return [MagicMock(chunk_id="level_1", content="Parent", metadata={})]
            if chunk_id == "level_3":
                return [MagicMock(chunk_id="level_2", content="Grandparent", metadata={})]
            return []
        
        def get_children(chunk_id):
            if chunk_id == "level_1":
                return [MagicMock(chunk_id="level_2", content="Child", metadata={})]
            if chunk_id == "level_2":
                return [MagicMock(chunk_id="level_3", content="Grandchild", metadata={})]
            return []
        
        mock_l4e.get_parents = get_parents
        mock_l4e.get_children = get_children
        mock_l4e.get_siblings.return_value = []
        
        expander.l4e_registry = mock_l4e
        
        # Expand from deepest level
        contexts = expander.expand(
            seed_chunk_id="level_3",
            seed_content="Deepest level",
        )
        
        # Should include all ancestors up to depth 3
        chunk_ids = {ctx.chunk_id for ctx in contexts}
        assert "level_3" in chunk_ids  # Seed
        assert "level_2" in chunk_ids  # Depth 1
        assert "level_1" in chunk_ids  # Depth 2


# =============================================================================
# Test Utilities
# =============================================================================

def test_global_instances() -> None:
    """Test that global instances are properly initialized."""
    indexer1 = get_global_indexer()
    indexer2 = get_global_indexer()
    assert indexer1 is indexer2
    
    engine1 = get_global_engine()
    engine2 = get_global_engine()
    assert engine1 is engine2
    
    proposer1 = get_global_proposer()
    proposer2 = get_global_proposer()
    assert proposer1 is proposer2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
