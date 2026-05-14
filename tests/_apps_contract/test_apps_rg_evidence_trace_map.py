"""W7 tests: AppsRgEvidenceTraceMap — C0 evidence trust per-section tracking."""
from __future__ import annotations

import unittest

from apps_rg.runtime.bindings.c0_evidence_trace_map import (
    AppsRgEvidenceTraceMap,
    SectionEvidenceTrace,
    C0_BEHAVIOR_CONSTRAINTS,
)


class TestSectionEvidenceTrace(unittest.TestCase):
    """Test per-section evidence trace."""

    def test_trace_creation(self) -> None:
        """Section trace can be created with all fields."""
        trace = SectionEvidenceTrace(
            section_id="executive_summary",
            section_type="executive_summary",
            source_resume_hash="sha256:resume_abc",
            jd_hash="sha256:jd_abc",
            briefing_hash="sha256:brief_abc",
            retrieved_chunk_refs=["chunk_1", "chunk_2", "chunk_3"],
            retrieved_chunk_hashes=["sha256:c1", "sha256:c2", "sha256:c3"],
            source_span_refs=[
                {"start_char": 0, "end_char": 100, "source_text_hash": "sha256:s1"},
            ],
            claim_refs=[
                {"claim_id": "c1", "claim_text": "Led AI initiatives", "evidence_refs": ["chunk_1"]},
            ],
            blocked_claims=[],
            injection_risk="LOW",
            support_status="PASS",
            evidence_count=3,
            min_evidence_threshold=2,
        )
        
        self.assertEqual(trace.section_id, "executive_summary")
        self.assertTrue(trace.has_sufficient_evidence)
        self.assertTrue(trace.all_claims_supported)

    def test_insufficient_evidence_detection(self) -> None:
        """Detect when evidence count is below threshold."""
        trace = SectionEvidenceTrace(
            section_id="weak_section",
            section_type="role",
            source_resume_hash="sha256:resume_abc",
            jd_hash="sha256:jd_abc",
            briefing_hash="sha256:brief_abc",
            retrieved_chunk_refs=["chunk_1"],  # Only 1
            retrieved_chunk_hashes=["sha256:c1"],
            source_span_refs=[],
            claim_refs=[],
            blocked_claims=[],
            injection_risk="HIGH",
            support_status="WEAK",
            evidence_count=1,
            min_evidence_threshold=3,  # Need 3, have 1
        )
        
        self.assertFalse(trace.has_sufficient_evidence)
        self.assertEqual(trace.injection_risk, "HIGH")

    def test_blocked_claims_detection(self) -> None:
        """Detect when claims are blocked due to lack of support."""
        trace = SectionEvidenceTrace(
            section_id="contested_section",
            section_type="role",
            source_resume_hash="sha256:resume_abc",
            jd_hash="sha256:jd_abc",
            briefing_hash="sha256:brief_abc",
            retrieved_chunk_refs=["chunk_1"],
            retrieved_chunk_hashes=["sha256:c1"],
            source_span_refs=[],
            claim_refs=[
                {"claim_id": "c1", "claim_text": "Valid claim", "evidence_refs": ["chunk_1"]},
                {"claim_id": "c2", "claim_text": "Unsupported claim", "evidence_refs": []},
            ],
            blocked_claims=[
                {"claim_id": "c2", "reason": "No evidence", "blocking_evidence_ref": ""},
            ],
            injection_risk="MEDIUM",
            support_status="PARTIAL",
            evidence_count=1,
            min_evidence_threshold=1,
        )
        
        self.assertFalse(trace.all_claims_supported)
        self.assertEqual(len(trace.blocked_claims), 1)

    def test_evidence_count_matches_lists(self) -> None:
        """evidence_count should match length of retrieved_chunk_refs."""
        chunk_refs = ["chunk_1", "chunk_2", "chunk_3", "chunk_4"]
        trace = SectionEvidenceTrace(
            section_id="well_supported",
            section_type="role",
            source_resume_hash="sha256:resume_abc",
            jd_hash="sha256:jd_abc",
            briefing_hash="sha256:brief_abc",
            retrieved_chunk_refs=chunk_refs,
            retrieved_chunk_hashes=["sha256:c"] * len(chunk_refs),
            source_span_refs=[],
            claim_refs=[],
            blocked_claims=[],
            injection_risk="LOW",
            support_status="PASS",
            evidence_count=len(chunk_refs),
            min_evidence_threshold=2,
        )
        
        self.assertEqual(trace.evidence_count, len(chunk_refs))
        self.assertTrue(trace.has_sufficient_evidence)


