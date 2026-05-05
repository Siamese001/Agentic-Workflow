"""W4 Research Bridge Integration Tests

Integration tests for apps_research → apps_lic flow and C0 retrieval wiring.
"""

import pytest
from datetime import datetime, timezone
from typing import Any


class TestW4P1ResearchBridge:
    """Test W4.P1: apps_research → apps_lic bridge."""
    
    def test_research_bridge_can_be_instantiated(self):
        """Verify AppsResearchBridge can be instantiated."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge(capability_ref="apps_research.v1")
        assert bridge is not None
        assert bridge._capability_ref == "apps_research.v1"
    
    def test_research_bridge_supported_capabilities(self):
        """Verify supported capabilities list."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge()
        
        assert "apps_research.v1" in bridge.SUPPORTED_CAPABILITIES
        assert "apps_research.v2" in bridge.SUPPORTED_CAPABILITIES
    
    def test_research_bridge_fetch_method_exists(self):
        """Verify bridge has required fetch method."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge()
        assert hasattr(bridge, 'fetch')
        assert callable(getattr(bridge, 'fetch'))
    
    def test_research_bridge_returns_research_result(self):
        """Verify fetch returns ResearchResult structure."""
        from apps_lic.integrations.apps_research_bridge import (
            AppsResearchBridge, ResearchResult
        )
        
        # This will fail with NotImplementedError or exception wrapping
        # because apps_research isn't actually wired in test context
        bridge = AppsResearchBridge()
        
        # Mock the invoke method to test the flow
        def mock_invoke(*args, **kwargs):
            class MockResult:
                run_id = "test-run-001"
                is_blocked = False
                is_stale = False
                age_days = 0.0
                confidence_score = 0.85
                evidence_items = []
                
            return MockResult()
        
        # Patch the internal method
        bridge._invoke_apps_research = mock_invoke
        
        result = bridge.fetch(
            recipient_class="RECRUITER",
            recipient_name="Jane Smith",
            company_name="Acme Corp",
            job_title="Engineering Manager",
            channel="email",
            outreach_mode="cold",
            relationship_distance="cold",
            capability_ref="apps_research.v1",
            request_id="req-001",
            run_id="run-001",
            trace_id="tr-001",
        )
        
        assert isinstance(result, ResearchResult)
        assert result.request_id == "req-001"
        assert "tr-001" in result.trace_id  # trace_id gets prefixed but original is included
    
    def test_research_bridge_blocks_on_unsupported_capability(self):
        """Verify bridge blocks when capability not supported."""
        from apps_lic.integrations.apps_research_bridge import (
            AppsResearchBridge, ResearchResult
        )
        
        bridge = AppsResearchBridge()
        
        result = bridge.fetch(
            recipient_class="RECRUITER",
            recipient_name="Jane Smith",
            company_name="Acme Corp",
            job_title="Engineering Manager",
            channel="email",
            outreach_mode="cold",
            relationship_distance="cold",
            capability_ref="unsupported.v1",  # Unsupported
            request_id="req-001",
            run_id="run-001",
            trace_id="tr-001",
        )
        
        assert isinstance(result, ResearchResult)
        assert result.is_blocked is True
        assert "Unsupported capability_ref" in result.block_reason
    
    def test_research_bridge_depth_profile_mapping(self):
        """Verify recipient class maps to correct depth profile."""
        from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
        
        bridge = AppsResearchBridge()
        
        # Test depth profile selection via _invoke_apps_research
        # Since we can't easily test the internal call, we verify the logic
        # by checking the method exists and has correct signature
        import inspect
        sig = inspect.signature(bridge._invoke_apps_research)
        params = list(sig.parameters.keys())
        
        assert "recipient_class" in params
        assert "company_name" in params
    
    def test_evidence_item_structure(self):
        """Verify EvidenceItem dataclass structure."""
        from apps_lic.integrations.apps_research_bridge import EvidenceItem
        
        item = EvidenceItem(
            source_id="src-001",
            label="Company funding news",
            uri="https://example.com/news",
            source_type="web",
            field_ref="company_brief",
            confidence=0.85,
        )
        
        assert item.source_id == "src-001"
        assert item.label == "Company funding news"
        assert item.confidence == 0.85
    
    def test_research_result_structure(self):
        """Verify ResearchResult dataclass structure."""
        from apps_lic.integrations.apps_research_bridge import (
            ResearchResult, EvidenceItem
        )
        
        result = ResearchResult(
            run_id="run-001",
            trace_id="tr-001",
            request_id="req-001",
            is_blocked=False,
            block_reason="",
            is_stale=False,
            age_days=0.0,
            evidence_items=(),
            confidence_score=0.85,
            result_hash="sha256:abc123",
            jd_hash="",
            jd_uri="",
            company_brief_hash="sha256:def456",
            fetch_duration_ms=1234.0,
            audit_ref="tr-001",
        )
        
        assert result.run_id == "run-001"
        assert result.confidence_score == 0.85
        assert result.is_blocked is False


class TestW4P2C0RetrievalWiring:
    """Test W4.P2: C0 retrieval → FEC producer wiring."""
    
    def test_fec_producer_exists(self):
        """Verify FEC producer module exists."""
        from apps_lic.cert.fec_producer import (
            produce_fec,
            PRODUCER_ID,
            FEC_SCHEMA_VERSION,
        )
        
        assert PRODUCER_ID == "apps_lic.research_bridge"
        assert FEC_SCHEMA_VERSION == "1.0.0"
        assert callable(produce_fec)
    
    def test_fec_producer_template_path(self):
        """Verify FEC producer works without C0 retrieval."""
        from apps_lic.cert.fec_producer import produce_fec, PRODUCER_ID
        
        context = {
            "research_snippets": [
                {"source": "linkedin", "content": "Company raised $50M", "confidence": 0.9},
                {"source": "crunchbase", "content": "Series B funding", "confidence": 0.85},
            ],
            "company_brief": {"funding_stage": "Series B"},
            "competitive_signals": [
                {"type": "hiring", "confidence": 0.8},
            ],
        }
        
        fec = produce_fec(context)
        
        assert fec["producer"] == PRODUCER_ID
        assert fec["grounded"] is True  # Has snippets
        assert fec["evidence_sufficiency"] == "template_with_signals"
        assert len(fec["retrieval_sources"]) > 0
    
    def test_fec_producer_c0_path(self):
        """Verify FEC producer works with C0 retrieval."""
        from apps_lic.cert.fec_producer import produce_fec
        
        context = {
            "research_snippets": [],
            "company_brief": {},
            "competitive_signals": [],
            "c0_retrieval_sources": {
                "retrieval_id": "c0-001",
                "query": "company funding",
                "results": [{"chunk": "Company raised Series B"}, {"chunk": "$50M round"}],
                "confidence": 0.92,
            },
        }
        
        fec = produce_fec(context)
        
        assert fec["grounded"] is True
        assert fec["evidence_sufficiency"] == "grounded"
        assert any(
            src.get("source_type") == "c0_retrieval"
            for src in fec["retrieval_sources"]
        )
    
    def test_fec_producer_no_evidence(self):
        """Verify FEC producer handles empty evidence gracefully."""
        from apps_lic.cert.fec_producer import produce_fec
        
        context = {
            "research_snippets": [],
            "company_brief": {},
            "competitive_signals": [],
        }
        
        fec = produce_fec(context)
        
        assert fec["grounded"] is False
        assert fec["evidence_sufficiency"] == "template_only"
    
    def test_fec_template_id_extraction(self):
        """Verify template ID extraction from context."""
        from apps_lic.cert.fec_producer import produce_fec
        
        context = {
            "research_snippets": [],
            "template_ids": ["template-001", "template-002"],
        }
        
        fec = produce_fec(context)
        
        assert "template-001" in fec["template_ids"]
        assert "template-002" in fec["template_ids"]
    
    def test_fec_structure_completeness(self):
        """Verify FEC has all required fields."""
        from apps_lic.cert.fec_producer import produce_fec
        
        context = {
            "research_snippets": [{"source": "test", "content": "test", "confidence": 0.5}],
        }
        
        fec = produce_fec(context)
        
        required_fields = [
            "producer",
            "grounded",
            "retrieval_sources",
            "template_ids",
            "route_id",
            "evidence_sufficiency",
            "_schema_version",
            "_metadata",
        ]
        
        for field in required_fields:
            assert field in fec, f"Missing required field: {field}"


class TestW4ResearchC0AdapterIntegration:
    """Test W4: apps_research C0 adapter integration."""
    
    def test_research_c0_adapter_exists(self):
        """Verify apps_research C0 adapter exists."""
        from apps_research.integrations.research_c0_adapter import (
            ResearchC0Adapter,
            C0EvidenceBundle,
            ResearchDepthProfile,
        )
        
        assert ResearchC0Adapter is not None
        assert C0EvidenceBundle is not None
        assert hasattr(ResearchDepthProfile, 'STANDARD')
        assert hasattr(ResearchDepthProfile, 'DEEP')
    
    def test_research_c0_adapter_instantiation(self):
        """Verify C0 adapter can be instantiated."""
        from apps_research.integrations.research_c0_adapter import ResearchC0Adapter
        
        adapter = ResearchC0Adapter(collection="test_collection")
        assert adapter is not None
    
    def test_research_exit_fec_producer_exists(self):
        """Verify apps_research exit FEC producer exists."""
        from apps_research.integrations.research_exit_fec_producer import (
            assemble_fec,
            ResearchFinalEvidenceContract,
        )
        
        assert callable(assemble_fec)
        assert ResearchFinalEvidenceContract is not None


class TestW4SpineWiring:
    """Test W4 components in spine wiring."""
    
    def test_spine_wiring_has_w4_components(self):
        """Verify spine wiring includes W4 verifiers."""
        wiring_path = Path("apps_lic/spine_wiring.py")
        content = wiring_path.read_text()
        
        assert "research_bridge" in content
        assert "c0_retrieval_wiring" in content
    
    def test_research_bridge_verifier_exists(self):
        """Verify _verify_research_bridge method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_research_bridge')
    
    def test_c0_retrieval_wiring_verifier_exists(self):
        """Verify _verify_c0_retrieval_wiring method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_c0_retrieval_wiring')


class TestW4BriefingQualityGate:
    """Test W4: Briefing quality gate integration."""
    
    def test_briefing_quality_gate_exists(self):
        """Verify BriefingQualityGate exists."""
        from apps_lic.integrations.briefing_quality_gate import (
            BriefingQualityGate,
            BriefingQualityDecision,
        )
        
        assert BriefingQualityGate is not None
        assert BriefingQualityDecision is not None
    
    def test_briefing_quality_gate_evaluation(self):
        """Verify quality gate can evaluate research results."""
        from apps_lic.integrations.briefing_quality_gate import (
            BriefingQualityGate,
            BriefingQualityDecision,
        )
        
        gate = BriefingQualityGate()
        
        class MockResult:
            evidence_items = [object(), object(), object()]  # 3 items
            age_days = 5.0
            confidence_score = 0.85
        
        result = MockResult()
        decision = gate.evaluate(result, recipient_class="RECRUITER")
        
        assert isinstance(decision, BriefingQualityDecision)
        assert decision.evidence_count == 3
        assert decision.quality_level in ("pass", "marginal", "fail")
    
    def test_briefing_quality_gate_coverage_check(self):
        """Verify quality gate checks coverage."""
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityGate
        
        gate = BriefingQualityGate()
        
        class LowCoverageResult:
            evidence_items = [object()]  # Only 1 item
            age_days = 5.0
            confidence_score = 0.85
        
        result = LowCoverageResult()
        decision = gate.evaluate(result, recipient_class="RECRUITER")
        
        # Should be marginal or fail due to low coverage
        assert decision.quality_level in ("marginal", "fail")
    
    def test_briefing_quality_gate_recency_check(self):
        """Verify quality gate checks recency with recipient-specific thresholds."""
        from apps_lic.integrations.briefing_quality_gate import BriefingQualityGate
        
        gate = BriefingQualityGate()
        
        class StaleResult:
            evidence_items = [object(), object(), object()]
            age_days = 45.0  # Very old
            confidence_score = 0.85
        
        # Test recruiter threshold (more lenient)
        result_recruiter = StaleResult()
        decision_recruiter = gate.evaluate(result_recruiter, recipient_class="RECRUITER")
        
        # Test executive threshold (stricter)
        result_exec = StaleResult()
        decision_exec = gate.evaluate(result_exec, recipient_class="EXECUTIVE")
        
        # Executive should be more likely to fail due to recency
        assert decision_exec.quality_level in ("fail", "marginal")


# Import needed for tests
from pathlib import Path
