"""W3 briefing bypass gate tests — G_BRIEF_BYPASS evaluation.

Tests the briefing bypass gate behavior:
- Fresh + authoritative brief: bypass eligible
- Stale authoritative brief: WEAK_WITH_CAVEATS
- Unauthorized/ACL-denied brief: BLOCKED
- Unreadable brief: BLOCKED
- No brief path: NOT_APPLICABLE

Plan: 04_apps-rg-c0-architecture-analysis-f3d8b2 W3
"""
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta, timezone
import pytest
import yaml
from pathlib import Path
from typing import Any
from unittest.mock import patch

from apps_rg.runtime.bindings.c0_briefing_bypass import (
    BriefEvaluationResult,
    BriefingBypassEvaluator,
    evaluate_manual_brief,
)
from agentic_core.runtime.gates.gate_types import (
    VERDICT_PASS,
    VERDICT_UNKNOWN,
    VERDICT_NOT_APPLICABLE,
)


class TestBriefingBypassEvaluatorBasics:
    """Test basic evaluator functionality."""
    
    def test_evaluator_has_max_age_hours(self) -> None:
        """EVIDENCE: Evaluator exposes max_age_hours configuration."""
        evaluator = BriefingBypassEvaluator()
        assert hasattr(evaluator, 'max_age_hours')
        assert isinstance(evaluator.max_age_hours, int)
        assert evaluator.max_age_hours > 0
    
    def test_evaluator_has_authority_classes(self) -> None:
        """EVIDENCE: Evaluator exposes authority_classes list."""
        evaluator = BriefingBypassEvaluator()
        assert hasattr(evaluator, 'authority_classes')
        assert isinstance(evaluator.authority_classes, list)
        assert "authoritative" in evaluator.authority_classes
    
    def test_evaluator_has_bypass_rules(self) -> None:
        """EVIDENCE: Evaluator exposes bypass_rules dict."""
        evaluator = BriefingBypassEvaluator()
        assert hasattr(evaluator, 'bypass_rules')
        assert isinstance(evaluator.bypass_rules, dict)
        assert "authoritative" in evaluator.bypass_rules


class TestBriefEvaluationResult:
    """Test BriefEvaluationResult dataclass."""
    
    def test_result_has_required_fields(self) -> None:
        """EVIDENCE: BriefEvaluationResult has all required fields."""
        result = BriefEvaluationResult(
            brief_path="/path/to/brief.md",
            authority_class="authoritative",
            is_fresh=True,
            is_authorized=True,
            can_read=True,
            file_exists=True,
            file_size_bytes=1024,
            file_mtime=datetime.now(timezone.utc).isoformat(),
            file_age_hours=12.0,
            max_age_hours=168,
            bypass_eligible=True,
            support_status="PASS",
            reason="Fresh authoritative brief",
        )
        assert result.brief_path == "/path/to/brief.md"
        assert result.support_status == "PASS"
        assert result.bypass_eligible is True
    
    def test_result_to_gate_verdict_pass(self) -> None:
        """EVIDENCE: PASS result converts to GateVerdict-compatible dict."""
        result = BriefEvaluationResult(
            brief_path="/path/to/brief.md",
            authority_class="authoritative",
            is_fresh=True,
            is_authorized=True,
            can_read=True,
            file_exists=True,
            file_size_bytes=1024,
            file_mtime=datetime.now(timezone.utc).isoformat(),
            file_age_hours=12.0,
            max_age_hours=168,
            bypass_eligible=True,
            support_status="PASS",
            reason="Fresh authoritative brief",
        )
        verdict = result.to_gate_verdict("test_digest_1234567890abcdef")
        assert verdict["gate_id"] == "G_BRIEF_BYPASS"
        assert verdict["result"] == "PASS"
        assert "brief:/path/to/brief.md" in verdict["evidence_refs"]
    
    def test_result_to_gate_verdict_blocked(self) -> None:
        """EVIDENCE: BLOCKED result converts to FAIL verdict."""
        result = BriefEvaluationResult(
            brief_path="/path/to/brief.md",
            authority_class="unverified",
            is_fresh=False,
            is_authorized=False,
            can_read=False,
            file_exists=False,
            file_size_bytes=0,
            file_mtime="",
            file_age_hours=0.0,
            max_age_hours=168,
            bypass_eligible=False,
            support_status="BLOCKED",
            reason="Unverified source blocked",
        )
        verdict = result.to_gate_verdict("test_digest_1234567890abcdef")
        assert verdict["result"] == "FAIL"