class TestAppsRgEvidenceTraceMap(unittest.TestCase):
    """Test full evidence trace map."""

    def test_trace_map_creation(self) -> None:
        """Evidence trace map can be created with all fields."""
        section_traces = [
            SectionEvidenceTrace(
                section_id="headline",
                section_type="headline",
                source_resume_hash="sha256:master",
                jd_hash="sha256:jd",
                briefing_hash="sha256:brief",
                retrieved_chunk_refs=[],
                retrieved_chunk_hashes=[],
                source_span_refs=[],
                claim_refs=[],
                blocked_claims=[],
                injection_risk="LOW",
                support_status="PASS",
                evidence_count=0,
                min_evidence_threshold=0,
            ),
            SectionEvidenceTrace(
                section_id="executive_summary",
                section_type="executive_summary",
                source_resume_hash="sha256:master",
                jd_hash="sha256:jd",
                briefing_hash="sha256:brief",
                retrieved_chunk_refs=["c1", "c2"],
                retrieved_chunk_hashes=["h1", "h2"],
                source_span_refs=[],
                claim_refs=[],
                blocked_claims=[],
                injection_risk="LOW",
                support_status="PASS",
                evidence_count=2,
                min_evidence_threshold=1,
            ),
        ]
        
        trace_map = AppsRgEvidenceTraceMap(
            run_id="run_001",
            trace_id="trace_001",
            request_id="req_001",
            source_resume_hash="sha256:master",
            jd_hash="sha256:jd",
            briefing_hash="sha256:brief",
            section_traces=section_traces,
            total_sections=2,
            sections_with_sufficient_evidence=2,
            total_evidence_chunks=2,
            total_blocked_claims=0,
            max_injection_risk="LOW",
            overall_support_status="PASS",
        )
        
        self.assertEqual(trace_map.total_sections, 2)
        self.assertEqual(trace_map.coverage_rate, 1.0)
        self.assertEqual(trace_map.sections_at_risk, [])

    def test_sections_at_risk_detection(self) -> None:
        """Identify sections with HIGH injection risk."""
        section_traces = [
            SectionEvidenceTrace(
                section_id="safe_section",
                section_type="role",
                source_resume_hash="sha256:master",
                jd_hash="sha256:jd",
                briefing_hash="sha256:brief",
                retrieved_chunk_refs=["c1"],
                retrieved_chunk_hashes=["h1"],
                source_span_refs=[],
                claim_refs=[],
                blocked_claims=[],
                injection_risk="LOW",
                support_status="PASS",
                evidence_count=1,
                min_evidence_threshold=1,
            ),
            SectionEvidenceTrace(
                section_id="risky_section",
                section_type="role",
                source_resume_hash="sha256:master",
                jd_hash="sha256:jd",
                briefing_hash="sha256:brief",
                retrieved_chunk_refs=[],
                retrieved_chunk_hashes=[],
                source_span_refs=[],
                claim_refs=[],
                blocked_claims=[],
                injection_risk="HIGH",
                support_status="EMPTY",
                evidence_count=0,
                min_evidence_threshold=2,
            ),
        ]
        
        trace_map = AppsRgEvidenceTraceMap(
            run_id="run_001",
            trace_id="trace_001",
            request_id="req_001",
            source_resume_hash="sha256:master",
            jd_hash="sha256:jd",
            briefing_hash="sha256:brief",
            section_traces=section_traces,
            total_sections=2,
            sections_with_sufficient_evidence=1,
            total_evidence_chunks=1,
            total_blocked_claims=0,
            max_injection_risk="HIGH",
            overall_support_status="PARTIAL",
        )
        
        self.assertEqual(trace_map.sections_at_risk, ["risky_section"])
        self.assertEqual(trace_map.coverage_rate, 0.5)

    def test_c0_cert_ref_present(self) -> None:
        """C0 binding cert ref is present for provenance."""
        trace_map = AppsRgEvidenceTraceMap(
            run_id="run_001",
            trace_id="trace_001",
            request_id="req_001",
            source_resume_hash="sha256:master",
            jd_hash="sha256:jd",
            briefing_hash="sha256:brief",
            section_traces=[],
            total_sections=0,
            sections_with_sufficient_evidence=0,
            total_evidence_chunks=0,
            total_blocked_claims=0,
            max_injection_risk="LOW",
            overall_support_status="PASS",
        )
        
        self.assertEqual(
            trace_map.c0_binding_cert_ref,
            "c0-apps-rg-evidence-trace-map-w7"
        )


class TestC0BehaviorConstraints(unittest.TestCase):
    """Test C0 behavior constraints — no answer generation, no prompt assembly."""

    def test_c0_no_answer_generation(self) -> None:
        """C0 does not generate answers — only retrieves evidence."""
        self.assertTrue(C0_BEHAVIOR_CONSTRAINTS["no_answer_generation"])

    def test_c0_no_prompt_assembly(self) -> None:
        """C0 does not compose prompts — only retrieves evidence."""
        self.assertTrue(C0_BEHAVIOR_CONSTRAINTS["no_prompt_assembly"])

    def test_c0_no_direct_l4_write(self) -> None:
        """C0 does not write directly to L4."""
        self.assertTrue(C0_BEHAVIOR_CONSTRAINTS["no_direct_l4_write"])

    def test_c0_read_only_retrieval(self) -> None:
        """C0 is read-only retrieval."""
        self.assertTrue(C0_BEHAVIOR_CONSTRAINTS["read_only_retrieval"])

    def test_c0_evidence_trace_required(self) -> None:
        """C0 must produce evidence trace."""
        self.assertTrue(C0_BEHAVIOR_CONSTRAINTS["evidence_trace_required"])


if __name__ == "__main__":
    unittest.main()
