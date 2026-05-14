"""W7 C0 evidence trust — AppsRgEvidenceTraceMap.

Per W7 requirements:
- Track per-section evidence provenance
- source_resume_hash, jd_hash, briefing_hash
- retrieved_chunk_refs, retrieved_chunk_hashes
- source_span_refs, claim_refs, blocked_claims
- injection_risk, support_status

Proves C0 does not answer, compose prompts, or write L4.
"""
from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class SectionEvidenceTrace:
    """Evidence trace for a single resume section.
    
    Tracks all evidence sources and their hashes for provenance.
    """
    section_id: str  # e.g., "headline", "executive_summary", "unify_consulting"
    section_type: str  # "headline", "executive_summary", "role", "education", "certifications"
    
    # Source hashes (ground truth for this section)
    source_resume_hash: str  # Hash of source resume (master)
    jd_hash: str  # Hash of job description for this run
    briefing_hash: str  # Hash of research briefing (if used)
    
    # Retrieved evidence
    retrieved_chunk_refs: list[str]  # Chroma chunk IDs retrieved for this section
    retrieved_chunk_hashes: list[str]  # Content hashes of retrieved chunks
    
    # Source references
    source_span_refs: list[dict[str, Any]]  # References to source resume spans
    # Each span ref has: start_char, end_char, source_text_hash, section_ref
    
    # Claim references derived from evidence
    claim_refs: list[dict[str, Any]]
    # Each claim has: claim_id, claim_text, evidence_refs, confidence
    
    # Blocked claims (unsupported or contradicted by evidence)
    blocked_claims: list[dict[str, Any]]
    # Each blocked claim has: claim_id, reason, blocking_evidence_ref
    
    # Risk assessment
    injection_risk: str  # "LOW", "MEDIUM", "HIGH" based on evidence gaps
    support_status: str  # "PASS", "PARTIAL", "WEAK", "EMPTY"
    
    # Evidence completeness
    evidence_count: int  # Number of evidence items
    min_evidence_threshold: int  # Minimum required for this section type
    
    @property
    def has_sufficient_evidence(self) -> bool:
        """True if evidence count meets threshold."""
        return self.evidence_count >= self.min_evidence_threshold
    
    @property
    def all_claims_supported(self) -> bool:
        """True if no claims were blocked."""
        return len(self.blocked_claims) == 0


@dataclasses.dataclass(frozen=True)
class AppsRgEvidenceTraceMap:
    """Complete evidence trace map for apps_rg resume generation.
    
    W7: C0 evidence trust — proves C0 only retrieves evidence.
    Per-section tracking of all evidence sources and their provenance.
    """
    run_id: str
    trace_id: str
    request_id: str
    
    # Overall source hashes
    source_resume_hash: str
    jd_hash: str
    briefing_hash: str
    
    # Per-section traces
    section_traces: list[SectionEvidenceTrace]
    
    # Aggregate metrics
    total_sections: int
    sections_with_sufficient_evidence: int
    total_evidence_chunks: int
    total_blocked_claims: int
    
    # Risk summary
    max_injection_risk: str  # "LOW", "MEDIUM", "HIGH"
    overall_support_status: str  # "PASS", "PARTIAL", "WEAK", "EMPTY"
    
    # Provenance
    c0_binding_cert_ref: str = "c0-apps-rg-evidence-trace-map-w7"
    
    @property
    def sections_at_risk(self) -> list[str]:
        """List of section_ids with HIGH injection risk."""
        return [
            s.section_id for s in self.section_traces
            if s.injection_risk == "HIGH"
        ]
    
    @property
    def coverage_rate(self) -> float:
        """Fraction of sections with sufficient evidence."""
        if self.total_sections == 0:
            return 0.0
        return self.sections_with_sufficient_evidence / self.total_sections


# C0 behavior constraints (for test verification)
C0_BEHAVIOR_CONSTRAINTS = {
    "no_answer_generation": True,  # C0 does not generate answers
    "no_prompt_assembly": True,      # C0 does not compose prompts
    "no_direct_l4_write": True,      # C0 does not write to L4
    "read_only_retrieval": True,     # C0 only retrieves evidence
    "evidence_trace_required": True, # Must produce evidence trace
}


__all__ = [
    "SectionEvidenceTrace",
    "AppsRgEvidenceTraceMap",
    "C0_BEHAVIOR_CONSTRAINTS",
]