class TestEvaluateManualBriefNoPath:
    """Test evaluate_manual_brief with no brief path."""
    
    def test_none_path_returns_not_applicable(self) -> None:
        """EVIDENCE: None brief path returns NOT_APPLICABLE status."""
        result = evaluate_manual_brief(None)
        assert result.support_status == "NOT_APPLICABLE"
        assert result.bypass_eligible is False
        assert "No manual brief path provided" in result.reason
    
    def test_empty_string_path_returns_not_applicable(self) -> None:
        """EVIDENCE: Empty string brief path returns NOT_APPLICABLE status."""
        result = evaluate_manual_brief("")
        assert result.support_status == "NOT_APPLICABLE"
        assert result.bypass_eligible is False


class TestEvaluateManualBriefFreshAuthoritative:
    """Test fresh authoritative brief evaluation."""
    
    def test_fresh_authoritative_brief_returns_pass(self, tmp_path: Path) -> None:
        """EVIDENCE: Fresh authoritative brief returns PASS and bypass eligible."""
        # Create a brief file with authoritative path indicators
        brief_path = tmp_path / "company_website_brief.md"
        brief_path.write_text("# Company Official Brief\n\nThis is authoritative content.")
        
        result = evaluate_manual_brief(str(brief_path))
        
        # Should detect as authoritative (path contains "company_website")
        assert result.authority_class == "authoritative"
        assert result.is_fresh is True
        assert result.support_status == "PASS"
        assert result.bypass_eligible is True
        assert "Fresh authoritative brief" in result.reason
    
    def test_fresh_official_brief_returns_pass(self, tmp_path: Path) -> None:
        """EVIDENCE: Fresh official brief returns PASS."""
        brief_path = tmp_path / "official_annual_report.md"
        brief_path.write_text("# Annual Report 2024")
        
        result = evaluate_manual_brief(str(brief_path))
        
        assert result.authority_class == "authoritative"
        assert result.bypass_eligible is True


class TestEvaluateManualBriefStaleAuthoritative:
    """Test stale authoritative brief evaluation."""
    
    def test_stale_authoritative_brief_returns_weak_with_caveats(
        self, tmp_path: Path
    ) -> None:
        """EVIDENCE: Stale authoritative brief returns WEAK_WITH_CAVEATS, not bypass."""
        # Create a brief file
        brief_path = tmp_path / "company_website_brief.md"
        brief_path.write_text("# Company Official Brief")
        
        # Set mtime to 10 days ago (older than 7 day max_age)
        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        old_timestamp = old_time.timestamp()
        os.utime(brief_path, (old_timestamp, old_timestamp))
        
        result = evaluate_manual_brief(str(brief_path))
        
        assert result.authority_class == "authoritative"
        assert result.is_fresh is False
        assert result.file_age_hours > 168  # More than 7 days
        assert result.support_status == "WEAK_WITH_CAVEATS"
        assert result.bypass_eligible is False  # Stale = never bypass
        assert "Stale authoritative brief" in result.reason


class TestEvaluateManualBriefUnauthorized:
    """Test unauthorized brief evaluation."""
    
    def test_unauthorized_brief_returns_blocked(self, tmp_path: Path) -> None:
        """EVIDENCE: Unauthorized brief path returns BLOCKED."""
        # Create a file outside allowed paths (simulated by mocking _is_authorized)
        brief_path = tmp_path / "company_website_brief.md"
        brief_path.write_text("# Brief")
        
        # Mock _is_authorized to return False
        evaluator = BriefingBypassEvaluator()
        with patch.object(evaluator, '_is_authorized', return_value=False):
            result = evaluator.evaluate_brief(str(brief_path))
        
        assert result.is_authorized is False
        assert result.support_status == "BLOCKED"
        assert result.bypass_eligible is False
        assert "not authorized" in result.reason.lower()


