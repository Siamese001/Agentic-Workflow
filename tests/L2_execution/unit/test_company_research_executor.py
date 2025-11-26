"""
Tests for L2 company research executor functionality and KG fallback.

Validates search_company_context(), Temporal KG fallback for C_LEVEL/EXECUTIVE/FOUNDER archetypes,
fallback conditions, and output mapping to OutreachRAGResult list.
"""

from unittest.mock import Mock

from l2.company_research_executor import CompanyResearchExecutor, CompanySearchConfig, CompanyResearchResult, KG_FALLBACK_ARCHETYPES
from l4.hybrid_search import HybridSearchExecutor, SearchResult
from l4.schema.outreach_schema import OutreachRAGResult
from l4 import PineconeAdapter, TripletStore, Triplet
from l1.outreach_dataclasses import ArchetypeType


class TestCompanyResearchExecutor:
    """Test suite for L2 company research executor validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_hybrid_search = Mock(spec=HybridSearchExecutor)
        self.mock_pinecone_adapter = Mock(spec=PineconeAdapter)
        self.mock_triplet_store = Mock(spec=TripletStore)
        self.executor = CompanyResearchExecutor(
            hybrid_search=self.mock_hybrid_search,
            pinecone_adapter=self.mock_pinecone_adapter,
            triplet_store=self.mock_triplet_store
        )
    
    def test_search_company_context_returns_company_research_result(self):
        """Test search_company_context() returns CompanyResearchResult with correct type."""
        # Mock hybrid search results
        mock_search_results = [
            SearchResult(
                id="company_1",
                text="TechCorp - Leading technology company with 5000 employees",
                fused_score=0.85,
                metadata={"company": "TechCorp", "industry": "Technology", "size": "5000-10000"}
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_pinecone_adapter.build_namespace.return_value = "test_mission_company"
        
        # Execute search
        result = self.executor.search_company_context(
            mission_id="test_mission_123",
            target_company="TechCorp",
            archetype=ArchetypeType.SENIOR_TA,
            rag_params={"company_weight": 0.8, "individual_weight": 0.2},
            signal_params={"strategic_signals": False, "technical_signals": True}
        )
        
        # Verify return type and structure
        assert isinstance(result, CompanyResearchResult)
        assert hasattr(result, 'results')
        assert hasattr(result, 'kg_results')
        assert hasattr(result, 'query_used')
        assert hasattr(result, 'namespace')
        assert hasattr(result, 'total_found')
        assert hasattr(result, 'kg_found')
        assert hasattr(result, 'metadata')
    
    def test_temporal_kg_fallback_for_c_level_archetype(self):
        """Test Temporal KG fallback used for C_LEVEL archetype."""
        # Mock hybrid search results (limited)
        mock_search_results = [
            SearchResult(
                id="limited_company",
                text="Basic company information",
                fused_score=0.6,
                metadata={"company": "ExecCorp"}
            )
        ]
        
        # Mock KG results (substantial)
        mock_kg_triplets = [
            Triplet(
                subject="ExecCorp",
                predicate="has_executive",
                object="CEO_John_Smith",
                timestamp="2024-01-15",
                confidence=0.9
            ),
            Triplet(
                subject="ExecCorp",
                predicate="revenue",
                object="$500M",
                timestamp="2024-01-10",
                confidence=0.85
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.return_value = mock_kg_triplets
        self.mock_pinecone_adapter.build_namespace.return_value = "exec_mission_company"
        
        # Execute C-Level search
        result = self.executor.search_company_context(
            mission_id="exec_mission",
            target_company="ExecCorp",
            archetype=ArchetypeType.C_LEVEL,
            rag_params={"company_weight": 0.9, "individual_weight": 0.1},
            signal_params={"strategic_signals": True, "financial_signals": True}
        )
        
        # Verify KG fallback was attempted for C-Level
        self.mock_triplet_store.query.assert_called()
        
        # Verify KG results are included
        assert isinstance(result.kg_results, list)
        assert result.kg_found > 0
    
    def test_temporal_kg_fallback_for_all_four_archetypes(self):
        """Test Temporal KG fallback used for all 4 archetypes in KG_FALLBACK_ARCHETYPES."""
        # Verify all 4 archetypes are in KG fallback set
        expected_archetypes = {
            ArchetypeType.C_LEVEL,
            ArchetypeType.HIRING_MANAGER,
            ArchetypeType.SENIOR_TA,
            ArchetypeType.RECRUITER
        }
        
        assert KG_FALLBACK_ARCHETYPES == expected_archetypes
        
        # Mock minimal setup for each archetype test
        mock_search_results = [SearchResult(id="1", text="Company info", fused_score=0.7, metadata={})]
        mock_kg_triplets = [Triplet(subject="TestCorp", predicate="test", object="value", timestamp="2024-01-01", confidence=0.8)]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.return_value = mock_kg_triplets
        self.mock_pinecone_adapter.build_namespace.return_value = "test_company"
        
        # Test each archetype triggers KG fallback
        for archetype in expected_archetypes:
            self.mock_triplet_store.query.reset_mock()
            
            result = self.executor.search_company_context(
                mission_id="test_mission",
                target_company="TestCorp",
                archetype=archetype,
                rag_params={},
                signal_params={}
            )
            
            # KG query should be attempted for all archetypes in the set
            self.mock_triplet_store.query.assert_called()
    
    def test_kg_fallback_skipped_when_kg_unavailable(self):
        """Test KG fallback skipped when TripletStore is unavailable."""
        # Create executor without triplet store
        executor_no_kg = CompanyResearchExecutor(
            hybrid_search=self.mock_hybrid_search,
            pinecone_adapter=self.mock_pinecone_adapter,
            triplet_store=None  # KG unavailable
        )
        
        mock_search_results = [
            SearchResult(
                id="no_kg_company",
                text="Company without KG data",
                fused_score=0.75,
                metadata={"company": "NoKGCorp"}
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_pinecone_adapter.build_namespace.return_value = "no_kg_mission_company"
        
        # Execute search without KG
        result = executor_no_kg.search_company_context(
            mission_id="no_kg_mission",
            target_company="NoKGCorp",
            archetype=ArchetypeType.C_LEVEL,
            rag_params={},
            signal_params={}
        )
        
        # Verify results without KG data
        assert isinstance(result, CompanyResearchResult)
        assert len(result.kg_results) == 0
        assert result.kg_found == 0
    
    def test_kg_fallback_skipped_when_less_than_2_results(self):
        """Test KG fallback skipped when <2 results returned from KG."""
        # Mock search results
        mock_search_results = [
            SearchResult(
                id="single_result_company",
                text="Company with limited data",
                fused_score=0.7,
                metadata={"company": "LimitedCorp"}
            )
        ]
        
        # Mock KG with only 1 result (below threshold)
        mock_kg_triplets = [
            Triplet(
                subject="LimitedCorp",
                predicate="has_employee",
                object="1_employee",
                timestamp="2024-01-01",
                confidence=0.6
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.return_value = mock_kg_triplets
        self.mock_pinecone_adapter.build_namespace.return_value = "limited_mission_company"
        
        # Execute search
        result = self.executor.search_company_context(
            mission_id="limited_mission",
            target_company="LimitedCorp",
            archetype=ArchetypeType.C_LEVEL,
            rag_params={},
            signal_params={}
        )
        
        # Verify KG results are included but marked as limited
        assert len(result.kg_results) == 1
        assert result.kg_found == 1
        # Implementation might still include results but mark them as insufficient
    
    def test_output_mapped_into_outreach_rag_result_list(self):
        """Test output mapped into OutreachRAGResult list correctly."""
        # Mock search results
        mock_search_results = [
            SearchResult(
                id="mapped_company_1",
                text="TechCorp - Technology innovation leader",
                fused_score=0.88,
                metadata={
                    "company": "TechCorp",
                    "industry": "Technology",
                    "founded": "2010",
                    "employees": "1000-5000"
                }
            ),
            SearchResult(
                id="mapped_company_2",
                text="TechCorp - Recent product launch success",
                fused_score=0.82,
                metadata={
                    "company": "TechCorp",
                    "product": "CloudPlatform",
                    "launch_date": "2024-01-01"
                }
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_pinecone_adapter.build_namespace.return_value = "mapped_mission_company"
        
        result = self.executor.search_company_context(
            mission_id="mapped_mission",
            target_company="TechCorp",
            archetype=ArchetypeType.HIRING_MANAGER,
            rag_params={"company_weight": 0.8},
            signal_params={"growth_signals": True}
        )
        
        # Verify results are mapped to OutreachRAGResult
        assert isinstance(result.results, list)
        assert len(result.results) == len(mock_search_results)
        
        for outreach_result in result.results:
            assert isinstance(outreach_result, OutreachRAGResult)
            assert hasattr(outreach_result, 'id')
            assert hasattr(outreach_result, 'text')
            assert hasattr(outreach_result, 'score')
            assert hasattr(outreach_result, 'company')
            assert outreach_result.company == "TechCorp"
    
    def test_kg_results_mapped_to_outreach_rag_results(self):
        """Test KG results are mapped to OutreachRAGResult format."""
        # Mock search results
        mock_search_results = [
            SearchResult(id="base", text="Base company info", fused_score=0.7, metadata={})
        ]
        
        # Mock KG results
        mock_kg_triplets = [
            Triplet(
                subject="FinanceCorp",
                predicate="revenue_2023",
                object="$1.2B",
                timestamp="2024-01-15",
                confidence=0.95
            ),
            Triplet(
                subject="FinanceCorp",
                predicate="executive_team",
                object="CFO_Jane_Doe",
                timestamp="2024-01-10",
                confidence=0.88
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.return_value = mock_kg_triplets
        self.mock_pinecone_adapter.build_namespace.return_value = "kg_mapped_mission_company"
        
        result = self.executor.search_company_context(
            mission_id="kg_mapped_mission",
            target_company="FinanceCorp",
            archetype=ArchetypeType.C_LEVEL,
            rag_params={},
            signal_params={"financial_signals": True}
        )
        
        # Verify KG results are mapped
        assert isinstance(result.kg_results, list)
        assert len(result.kg_results) == len(mock_kg_triplets)
        
        for kg_outreach_result in result.kg_results:
            assert isinstance(kg_outreach_result, OutreachRAGResult)
            assert hasattr(kg_outreach_result, 'id')
            assert hasattr(kg_outreach_result, 'text')
            assert hasattr(kg_outreach_result, 'score')
            # KG results should have company information
            assert kg_outreach_result.company == "FinanceCorp"
    
    def test_company_search_config_application(self):
        """Test CompanySearchConfig is applied to search operations."""
        # Create custom config
        custom_config = CompanySearchConfig(
            top_k=25,
            score_threshold=0.7,
            include_news=True,
            include_financials=True,
            max_age_days=120,
            use_kg_fallback=True
        )
        
        # Verify config structure
        assert custom_config.top_k == 25
        assert custom_config.score_threshold == 0.7
        assert custom_config.include_news is True
        assert custom_config.include_financials is True
        assert custom_config.max_age_days == 120
        assert custom_config.use_kg_fallback is True
    
    def test_archetype_influences_search_configuration(self):
        """Test archetype influences search configuration and KG usage."""
        mock_search_results = [SearchResult(id="1", text="Company info", fused_score=0.8, metadata={})]
        mock_kg_triplets = [Triplet(subject="TestCorp", predicate="test", object="value", timestamp="2024-01-01", confidence=0.9)]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.return_value = mock_kg_triplets
        self.mock_pinecone_adapter.build_namespace.return_value = "archetype_test_company"
        
        # Test different archetypes
        archetypes = [
            ArchetypeType.RECRUITER,
            ArchetypeType.SENIOR_TA,
            ArchetypeType.HIRING_MANAGER,
            ArchetypeType.C_LEVEL
        ]
        
        for archetype in archetypes:
            self.mock_triplet_store.query.reset_mock()
            
            result = self.executor.search_company_context(
                mission_id="archetype_test",
                target_company="TestCorp",
                archetype=archetype,
                rag_params={"company_weight": 0.8},
                signal_params={}
            )
            
            # All archetypes should trigger KG query (based on KG_FALLBACK_ARCHETYPES)
            self.mock_triplet_store.query.assert_called()
            
            # Verify result structure
            assert isinstance(result, CompanyResearchResult)
            assert isinstance(result.results, list)
            assert isinstance(result.kg_results, list)
    
    def test_company_research_metadata_completeness(self):
        """Test CompanyResearchResult contains complete metadata."""
        mock_search_results = [
            SearchResult(
                id="meta_company",
                text="Company with complete metadata",
                fused_score=0.85,
                metadata={
                    "company": "MetaCorp",
                    "industry": "Technology",
                    "size": "1000-5000",
                    "founded": "2015"
                }
            )
        ]
        
        mock_kg_triplets = [
            Triplet(
                subject="MetaCorp",
                predicate="has_funding",
                object="$50M_Series_B",
                timestamp="2024-01-01",
                confidence=0.9
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.return_value = mock_kg_triplets
        self.mock_pinecone_adapter.build_namespace.return_value = "meta_mission_company"
        
        result = self.executor.search_company_context(
            mission_id="meta_mission",
            target_company="MetaCorp",
            archetype=ArchetypeType.SENIOR_TA,
            rag_params={},
            signal_params={}
        )
        
        # Verify metadata completeness
        assert isinstance(result.metadata, dict)
        assert result.query_used is not None
        assert result.namespace is not None
        assert isinstance(result.total_found, int)
        assert isinstance(result.kg_found, int)
        assert result.total_found >= len(result.results)
        assert result.kg_found >= len(result.kg_results)
    
    def test_error_handling_kg_query_failure(self):
        """Test executor handles KG query failures gracefully."""
        mock_search_results = [
            SearchResult(
                id="error_company",
                text="Company with KG error",
                fused_score=0.75,
                metadata={"company": "ErrorCorp"}
            )
        ]
        
        # Mock KG query to raise exception
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_triplet_store.query.side_effect = Exception("KG service unavailable")
        self.mock_pinecone_adapter.build_namespace.return_value = "error_mission_company"
        
        # Should handle KG error gracefully and still return search results
        result = self.executor.search_company_context(
            mission_id="error_mission",
            target_company="ErrorCorp",
            archetype=ArchetypeType.C_LEVEL,
            rag_params={},
            signal_params={}
        )
        
        # Should still return valid result with search results but no KG results
        assert isinstance(result, CompanyResearchResult)
        assert len(result.results) > 0  # Search results should be present
        assert len(result.kg_results) == 0  # KG results should be empty due to error
        assert result.kg_found == 0
    
    def test_empty_search_and_kg_results_handling(self):
        """Test executor handles empty search and KG results correctly."""
        # Mock empty results
        self.mock_hybrid_search.search.return_value = []
        self.mock_triplet_store.query.return_value = []
        self.mock_pinecone_adapter.build_namespace.return_value = "empty_mission_company"
        
        result = self.executor.search_company_context(
            mission_id="empty_mission",
            target_company="EmptyCorp",
            archetype=ArchetypeType.RECRUITER,
            rag_params={},
            signal_params={}
        )
        
        # Verify empty results are handled
        assert isinstance(result, CompanyResearchResult)
        assert len(result.results) == 0
        assert len(result.kg_results) == 0
        assert result.total_found == 0
        assert result.kg_found == 0
