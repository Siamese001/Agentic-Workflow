"""
Test Neo4j integration for L2 execution modules

Tests that Neo4j integration works correctly and gracefully handles
missing Neo4j driver or connection issues.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, UTC
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from l4.temporal_schemas import (
    TemporalEntity,
    TemporalTriplet,
    TemporalEvent,
    TemporalRange,
)


class TestNeo4jIntegration:
    """Test Neo4j integration components."""

    def test_graph_query_imports(self):
        """Test that graph_query module imports correctly."""
        from graph_query import graph_query
        assert callable(graph_query)

    def test_graph_query_without_neo4j(self):
        """Test graph_query gracefully handles missing Neo4j."""
        from graph_query import graph_query
        
        with patch('graph_query._NEO4J_AVAILABLE', False):
            with pytest.raises(ImportError, match="Neo4j driver not installed"):
                graph_query("MATCH (n) RETURN n")

    def test_factual_qa_imports(self):
        """Test that factual_qa module imports correctly."""
        from l2.factual_qa import factual_qa, trend_analysis
        assert callable(factual_qa)
        assert callable(trend_analysis)

    def test_factual_qa_without_neo4j(self):
        """Test factual_qa gracefully handles missing Neo4j."""
        from l2.factual_qa import factual_qa
        
        with patch('l2.factual_qa._NEO4J_AVAILABLE', False):
            result = factual_qa(
                "test_company",
                "2020-01-01T00:00:00Z",
                "2023-01-01T00:00:00Z",
                "WORKED_AT"
            )
            assert "Neo4j driver not installed" in result

    def test_trend_analysis_without_neo4j(self):
        """Test trend_analysis gracefully handles missing Neo4j."""
        from l2.factual_qa import trend_analysis
        
        with patch('l2.factual_qa._NEO4J_AVAILABLE', False):
            result = trend_analysis(
                ["company1", "company2"],
                ["WORKED_AT", "HAS_SKILL"],
                "2020-01-01T00:00:00Z",
                "2023-01-01T00:00:00Z"
            )
            assert "Neo4j driver not installed" in result

    def test_kg_writer_imports(self):
        """Test that kg_writer module imports correctly."""
        from l2.kg_writer import (
            insert_entity,
            insert_triplet,
            insert_event,
            batch_process_invalidation,
            ingest_transcript
        )
        assert callable(insert_entity)
        assert callable(insert_triplet)
        assert callable(insert_event)
        assert callable(batch_process_invalidation)
        assert callable(ingest_transcript)

    @pytest.mark.asyncio
    async def test_kg_writer_without_neo4j(self):
        """Test kg_writer gracefully handles missing Neo4j."""
        from l2.kg_writer import insert_entity, insert_triplet, insert_event
        
        # Create test data
        entity = TemporalEntity(
            entity_id="test_entity",
            entity_type="organization",
            canonical_id="canonical_1",
            aliases={"Test Corp", "Test Company"},
        )
        
        triplet = TemporalTriplet(
            triplet_id="test_triplet",
            subject="user_1",
            predicate="WORKED_AT",
            object="test_entity",
            temporal_range=TemporalRange(valid_at=datetime.now(UTC)),
        )
        
        event = TemporalEvent(
            event_id="test_event",
            event_type="invalidation",
            triplet_id="test_triplet",
        )
        
        with patch('l2.kg_writer._NEO4J_AVAILABLE', False):
            # These should not raise exceptions when Neo4j is unavailable
            await insert_entity(entity)
            await insert_triplet(triplet)
            await insert_event(event)

    def test_neo4j_graph_store_imports(self):
        """Test that Neo4jGraphStore imports correctly."""
        try:
            from graph_store_neo4j import Neo4jGraphStore
            assert Neo4jGraphStore is not None
        except ImportError:
            # Expected if neo4j driver not installed
            pytest.skip("Neo4j driver not installed")

    def test_neo4j_graph_store_without_driver(self):
        """Test Neo4jGraphStore gracefully handles missing driver."""
        with patch('graph_store_neo4j.GraphDatabase', None):
            from graph_store_neo4j import Neo4jGraphStore
            
            with pytest.raises(ImportError, match="Neo4j driver not installed"):
                Neo4jGraphStore()

    def test_ingestion_dag_imports(self):
        """Test that kg_ingestion_dag imports with Neo4j components."""
        try:
            from orchestration.kg_ingestion_dag import (
                UnifiedKGIngestionDAG,
                IngestionStage,
                ingest_documents
            )
            assert UnifiedKGIngestionDAG is not None
            assert IngestionStage is not None
            assert callable(ingest_documents)
        except ImportError as e:
            pytest.fail(f"kg_ingestion_dag should import successfully: {e}")

    @pytest.mark.asyncio
    async def test_ingestion_dag_mirroring_methods(self):
        """Test that ingestion DAG mirroring methods exist and are callable."""
        from orchestration.kg_ingestion_dag import (
            _mirror_entities_to_neo4j,
            _mirror_triplets_to_neo4j,
            _mirror_invalidations_to_neo4j,
            _mirror_complete_transcript_to_neo4j,
        )
        
        # These should be callable and not raise exceptions
        await _mirror_entities_to_neo4j({})
        await _mirror_triplets_to_neo4j({})
        await _mirror_invalidations_to_neo4j({})
        await _mirror_complete_transcript_to_neo4j({})

    def test_requirements_includes_neo4j(self):
        """Test that requirements.txt includes Neo4j dependency."""
        import os
        # Get the project root directory (2 levels up from tests/L2_execution/)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        requirements_path = os.path.join(project_root, "requirements.txt")
        
        with open(requirements_path, "r") as f:
            requirements = f.read()
        
        assert "neo4j>=5.22.0" in requirements

    def test_all_modules_import_without_neo4j(self):
        """Test that all new Neo4j modules can be imported without Neo4j driver."""
        modules_to_test = [
            "graph_query",
            "graph_store_neo4j",
            "l2.kg_writer",
            "l2.factual_qa",
            "orchestration.kg_ingestion_dag",
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Module {module_name} should import without Neo4j driver: {e}")