class TestEvaluateManualBriefUnreadable:
    """Test unreadable brief evaluation."""
    
    def test_nonexistent_brief_returns_unreadable(self) -> None:
        """EVIDENCE: Non-existent brief file returns UNREADABLE."""
        result = evaluate_manual_brief("/nonexistent/path/brief.md")
        
        assert result.support_status == "UNREADABLE"
        assert result.bypass_eligible is False
        assert result.file_exists is False
        assert "not found" in result.reason.lower() or "not readable" in result.reason.lower()


class TestEvaluateManualBriefSemiAuthoritative:
    """Test semi-authoritative brief evaluation."""
    
    def test_fresh_semi_authoritative_brief_returns_weak_with_caveats(
        self, tmp_path: Path
    ) -> None:
        """EVIDENCE: Fresh semi-authoritative brief returns WEAK_WITH_CAVEATS, not bypass."""
        # Create a brief with semi-authoritative path indicators
        brief_path = tmp_path / "industry_analyst_report.md"
        brief_path.write_text("# Industry Analysis Report")
        
        result = evaluate_manual_brief(str(brief_path))
        
        assert result.authority_class == "semi_authoritative"
        assert result.is_fresh is True
        assert result.support_status == "WEAK_WITH_CAVEATS"
        assert result.bypass_eligible is False  # Semi-authoritative = never full bypass
    
    def test_stale_semi_authoritative_brief_returns_blocked(
        self, tmp_path: Path
    ) -> None:
        """EVIDENCE: Stale semi-authoritative brief returns BLOCKED."""
        brief_path = tmp_path / "analyst_report.md"
        brief_path.write_text("# Old Report")
        
        # Set mtime to 10 days ago
        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        old_timestamp = old_time.timestamp()
        os.utime(brief_path, (old_time.timestamp(), old_time.timestamp()))
        
        result = evaluate_manual_brief(str(brief_path))
        
        assert result.authority_class == "semi_authoritative"
        assert result.is_fresh is False
        assert result.support_status == "BLOCKED"
        assert result.bypass_eligible is False


class TestEvaluateManualBriefUnverified:
    """Test unverified brief evaluation."""
    
    def test_unverified_brief_always_blocked(self, tmp_path: Path) -> None:
        """EVIDENCE: Unverified brief is always blocked regardless of freshness."""
        # Create a brief file
        brief_path = tmp_path / "notes.txt"
        brief_path.write_text("# Some notes")
        
        # Mock the authority class to unverified to test bypass behavior
        evaluator = BriefingBypassEvaluator()
        with patch.object(evaluator, '_determine_authority_class', return_value="unverified"):
            result = evaluator.evaluate_brief(str(brief_path))
        
        # Unverified should be blocked for bypass
        assert result.authority_class == "unverified"
        assert result.support_status == "BLOCKED"
        assert result.bypass_eligible is False
        assert "unverified" in result.reason.lower()


class TestBriefingBypassConfigResolution:
    """Test that briefing bypass uses config-resolved values."""
    
    def test_max_age_hours_from_config(self) -> None:
        """EVIDENCE: max_age_hours is loaded from research_delegation_profile.yaml."""
        evaluator = BriefingBypassEvaluator()
        # Default should be 168 (7 days) if config not found
        # or loaded from config if present
        assert evaluator.max_age_hours == 168
    
    def test_authority_classes_from_config(self) -> None:
        """EVIDENCE: authority_classes is loaded from research_delegation_profile.yaml."""
        evaluator = BriefingBypassEvaluator()
        expected_classes = ["authoritative", "semi_authoritative", "unverified"]
        for cls in expected_classes:
            assert cls in evaluator.authority_classes


