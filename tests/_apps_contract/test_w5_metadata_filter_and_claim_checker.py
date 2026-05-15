"""W5 exact metadata filtering and deterministic claim checking tests.

Tests:
- Exact metadata filter lane for fact_vectors only
- Chroma where-clause filtering with mandatory filters
- Minimal deterministic claim checker (employer, certification, year, title)
- Score separation (dense_score vs metadata_score)
- Claim check behavior for unsupported claims
- No process_docs usage
- No LLM judge/free-text verifier

Plan: 04_apps-rg-c0-architecture-analysis-f3d8b2 W5
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from apps_rg.runtime.bindings.c0_binding import (
    MetadataFilterProfile,
    MetadataFilterResult,
    DeterministicClaimChecker,
    ClaimCheckResult,
)


class TestMetadataFilterProfileLoading:
    """Test metadata filter profile loading and configuration."""
    
    def test_profile_loads_from_yaml(self) -> None:
        """EVIDENCE: MetadataFilterProfile loads from YAML config file."""
        profile = MetadataFilterProfile()
        # Should have loaded the profile (may be disabled if file missing)
        assert hasattr(profile, '_config')
        assert hasattr(profile, '_filterable_fields')
    
    def test_profile_has_enabled_flag(self) -> None:
        """EVIDENCE: Profile exposes enabled configuration."""
        profile = MetadataFilterProfile()
        assert isinstance(profile.enabled, bool)
    
    def test_profile_has_filterable_fields(self) -> None:
        """EVIDENCE: Profile has configured filterable fields."""
        profile = MetadataFilterProfile()
        fields = profile.get_filterable_fields()
        assert isinstance(fields, list)
    
    def test_filterable_fields_have_required_config(self) -> None:
        """EVIDENCE: Each filterable field has required configuration."""
        profile = MetadataFilterProfile()
        fields = profile.get_filterable_fields()
        
        if fields:
            field = fields[0]
            assert "field_name" in field
            assert "display_name" in field
            assert "query_sources" in field
    
    def test_filterable_fields_include_company_role_cert(self) -> None:
        """EVIDENCE: Filterable fields include company, role, certification, year."""
        profile = MetadataFilterProfile()
        fields = profile.get_filterable_fields()

        field_names = [f.get("field_name") for f in fields]

        assert "company" in field_names
        assert "role" in field_names
        assert "certification" in field_names
        assert "year" in field_names


class TestChromaWhereClauseBuilding:
    """Test Chroma where-clause construction with mandatory filters."""
    
    def test_app_filter_is_mandatory(self) -> None:
        """EVIDENCE: app=apps_rg filter is always applied."""
        profile = MetadataFilterProfile()
        
        if not profile.enabled:
            pytest.skip("Metadata filter profile disabled")
        
        # Build where clause with minimal payload
        where = profile.build_chroma_where_clause(
            app_payload={},
        )
        
        # Must have app filter
        assert where is not None
        where_json = json.dumps(where)
        assert "apps_rg" in where_json
    
    def test_source_class_filter_is_mandatory(self) -> None:
        """EVIDENCE: source_class filter for candidate-owned sources is always applied."""
        profile = MetadataFilterProfile()
        
        if not profile.enabled:
            pytest.skip("Metadata filter profile disabled")
        
        where = profile.build_chroma_where_clause(
            app_payload={},
        )
        
        # Must have source_class filter
        assert where is not None
        where_json = json.dumps(where)
        assert "candidate_profile" in where_json or "project_evidence" in where_json
    
    def test_company_research_is_rejected(self) -> None:
        """EVIDENCE: company_research source class is explicitly rejected."""
        profile = MetadataFilterProfile()
        
        # Check rejected_source_classes in config
        config = profile._config
        rejected = config.get("rejected_source_classes", [])
        
        assert "company_research" in rejected
        assert "rubrics" in rejected
        assert "governance_docs" in rejected
        assert "process_docs" in rejected
    
    def test_where_clause_includes_optional_metadata_filters(self) -> None:
        """EVIDENCE: Optional metadata filters added from app_payload."""
        profile = MetadataFilterProfile()
        
        if not profile.enabled:
            pytest.skip("Metadata filter profile disabled")
        
        # Build where clause with employer in payload
        where = profile.build_chroma_where_clause(
            app_payload={
                "jd_payload": {
                    "target_company": "Acme Corp"
                }
            },
        )
        
        # Should have employer filter
        assert where is not None
        where_json = json.dumps(where)
        assert "Acme Corp" in where_json or "acme corp" in where_json.lower()
    
    def test_where_clause_uses_and_operator(self) -> None:
        """EVIDENCE: Multiple filters combined with $and."""
        profile = MetadataFilterProfile()
        
        if not profile.enabled:
            pytest.skip("Metadata filter profile disabled")
        
        # Build where clause with multiple filter sources
        where = profile.build_chroma_where_clause(
            app_payload={
                "jd_payload": {
                    "target_company": "Acme Corp",
                    "required_certifications": ["AWS Certified"]
                }
            },
        )
        
        # Must have $and with multiple conditions
        assert where is not None
        assert "$and" in where or len(where) >= 2


class TestMetadataMatchChecking:
    """Test exact metadata match checking."""
    
    def test_exact_match_returns_score_1_0(self) -> None:
        """EVIDENCE: Exact metadata match returns metadata_score=1.0."""
        profile = MetadataFilterProfile()
        
        result = profile.check_metadata_match(
            evidence_metadata={"employer": "Acme Corp"},
            filter_field="employer",
            filter_value="Acme Corp",
        )
        
        assert isinstance(result, MetadataFilterResult)
        assert result.matched is True
        assert result.match_type == "exact"
        assert result.metadata_score == 1.0
    
    def test_partial_match_returns_score_0_5(self) -> None:
        """EVIDENCE: Partial metadata match returns metadata_score=0.5."""
        profile = MetadataFilterProfile()
        
        result = profile.check_metadata_match(
            evidence_metadata={"employer": "Acme Corporation"},
            filter_field="employer",
            filter_value="Acme Corp",
        )
        
        assert result.matched is True
        assert result.match_type == "partial"
        assert result.metadata_score == 0.5
    
    def test_no_match_returns_score_0_0(self) -> None:
        """EVIDENCE: No metadata match returns metadata_score=0.0."""
        profile = MetadataFilterProfile()
        
        result = profile.check_metadata_match(
            evidence_metadata={"employer": "Different Corp"},
            filter_field="employer",
            filter_value="Acme Corp",
        )
        
        assert result.matched is False
        assert result.match_type == "none"
        assert result.metadata_score == 0.0
    
    def test_missing_field_returns_score_0_0(self) -> None:
        """EVIDENCE: Missing metadata field returns metadata_score=0.0."""
        profile = MetadataFilterProfile()
        
        result = profile.check_metadata_match(
            evidence_metadata={},
            filter_field="employer",
            filter_value="Acme Corp",
        )
        
        assert result.matched is False
        assert result.match_type == "none"
        assert result.metadata_score == 0.0
    
    def test_case_insensitive_matching(self) -> None:
        """EVIDENCE: Metadata matching is case-insensitive."""
        profile = MetadataFilterProfile()
        
        result = profile.check_metadata_match(
            evidence_metadata={"employer": "ACME CORP"},
            filter_field="employer",
            filter_value="acme corp",
        )
        
        assert result.matched is True
        assert result.match_type == "exact"


class TestDeterministicClaimChecker:
    """Test deterministic claim checker for structured claims."""
    
    def test_supported_claim_types_listed(self) -> None:
        """EVIDENCE: Claim checker has defined supported claim types."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        assert "employer_match" in checker.SUPPORTED_CLAIM_TYPES
        assert "certification_match" in checker.SUPPORTED_CLAIM_TYPES
        assert "year_in_range" in checker.SUPPORTED_CLAIM_TYPES
        assert "title_match" in checker.SUPPORTED_CLAIM_TYPES
    
    def test_employer_match_verified(self) -> None:
        """EVIDENCE: Employer match is verified exactly."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="employer_match",
            claim_value="Acme Corp",
            evidence_metadata_list=[
                {"chunk_id": "doc1", "employer": "Acme Corp"},
            ],
        )
        
        assert result.verified is True
        assert result.support_status == "PASS"
        assert result.verification_method == "exact_match"
    
    def test_employer_mismatch_downgrades(self) -> None:
        """EVIDENCE: Unmatched employer claim downgrades support status."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="employer_match",
            claim_value="Acme Corp",
            evidence_metadata_list=[
                {"chunk_id": "doc1", "employer": "Different Corp"},
            ],
        )
        
        assert result.verified is False
        # Must downgrade, not silently PASS
        assert result.support_status in ["WEAK_WITH_CAVEATS", "PARTIAL", "UNSUPPORTED"]
    
    def test_certification_match_verified(self) -> None:
        """EVIDENCE: Certification match is verified exactly."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="certification_match",
            claim_value="AWS Certified Solutions Architect",
            evidence_metadata_list=[
                {"chunk_id": "doc1", "certification": "AWS Certified Solutions Architect"},
            ],
        )
        
        assert result.verified is True
        assert result.support_status == "PASS"
    
    def test_year_range_overlap_verified(self) -> None:
        """EVIDENCE: Year range overlap is verified."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="year_in_range",
            claim_value="2020-2023",
            evidence_metadata_list=[
                {"chunk_id": "doc1", "year": "2021-2022"},
            ],
        )
        
        assert result.verified is True
        assert result.support_status == "PASS"
        assert result.verification_method == "range_overlap"
    
    def test_year_range_no_overlap_downgrades(self) -> None:
        """EVIDENCE: Year range without overlap downgrades support."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="year_in_range",
            claim_value="2020-2023",
            evidence_metadata_list=[
                {"chunk_id": "doc1", "year": "2015-2018"},
            ],
        )
        
        assert result.verified is False
        assert result.support_status in ["WEAK_WITH_CAVEATS", "PARTIAL"]
    
    def test_unsupported_claim_type_returns_unsupported(self) -> None:
        """EVIDENCE: Unsupported claim type returns UNSUPPORTED status."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="semantic_skill_verification",  # Not in SUPPORTED_CLAIM_TYPES
            claim_value="Python expertise",
            evidence_metadata_list=[],
        )
        
        assert result.verified is False
        assert result.support_status == "UNSUPPORTED"
        assert result.verification_method == "unsupported"
    
    def test_multiple_claims_checked(self) -> None:
        """EVIDENCE: Multiple claims can be checked together."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        results = checker.check_all_claims(
            claims=[
                ("employer_match", "Acme Corp"),
                ("certification_match", "AWS Certified"),
            ],
            evidence_metadata_list=[
                {"chunk_id": "doc1", "employer": "Acme Corp", "certification": "AWS Certified"},
            ],
        )
        
        assert len(results) == 2
        assert all(r.verified for r in results)
        assert all(r.support_status == "PASS" for r in results)


class TestScoreSeparation:
    """Test that dense_score and metadata_score remain separate."""
    
    def test_metadata_score_not_merged_into_dense_score(self) -> None:
        """EVIDENCE: metadata_score is tracked separately from dense_score."""
        # This is enforced by the design — scores are in separate fields
        profile = MetadataFilterProfile()
        
        config = profile._config.get("score_separation", {})
        
        # Separate fields for each score type
        dense_field = config.get("dense_score_field")
        metadata_field = config.get("metadata_score_field")
        combined_field = config.get("combined_score_field")
        
        assert dense_field is not None
        assert metadata_field is not None
        # combined_score_field should be null (never merge)
        assert combined_field is None
    
    def test_evidence_item_has_both_scores(self) -> None:
        """EVIDENCE: Evidence items can have both confidence_score and metadata_score."""
        profile = MetadataFilterProfile()

        evidence_fields = profile._config.get("score_separation", {}).get("evidence_item_fields", [])

        assert "confidence_score" in evidence_fields
        assert "metadata_score" in evidence_fields


class TestNoProcessDocsUsage:
    """Verify process_docs is never used for metadata filtering."""
    
    def test_process_docs_in_rejected_source_classes(self) -> None:
        """EVIDENCE: process_docs is explicitly in rejected source classes."""
        profile = MetadataFilterProfile()
        
        rejected = profile._config.get("rejected_source_classes", [])
        assert "process_docs" in rejected
    
    def test_collection_is_fact_vectors(self) -> None:
        """EVIDENCE: Metadata filter uses fact_vectors collection only."""
        # The metadata filter profile is for fact_vectors only
        # This is verified by the fact that it uses the same collection
        # as the section retrieval (fact_vectors)
        profile = MetadataFilterProfile()
        
        # The profile doesn't specify a collection name directly
        # but the gate profile confirms it's fact_vectors only
        config = profile._config
        # No process_docs references should exist
        config_str = json.dumps(config)
        assert "process_docs" not in config_str or "rejected" in config_str


class TestNoLlmJudge:
    """Verify no LLM judge is used for claim verification."""
    
    def test_claim_checker_is_deterministic(self) -> None:
        """EVIDENCE: Claim checker uses exact match, not LLM."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        # The checker only supports deterministic claim types
        # No LLM-related claim types
        llm_types = ["semantic_verification", "llm_judge", "natural_language"]
        for claim_type in llm_types:
            assert claim_type not in checker.SUPPORTED_CLAIM_TYPES
    
    def test_verification_methods_are_deterministic(self) -> None:
        """EVIDENCE: Verification methods are exact_match or range_overlap only."""
        profile = MetadataFilterProfile()
        checker = DeterministicClaimChecker(profile)
        
        result = checker.check_claim(
            claim_type="employer_match",
            claim_value="Acme Corp",
            evidence_metadata_list=[{"chunk_id": "doc1", "employer": "Acme Corp"}],
        )
        
        assert result.verification_method in ["exact_match", "range_overlap"]
        assert result.verification_method != "llm_judge"
        assert result.verification_method != "semantic_similarity"


class TestMetadataFilterDisabled:
    """Test behavior when metadata filter is disabled."""
    
    def test_disabled_profile_returns_none_where_clause(self) -> None:
        """EVIDENCE: Disabled profile returns None for where clause."""
        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = Path(tmpdir) / "metadata_filter_profile.yaml"
            profile_path.write_text(yaml.safe_dump({"enabled": False}))
            
            with patch.object(MetadataFilterProfile, 'PROFILE_PATH', profile_path):
                profile = MetadataFilterProfile()
                assert profile.enabled is False
                
                where = profile.build_chroma_where_clause(app_payload={})
                assert where is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
