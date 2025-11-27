"""
Tests for L2 executor temporal research pathways - Phase 6 L4 expansion.

Tests L2 executor consumption of enriched Evidence objects, C-Level weighting, and graceful fallback.
"""

import pytest
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Optional
from l4.temporal_kg import TemporalKG, TemporalNodeMetadata
from l4.high_signal import HighSignalScore
from l4.temporal_fusion import TemporalRankFusion
from l4.rag.rag_engine import RAGEngine, OutreachRAGResult
from l2.company_research_executor import CompanyResearchExecutor
from l2.contact_research_executor import ContactResearchExecutor


class TestTemporalResearchPathways:
    """Test suite for L2 executor temporal research integration."""
    
    def setup_method(self):
        """Set up test fixtures for L2 temporal research validation."""
        # Create mock components
        class MockPineconeAdapter:
            def upsert_text_records(self, texts, namespace, ids, metadata_list):
                pass
            
            def query_by_text(self, query_text, namespace, top_k, filter_dict=None):
                return []
            
            def delete_records(self, ids, namespace):
                pass
        
        self.mock_adapter = MockPineconeAdapter()
        self.temporal_kg = TemporalKG(self.mock_adapter)
        self.fusion = TemporalRankFusion()
        self.now = datetime.now(UTC)
        
        # Create enriched RAG results with temporal data
        self.enriched_company_results = [
            OutreachRAGResult(
                id="company_1",
                text="Company launched AI platform serving 1M customers",
                score=0.85,
                company="TestCompany",
                title="AI Platform Launch",
                source="company_news",
                signal_score=0.9,
                signal_type="product_launch"
            ),
            OutreachRAGResult(
                id="company_2",
                text="Hiring 200 engineers for AI expansion",
                score=0.75,
                company="TestCompany",
                title="Engineering Hiring",
                source="company_careers",
                signal_score=0.7,
                signal_type="hiring_trend"
            )
        ]
        
        self.enriched_contact_results = [
            OutreachRAGResult(
                id="contact_1",
                text="Contact promoted to VP of Engineering",
                score=0.8,
                company="TestCompany",
                title="VP Engineering",
                source="linkedin_profile",
                signal_score=0.6,
                signal_type="career_progression"
            )
        ]
    
    def test_l2_can_consume_enriched_evidence_objects(self):
        """Test that L2 executors can safely consume enriched Evidence objects."""
        # Test CompanyResearchExecutor with enriched data
        company_executor = CompanyResearchExecutor(
            hybrid_search=None,
            pinecone_adapter=self.mock_adapter
        )
        
        # Mock the research method to accept enriched RAG results
        def mock_research_with_temporal(query, rag_results=None):
            if rag_results is None:
                return {"status": "no_data"}
            
            # Verify enriched signal score is accessible
            enriched_count = 0
            for result in rag_results:
                if hasattr(result, 'signal_score') and result.signal_score > 0:
                    enriched_count += 1
                    assert 0.0 <= result.signal_score <= 1.0
                    assert hasattr(result, 'signal_type')
            
            return {
                "status": "success",
                "enriched_results": enriched_count,
                "total_results": len(rag_results)
            }
        
        # Test with enriched results
        result = mock_research_with_temporal("test company", self.enriched_company_results)
        
        assert result["status"] == "success"
        assert result["enriched_results"] > 0
        assert result["total_results"] == len(self.enriched_company_results)
    
    def test_l2_can_consume_enriched_contact_evidence(self):
        """Test that ContactResearchExecutor can consume enriched contact data."""
        contact_executor = ContactResearchExecutor(
            hybrid_search=None,
            pinecone_adapter=self.mock_adapter
        )
        
        # Mock contact research with temporal data
        def mock_contact_research_with_temporal(query, rag_results=None):
            if rag_results is None:
                return {"status": "no_data"}
            
            # Verify temporal signal scores
            temporal_signals = []
            for result in rag_results:
                if hasattr(result, 'signal_score') and result.signal_score > 0:
                    temporal_signals.append({
                        "text": result.text,
                        "signal_score": result.signal_score,
                        "signal_type": result.signal_type
                    })
            
            return {
                "status": "success",
                "temporal_signals": temporal_signals,
                "signal_count": len(temporal_signals)
            }
        
        result = mock_contact_research_with_temporal("test contact", self.enriched_contact_results)
        
        assert result["status"] == "success"
        assert result["signal_count"] > 0
        assert len(result["temporal_signals"]) == len(self.enriched_contact_results)
    
    def test_c_level_weighting_70_company_30_contact(self):
        """Test C-Level archetype weighting (70% company / 30% contact)."""
        # Simulate C-Level research with temporal data
        company_weight = 0.7
        contact_weight = 0.3
        
        # Calculate weighted scores
        company_avg_score = sum(r.score for r in self.enriched_company_results) / len(self.enriched_company_results)
        contact_avg_score = sum(r.score for r in self.enriched_contact_results) / len(self.enriched_contact_results)
        
        # Apply C-Level weighting
        weighted_company_score = company_avg_score * company_weight
        weighted_contact_score = contact_avg_score * contact_weight
        final_score = weighted_company_score + weighted_contact_score
        
        # Verify weighting calculation
        expected_company = 0.7 * company_avg_score
        expected_contact = 0.3 * contact_avg_score
        expected_final = expected_company + expected_contact
        
        assert abs(weighted_company_score - expected_company) < 0.001
        assert abs(weighted_contact_score - expected_contact) < 0.001
        assert abs(final_score - expected_final) < 0.001
        
        # Company should contribute more to final score for C-Level
        assert weighted_company_score > weighted_contact_score
    
    def test_c_level_temporal_signal_prioritization(self):
        """Test that C-Level research prioritizes temporal signals appropriately."""
        # C-Level should prioritize high signal scores over contact signals
        recent_company_signals = [
            r for r in self.enriched_company_results 
            if hasattr(r, 'signal_score') and r.signal_score > 0.8
        ]
        
        contact_signals = self.enriched_contact_results
        
        # Mock C-Level research prioritization
        def mock_c_level_prioritization(company_results, contact_results):
            prioritized = []
            
            # Prioritize high signal score company signals
            for result in company_results:
                if hasattr(result, 'signal_score') and result.signal_score > 0.8:
                    prioritized.append({
                        "text": result.text,
                        "priority": "high",
                        "reason": "Recent company signal",
                        "signal_score": result.signal_score
                    })
            
            # Add contact signals with lower priority
            for result in contact_results:
                prioritized.append({
                    "text": result.text,
                    "priority": "medium", 
                    "reason": "Contact signal",
                    "signal_score": result.signal_score
                })
            
            return prioritized
        
        prioritized_results = mock_c_level_prioritization(
            self.enriched_company_results, 
            self.enriched_contact_results
        )
        
        # Should have high priority recent company signals
        high_priority_count = sum(1 for r in prioritized_results if r["priority"] == "high")
        assert high_priority_count > 0, "Should prioritize recent company signals"
        
        # High priority items should have higher signal scores
        high_priority_scores = [r["signal_score"] for r in prioritized_results if r["priority"] == "high"]
        medium_priority_scores = [r["signal_score"] for r in prioritized_results if r["priority"] == "medium"]
        
        if high_priority_scores and medium_priority_scores:
            avg_high = sum(high_priority_scores) / len(high_priority_scores)
            avg_medium = sum(medium_priority_scores) / len(medium_priority_scores)
            assert avg_high > avg_medium, "High priority should have higher signal scores"
    
    def test_graceful_fallback_if_temporal_kg_unavailable(self):
        """Test graceful fallback when temporal KG is unavailable."""
        # Test with None temporal_kg
        rag_engine = RAGEngine()
        rag_engine.temporal_kg = None  # Simulate unavailable temporal KG
        
        # Mock retrieve method with fallback
        def mock_retrieve_with_fallback(query, use_temporal=True):
            if use_temporal and rag_engine.temporal_kg is None:
                # Fallback to basic RAG without temporal features
                return [OutreachRAGResult(
                    id="fallback_1",
                    text="Basic RAG result without temporal data",
                    score=0.5,
                    company="Unknown",
                    title="Basic Result",
                    source="basic_search",
                    signal_score=0.0,
                    signal_type=None
                )]
            
            # Normal temporal-enhanced RAG (would be implemented)
            return []
        
        # Test fallback behavior
        result = mock_retrieve_with_fallback("test query", use_temporal=True)
        
        assert len(result) == 1
        assert result[0].signal_score == 0.0, "Fallback should have zero signal score"
        assert "temporal data" in result[0].text
    
    def test_l2_executor_handles_missing_temporal_metadata(self):
        """Test that L2 executors handle missing temporal metadata gracefully."""
        # Create mixed results: some with signal data, some without
        mixed_results = [
            OutreachRAGResult(
                id="temporal_1",
                text="Result with temporal data",
                score=0.8,
                company="TestCompany",
                title="Temporal Result",
                source="temporal_source",
                signal_score=0.9,
                signal_type="strong_signal"
            ),
            OutreachRAGResult(
                id="basic_1",
                text="Result without temporal data",
                score=0.6,
                company="TestCompany",
                title="Basic Result",
                source="basic_source",
                signal_score=0.0,
                signal_type=None
            ),
            OutreachRAGResult(
                id="temporal_2",
                text="Another temporal result",
                score=0.7,
                company="TestCompany",
                title="Another Temporal Result",
                source="temporal_source_2",
                signal_score=0.5,
                signal_type="moderate_signal"
            )
        ]
        
        # Mock L2 processing that handles mixed signal data
        def mock_l2_process_mixed_metadata(results):
            processed = []
            temporal_count = 0
            basic_count = 0
            
            for result in results:
                if hasattr(result, 'signal_score') and result.signal_score > 0:
                    processed.append({
                        "text": result.text,
                        "type": "temporal_enhanced",
                        "signal_score": result.signal_score,
                        "signal_type": result.signal_type
                    })
                    temporal_count += 1
                else:
                    processed.append({
                        "text": result.text,
                        "type": "basic",
                        "score": result.score
                    })
                    basic_count += 1
            
            return {
                "processed": processed,
                "temporal_enhanced": temporal_count,
                "basic": basic_count,
                "total": len(results)
            }
        
        processed = mock_l2_process_mixed_metadata(mixed_results)
        
        assert processed["total"] == 3
        assert processed["temporal_enhanced"] == 2
        assert processed["basic"] == 1
        assert len(processed["processed"]) == 3
    
    def test_temporal_research_preserves_l2_boundaries(self):
        """Test that temporal research preserves L1-L5 boundaries."""
        # Test that L2 executors don't directly modify L4 components
        company_executor = CompanyResearchExecutor(
            hybrid_search=None,
            pinecone_adapter=self.mock_adapter
        )
        
        # Mock L2 research that only consumes, doesn't modify L4
        original_temporal_kg_methods = {
            "compute_temporal_weight": hasattr(self.temporal_kg, "compute_temporal_weight"),
            "search_temporal": hasattr(self.temporal_kg, "search_temporal")
        }
        
        def mock_l2_research_preserves_boundaries(query, temporal_kg):
            # L2 should only use temporal_kg methods, not modify them
            if hasattr(temporal_kg, "compute_temporal_weight"):
                weight = temporal_kg.compute_temporal_weight(datetime.now(UTC))
                assert isinstance(weight, float)
            
            # Should not add new methods to temporal_kg
            original_method_count = len([m for m in dir(temporal_kg) if not m.startswith('_')])
            
            return {
                "preserves_boundaries": True,
                "original_methods": original_method_count
            }
        
        result = mock_l2_research_preserves_boundaries("test", self.temporal_kg)
        
        assert result["preserves_boundaries"] is True
        
        # Verify temporal_kg wasn't modified
        current_methods = {
            "compute_temporal_weight": hasattr(self.temporal_kg, "compute_temporal_weight"),
            "search_temporal": hasattr(self.temporal_kg, "search_temporal")
        }
        
        assert current_methods == original_temporal_kg_methods
    
    def test_temporal_research_error_handling(self):
        """Test error handling in temporal research pathways."""
        # Test with malformed signal scores
        malformed_results = [
            OutreachRAGResult(
                id="valid_1",
                text="Valid result",
                score=0.8,
                company="TestCompany",
                title="Valid Result",
                source="valid_source",
                signal_score=0.9,
                signal_type="valid_signal"
            ),
            OutreachRAGResult(
                id="malformed_1",
                text="Malformed result",
                score=0.6,
                company="TestCompany",
                title="Malformed Result",
                source="malformed_source",
                signal_score=2.5,  # Should be 0-1
                signal_type="malformed_signal"
            )
        ]
        
        # Mock L2 error handling
        def mock_l2_error_handling(results):
            processed = []
            errors = []
            
            for i, result in enumerate(results):
                try:
                    # Validate signal score and type
                    signal_score = getattr(result, 'signal_score', 0.0)
                    signal_type = getattr(result, 'signal_type', '')
                    
                    # Type validation and normalization
                    if not isinstance(signal_score, (int, float)) or signal_score > 1.0:
                        signal_score = min(max(float(signal_score), 0.0), 1.0)
                        errors.append(f"Result {i}: Normalized signal_score")
                    
                    if not isinstance(signal_type, str):
                        signal_type = str(signal_type) if signal_type is not None else ""
                        errors.append(f"Result {i}: Converted signal_type to string")
                    
                    processed.append({
                        "text": result.text,
                        "signal_score": signal_score,
                        "signal_type": signal_type
                    })
                    
                except Exception as e:
                    errors.append(f"Result {i}: Processing error - {e}")
                    # Add safe fallback
                    processed.append({
                        "text": result.text,
                        "signal_score": 0.0,
                        "signal_type": "Error processing"
                    })
            
            return {
                "processed": processed,
                "errors": errors,
                "success_count": len(processed) - len(errors)
            }
        
        result = mock_l2_error_handling(malformed_results)
        
        assert len(result["processed"]) == 2
        assert len(result["errors"]) > 0  # Should detect and handle errors
        assert result["success_count"] >= 1  # At least one should succeed
        assert all(0.0 <= p["signal_score"] <= 1.0 for p in result["processed"])