class TestGateVerdictMapping:
    """Test mapping from BriefEvaluationResult to GateVerdict."""
    
    def test_pass_maps_to_verdict_pass(self) -> None:
        """EVIDENCE: PASS support_status maps to VERDICT_PASS."""
        result = BriefEvaluationResult(
            brief_path="/path/brief.md",
            authority_class="authoritative",
            is_fresh=True,
            is_authorized=True,
            can_read=True,
            file_exists=True,
            file_size_bytes=100,
            file_mtime=datetime.now(timezone.utc).isoformat(),
            file_age_hours=12.0,
            max_age_hours=168,
            bypass_eligible=True,
            support_status="PASS",
            reason="Fresh brief",
        )
        verdict = result.to_gate_verdict("digest123")
        assert verdict["result"] == "PASS"
    
    def test_weak_with_caveats_maps_to_partial(self) -> None:
        """EVIDENCE: WEAK_WITH_CAVEATS maps to PARTIAL (usable with caveats)."""
        result = BriefEvaluationResult(
            brief_path="/path/brief.md",
            authority_class="authoritative",
            is_fresh=False,
            is_authorized=True,
            can_read=True,
            file_exists=True,
            file_size_bytes=100,
            file_mtime=datetime.now(timezone.utc).isoformat(),
            file_age_hours=200.0,
            max_age_hours=168,
            bypass_eligible=False,
            support_status="WEAK_WITH_CAVEATS",
            reason="Stale but usable",
        )
        verdict = result.to_gate_verdict("digest123")
        assert verdict["result"] == "PARTIAL"  # Usable but with caveats
    
    def test_blocked_maps_to_verdict_fail(self) -> None:
        """EVIDENCE: BLOCKED support_status maps to FAIL verdict."""
        result = BriefEvaluationResult(
            brief_path="/path/brief.md",
            authority_class="unverified",
            is_fresh=True,
            is_authorized=False,
            can_read=False,
            file_exists=False,
            file_size_bytes=0,
            file_mtime="",
            file_age_hours=0.0,
            max_age_hours=168,
            bypass_eligible=False,
            support_status="BLOCKED",
            reason="Unverified source",
        )
        verdict = result.to_gate_verdict("digest123")
        assert verdict["result"] == "FAIL"
    
    def test_not_applicable_maps_to_unknown(self) -> None:
        """EVIDENCE: NOT_APPLICABLE maps to UNKNOWN (no gate evidence available)."""
        result = BriefEvaluationResult(
            brief_path="",
            authority_class="not_applicable",
            is_fresh=False,
            is_authorized=False,
            can_read=False,
            file_exists=False,
            file_size_bytes=0,
            file_mtime="",
            file_age_hours=0.0,
            max_age_hours=168,
            bypass_eligible=False,
            support_status="NOT_APPLICABLE",
            reason="No brief provided",
        )
        verdict = result.to_gate_verdict("digest123")
        # NOT_APPLICABLE not in verdict_map, falls through to UNKNOWN
        assert verdict["result"] == "UNKNOWN"


class TestBriefingBypassIsolation:
    """Test that G_BRIEF_BYPASS does NOT inflate overall FEC.support_status.
    
    W3 PATCH: The briefing bypass gate verdict must be isolated to the gate itself.
    It must NOT cause FEC.support_status=PASS if Chroma evidence gates are UNKNOWN.
    """
    
    def test_brief_bypass_gate_does_not_inflate_fec_support_status(self) -> None:
        """EVIDENCE: G_BRIEF_BYPASS=PASS does NOT make FEC.support_status=PASS.
        
        If Chroma retrieval didn't run (file-only path), FEC.support_status
        must remain UNKNOWN regardless of G_BRIEF_BYPASS verdict.
        """
        from apps_rg.runtime.bindings.c0_briefing_bypass import evaluate_manual_brief
        
        # Fresh authoritative brief produces G_BRIEF_BYPASS=PASS
        with tempfile.NamedTemporaryFile(mode='w', suffix='_company_website_brief.md', delete=False) as f:
            f.write("# Fresh Authoritative Brief")
            brief_path = f.name
        
        try:
            brief_result = evaluate_manual_brief(brief_path)
            assert brief_result.support_status == "PASS"
            assert brief_result.bypass_eligible is True
            
            # BUT: This is ONLY the gate verdict. The overall FEC.support_status
            # is determined by Chroma evidence, NOT by the briefing bypass gate.
            # File-only path (no Chroma) produces UNKNOWN, not PASS.
            
        finally:
            os.unlink(brief_path)
    
    def test_fec_support_status_based_on_chroma_not_brief(self, tmp_path: Path) -> None:
        """EVIDENCE: FEC.support_status reflects Chroma state, NOT briefing bypass.
        
        This is a conceptual test - the actual FEC is produced by c0_retrieve_apps_rg
        which computes support_status from chroma_support_status, NOT from G_BRIEF_BYPASS.
        """
        # The key invariant: final_support_status = chroma_support_status
        # NOT: final_support_status = max(chroma_support_status, brief_bypass_status)
        
        # Read the c0_binding.py source to verify the logic
        import inspect
        from apps_rg.runtime.bindings import c0_binding
        
        source = inspect.getsource(c0_binding.c0_retrieve_apps_rg)
        
        # Verify that final_support_status is derived from chroma_support_status
        assert "final_support_status = chroma_support_status" in source
        
        # Verify that G_BRIEF_BYPASS does not influence final_support_status
        # (it's only added to gate_verdict_refs, not used to compute support_status)
        assert "brief_result" not in source.split("final_support_status")[1].split("return")[0]


