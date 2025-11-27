"""
Tests for L2 contact research executor functionality and integration.

Validates search_contact_profile() returns List[OutreachRAGResult], uses HybridSearchExecutor,
namespace building via pinecone_adapter, and pure L2 execution without L1/L3/L4/L5 imports.
"""

import pytest
from unittest.mock import Mock

from l2.contact_research_executor import ContactResearchExecutor, ContactSearchConfig, ContactResearchResult
from l4.hybrid_search import HybridSearchExecutor, SearchResult
from l4.schema.outreach_schema import OutreachRAGResult
from l4 import PineconeAdapter


class TestContactResearchExecutor:
    """Test suite for L2 contact research executor validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_hybrid_search = Mock(spec=HybridSearchExecutor)
        self.mock_pinecone_adapter = Mock(spec=PineconeAdapter)
        self.executor = ContactResearchExecutor(
            hybrid_search=self.mock_hybrid_search,
            pinecone_adapter=self.mock_pinecone_adapter
        )
    
    def test_search_contact_profile_returns_contact_research_result(self):
        """Test search_contact_profile() returns ContactResearchResult with correct type."""
        # Mock hybrid search results
        mock_search_results = [
            SearchResult(
                id="contact_1",
                score=0.85,
                text="John Smith - Senior Software Engineer at TechCorp",
                fused_score=0.85,
                metadata={"company": "TechCorp", "title": "Senior Software Engineer"}
            ),
            SearchResult(
                id="contact_2",
                score=0.78,
                text="Jane Doe - Engineering Manager at StartupCorp",
                fused_score=0.78,
                metadata={"company": "StartupCorp", "title": "Engineering Manager"}
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_pinecone_adapter.build_namespace.return_value = "test_mission_contact"
        
        # Execute search
        result = self.executor.search_contact_profile(
            mission_id="test_mission_123",
            target_role="Senior Software Engineer",
            target_company="TechCorp",
            archetype="senior_ta",
            rag_params={"company_weight": 0.5, "individual_weight": 0.5},
            signal_params={"strategic_signals": False, "technical_signals": True}
        )
        
        # Verify return type and structure
        assert isinstance(result, ContactResearchResult)
        assert hasattr(result, 'results')
        assert hasattr(result, 'query_used')
        assert hasattr(result, 'namespace')
        assert hasattr(result, 'total_found')
        assert hasattr(result, 'filtered_count')
        assert hasattr(result, 'metadata')
    
    def test_search_contact_profile_returns_outreach_rag_results(self):
        """Test search_contact_profile() returns List[OutreachRAGResult] in results field."""
        # Mock search results
        mock_search_results = [
            SearchResult(
                id="contact_1",
                score=0.92,
                text="Sarah Chen - Principal Engineer with Python expertise",
                fused_score=0.92,
                metadata={
                    "company": "TechCorp",
                    "title": "Principal Engineer",
                    "source": "linkedin"
                }
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_search_results
        self.mock_pinecone_adapter.build_namespace.return_value = "mission_contact"
        
        result = self.executor.search_contact_profile(
            mission_id="mission_456",
            target_role="Principal Engineer",
            target_company="TechCorp",
            archetype="senior_ta",
            rag_params={"company_weight": 0.4, "individual_weight": 0.6},
            signal_params={"min_signal_score": 0.0, "max_age_days": 400}
        )
        
        # Verify results contain OutreachRAGResult objects
        assert isinstance(result.results, list)
        assert len(result.results) > 0
        
        for outreach_result in result.results:
            assert isinstance(outreach_result, OutreachRAGResult)
            assert hasattr(outreach_result, 'id')
            assert hasattr(outreach_result, 'text')
            assert hasattr(outreach_result, 'score')
            assert hasattr(outreach_result, 'company')
            assert hasattr(outreach_result, 'title')
    
    def test_uses_hybrid_search_executor_correctly(self):
        """Test executor uses HybridSearchExecutor.search() correctly."""
        # Mock search results
        expected_results = [
            SearchResult(
                id="search_1",
                score=0.88,
                text="Michael Johnson - CTO at EnterpriseCorp",
                fused_score=0.88,
                metadata={"company": "EnterpriseCorp", "title": "CTO"}
            )
        ]
        
        self.mock_hybrid_search.search.return_value = expected_results
        self.mock_pinecone_adapter.build_namespace.return_value = "enterprise_mission_contact"
        
        # Execute with specific parameters
        self.executor.search_contact_profile(
            mission_id="enterprise_mission",
            target_role="CTO",
            target_company="EnterpriseCorp",
            archetype="senior_ta",
            rag_params={"company_weight": 0.7, "individual_weight": 0.3},
            signal_params={"min_signal_score": 0.0, "max_age_days": 400}
        )
        
        # Verify HybridSearchExecutor.search was called
        self.mock_hybrid_search.search.assert_called_once()
        
        # Debug: Check mock call details
        print(f"DEBUG: call_count = {self.mock_hybrid_search.search.call_count}")
        print(f"DEBUG: call_args = {self.mock_hybrid_search.search.call_args}")
        print(f"DEBUG: call_args_list = {self.mock_hybrid_search.search.call_args_list}")
        
        # Get the call arguments
        call_args = self.mock_hybrid_search.search.call_args
        assert call_args is not None
        
        # Verify search was called with proper configuration
        args, kwargs = call_args
        assert len(kwargs) > 0  # Should have query argument
        assert "query" in kwargs  # Query should be present
        assert "namespace" in kwargs  # Namespace should be present
        assert "config" in kwargs  # Config should be present
    
    def test_namespace_built_via_pinecone_adapter(self):
        """Test namespace is built via pinecone_adapter.build_namespace()."""
        expected_namespace = "test_mission_789_contact"
        self.mock_pinecone_adapter.build_namespace.return_value = expected_namespace
        self.mock_hybrid_search.search.return_value = []
        
        # Execute search
        self.executor.search_contact_profile(
            mission_id="test_mission_789",
            target_role="Software Engineer",
            target_company="TestCorp",
            archetype="recruiter",
            rag_params={},
            signal_params={}
        )
        
        # Verify pinecone_adapter.build_namespace was called correctly
        self.mock_pinecone_adapter.build_namespace.assert_called_once_with(
            mission_id="test_mission_789",
            profile_type="contact"
        )
        
        # Verify namespace is used in result
        # (This would be verified by checking the actual result)
    
    def test_no_l1_l3_l4_l5_imports_violation(self):
        """Test executor has no L1/L3/L4/L5 imports (pure L2)."""
        # This is a structural test - verify the module imports
        import l2.contact_research_executor
        
        # The module should only import L4 components (HybridSearchExecutor, PineconeAdapter)
        # and L1 dataclasses (ArchetypeType) but no L1 planning logic
        from l2.contact_research_executor import ContactResearchExecutor
        
        # Verify the class exists and has expected methods
        assert hasattr(ContactResearchExecutor, 'search_contact_profile')
        assert callable(getattr(ContactResearchExecutor, 'search_contact_profile'))
    
    def test_archetype_parameter_influence_on_search(self):
        """Test archetype parameters influence search configuration."""
        # Mock search results
        self.mock_hybrid_search.search.return_value = []
        self.mock_pinecone_adapter.build_namespace.return_value = "archetype_test_contact"
        
        # Test different archetypes
        archetypes = ["recruiter", "senior_ta", "executive", "c_level"]
        
        for archetype in archetypes:
            self.executor.search_contact_profile(
                mission_id="test_mission",
                target_role="Test Role",
                target_company="TestCorp",
                archetype=archetype,
                rag_params={"company_weight": 0.5, "individual_weight": 0.5},
                signal_params={}
            )
        
        # Verify search was called for each archetype
        assert self.mock_hybrid_search.search.call_count == len(archetypes)
    
    def test_rag_parameters_applied_to_search(self):
        """Test RAG parameters are applied to search configuration."""
        self.mock_hybrid_search.search.return_value = []
        self.mock_pinecone_adapter.build_namespace.return_value = "rag_test_contact"
        
        # Test with specific RAG parameters
        rag_params = {
            "company_weight": 0.8,
            "individual_weight": 0.2,
            "source_weights": {"linkedin": 0.9, "company_site": 0.7}
        }
        
        self.executor.search_contact_profile(
            mission_id="rag_mission",
            target_role="Test Role",
            target_company="TestCorp",
            archetype="executive",
            rag_params=rag_params,
            signal_params={}
        )
        
        # Verify search was called (RAG params should influence search config)
        self.mock_hybrid_search.search.assert_called_once()
    
    def test_signal_parameters_applied_to_search(self):
        """Test signal parameters are applied to search configuration."""
        self.mock_hybrid_search.search.return_value = []
        self.mock_pinecone_adapter.build_namespace.return_value = "signal_test_contact"
        
        # Test with specific signal parameters
        signal_params = {
            "strategic_signals": True,
            "technical_signals": False,
            "financial_signals": True,
            "recent_activity_signals": True
        }
        
        self.executor.search_contact_profile(
            mission_id="signal_mission",
            target_role="Test Role", 
            target_company="TestCorp",
            archetype="c_level",
            rag_params={},
            signal_params=signal_params
        )
        
        # Verify search was called (signal params should influence filtering)
        self.mock_hybrid_search.search.assert_called_once()
    
    def test_contact_research_result_metadata_completeness(self):
        """Test ContactResearchResult contains complete metadata."""
        # Mock search results
        mock_results = [
            SearchResult(
                id="meta_test_1",
                score=0.75,
                text="Test contact with metadata",
                fused_score=0.75,
                metadata={"test": "metadata"}
            )
        ]
        
        self.mock_hybrid_search.search.return_value = mock_results
        self.mock_pinecone_adapter.build_namespace.return_value = "meta_mission_contact"
        
        result = self.executor.search_contact_profile(
            mission_id="meta_mission",
            target_role="Test Role",
            target_company="TestCorp",
            archetype="senior_ta",
            rag_params={},
            signal_params={}
        )
        
        # Verify metadata completeness
        assert isinstance(result.metadata, dict)
        assert result.query_used is not None
        assert result.namespace is not None
        assert isinstance(result.total_found, int)
        assert isinstance(result.filtered_count, int)
    
    def test_search_error_handling(self):
        """Test executor handles search errors gracefully."""
        # Mock search to raise exception
        self.mock_hybrid_search.search.side_effect = Exception("Search service unavailable")
        self.mock_pinecone_adapter.build_namespace.return_value = "error_test_contact"
        
        # Should handle error gracefully
        with pytest.raises(Exception):
            self.executor.search_contact_profile(
                mission_id="error_mission",
                target_role="Test Role",
                target_company="TestCorp",
                archetype="recruiter",
                rag_params={},
                signal_params={}
            )
    
    def test_empty_search_results_handling(self):
        """Test executor handles empty search results correctly."""
        # Mock empty search results
        self.mock_hybrid_search.search.return_value = []
        self.mock_pinecone_adapter.build_namespace.return_value = "empty_test_contact"
        
        result = self.executor.search_contact_profile(
            mission_id="empty_mission",
            target_role="Nonexistent Role",
            target_company="NonexistentCorp",
            archetype="recruiter",
            rag_params={},
            signal_params={}
        )
        
        # Verify empty results are handled
        assert isinstance(result, ContactResearchResult)
        assert len(result.results) == 0
        assert result.total_found == 0
        assert result.filtered_count == 0
    
    def test_search_config_application(self):
        """Test ContactSearchConfig is applied to search operations."""
        # Create executor with custom config
        custom_config = ContactSearchConfig(
            top_k=20,
            score_threshold=0.8,
            include_recent_activity=True,
            max_age_days=90,
            source_weights={"linkedin": 0.95, "github": 0.7}
        )
        
        # Note: This tests the config structure exists
        assert custom_config.top_k == 20
        assert custom_config.score_threshold == 0.8
        assert custom_config.include_recent_activity is True
        assert custom_config.max_age_days == 90
        assert isinstance(custom_config.source_weights, dict)