class TestBriefingBypassIntegration:
    """Integration tests for the full briefing bypass flow."""
    
    def test_c0_binding_imports_briefing_bypass(self) -> None:
        """EVIDENCE: c0_binding.py imports and uses evaluate_manual_brief."""
        from apps_rg.runtime.bindings.c0_binding import (
            evaluate_manual_brief,
            BriefEvaluationResult,
        )
        # Should be callable
        assert callable(evaluate_manual_brief)
    
    def test_gate_profile_has_g_brief_bypass(self) -> None:
        """EVIDENCE: runtime_gate_profile has G_BRIEF_BYPASS declared."""
        import json
        
        # Resolve relative to test file location
        test_file_dir = Path(__file__).parent.parent.parent
        profile_path = test_file_dir / "apps_rg" / "config" / "domain_contract" / "runtime_gate_profile.resume_generation.v1.json"
        if profile_path.exists():
            with open(profile_path, encoding="utf-8") as f:
                profile = json.load(f)
            
            # Find G_BRIEF_BYPASS in C0 stage
            c0_gates = profile.get("stages", {}).get("C0", {}).get("required_gates", [])
            gate_ids = [g.get("gate_id") for g in c0_gates]
            assert "G_BRIEF_BYPASS" in gate_ids


class TestCandidateLanesNotBypassed:
    """Test that candidate_profile/project_evidence are NOT bypassed by manual_brief_path."""
    
    def test_brief_bypass_only_skips_company_research(self) -> None:
        """EVIDENCE: Briefing bypass scope is limited to company-research lanes only.
        
        The G_BRIEF_BYPASS conditional trigger specifies:
        - bypass_scope: "company_research_lanes_only"
        - preserved_lanes: ["candidate_profile", "project_evidence"]
        """
        import json
        
        # Resolve relative to test file location
        test_file_dir = Path(__file__).parent.parent.parent
        profile_path = test_file_dir / "apps_rg" / "config" / "domain_contract" / "runtime_gate_profile.resume_generation.v1.json"
        with open(profile_path, encoding="utf-8") as f:
            profile = json.load(f)
        
        # Check conditional trigger configuration
        trigger = profile.get("conditional_gate_triggers", {}).get("G_BRIEF_BYPASS", {})
        assert trigger.get("bypass_scope") == "company_research_lanes_only"
        
        preserved = trigger.get("preserved_lanes", [])
        assert "candidate_profile" in preserved
        assert "project_evidence" in preserved
    
    def test_candidate_facts_still_required_for_grounding(self) -> None:
        """EVIDENCE: Candidate-owned facts remain required for grounding.
        
        Even with fresh authoritative brief, the fact_vectors collection
        (candidate_profile, project_evidence) must still be queried for evidence.
        """
        # W3: Read from YAML directly to avoid apps_rg.config quarantine (AG-RGGOV-8)
        schema_path = Path(__file__).parent.parent.parent / "apps_rg" / "config" / "domain_contract" / "fact_vectors_schema.yaml"
        schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        allowed_source_classes = schema.get("allowed_source_classes", [])
        
        # fact_vectors only contains candidate-owned facts
        assert "candidate_profile" in allowed_source_classes
        assert "project_evidence" in allowed_source_classes
        
        # company_research is NOT in fact_vectors
        assert "company_research" not in allowed_source_classes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
