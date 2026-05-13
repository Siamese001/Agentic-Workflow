"""W5A: Minimal merge path prerequisite for W5B aggregate scoring.

This module provides the merge binding that assembles scored SectionArtifacts
into a MergedResumeArtifact without performing aggregate scoring.

W5A Scope:
- Accept scored SectionArtifacts from W5
- Validate canonical section coverage
- Preserve section_id and artifact traceability
- Assemble a MergedResumeArtifact using W3A schema
- Mark aggregate scorer refs as pending (W5B scope)
- Mark writeback candidates as None/inert (W5C scope)

Non-Goals (W5B/W5C scope):
- NO aggregate scoring (x1b_result_ref, x1d_result_ref for whole resume)
- NO writeback candidate emission (inert until Exit/UWG/L4)
- NO L6 shadow learning (W7 scope)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from apps_rg.runtime.schemas import (
    SectionArtifact,
    MergedResumeArtifact,
    AggregateWritebackCandidate,
)


# W3A Canonical section list for full resume coverage
CANONICAL_SECTION_IDS = [
    "headline",
    "executive_summary",
    "professional_summary",
    "insurtech_expertise",  # P1 promoted
    "ey_methodology",       # P1 promoted
    "core_competencies",
    "experience_highlights",
    "key_achievements",
    "board_positions",
    "recent_experience",
    "prior_experience",
    "early_career",         # P2 compactness
    "education",            # P2 compactness
    "certifications_high_signal",
    "certifications_low_signal",  # P2 compactness
]


@dataclass(frozen=True)
class MergeInput:
    """Input contract for W5A merge binding.
    
    Accepts scored SectionArtifacts from W5 section scorer.
    """
    run_id: str
    section_artifacts: List[SectionArtifact]  # From W5 scorer
    run_context: Dict[str, Any] = field(default_factory=dict)
    
    # Attribution
    source_resume_digest: Optional[str] = None


@dataclass(frozen=True)
class MergeResult:
    """Result of W5A merge binding.
    
    Contains MergedResumeArtifact with section traceability preserved.
    Aggregate scoring refs marked pending (W5B scope).
    """
    success: bool
    merged_artifact: Optional[MergedResumeArtifact] = None
    error_message: Optional[str] = None
    
    # Section coverage report
    sections_present: List[str] = field(default_factory=list)
    sections_missing: List[str] = field(default_factory=list)
    coverage_ratio: float = 0.0


class MergeBinding:
    """W5A: Minimal merge path binding.
    
    Assembles scored SectionArtifacts into MergedResumeArtifact.
    Does NOT perform aggregate scoring (W5B scope).
    """
    
    # Version for provenance
    MERGE_BINDING_VERSION = "w5a-2026-05-12"
    
    def merge_sections(self, merge_input: MergeInput) -> MergeResult:
        """Assemble scored sections into merged resume artifact.
        
        W5A scope: Merge only, no aggregate scoring.
        """
        # Validate section coverage
        coverage_result = self._validate_section_coverage(
            merge_input.section_artifacts
        )
        
        if coverage_result.coverage_ratio < 0.5:
            return MergeResult(
                success=False,
                error_message=f"Insufficient section coverage: {coverage_result.coverage_ratio:.0%}",
                sections_present=coverage_result.sections_present,
                sections_missing=coverage_result.sections_missing,
                coverage_ratio=coverage_result.coverage_ratio,
            )
        
        # Assemble merged content in canonical order
        merged_content = self._assemble_content(
            merge_input.section_artifacts,
            coverage_result.section_order
        )
        
        # Collect source artifact IDs for traceability
        source_artifact_ids = [
            art.artifact_id for art in merge_input.section_artifacts
        ]
        
        # Build MergedResumeArtifact (W3A schema)
        merged_artifact = MergedResumeArtifact(
            artifact_id=str(uuid.uuid4()),
            run_id=merge_input.run_id,
            merged_content=merged_content,
            merge_timestamp=datetime.utcnow(),
            source_section_artifacts=source_artifact_ids,
            # Aggregate scores: pending (W5B scope)
            aggregate_scores={
                "aggregate_x1b_result_ref": "pending_w5b",
                "aggregate_x1d_result_ref": "pending_w5b",
                "aggregate_x1bd_composite": 0.0,
            },
            g22_factual_grounding_score=0.0,  # Pending W5B
            # Whole-run gates: pending (W5B/W6 scope)
            g24_compliance_passed=False,
            g28_safety_passed=False,
            # Writeback candidate: None/inert (W5C scope)
            writeback_candidate=None,
            # Provenance
            merge_binding_version=self.MERGE_BINDING_VERSION,
            disposition_digest=None,  # Set by Exit layer
        )
        
        return MergeResult(
            success=True,
            merged_artifact=merged_artifact,
            sections_present=coverage_result.sections_present,
            sections_missing=coverage_result.sections_missing,
            coverage_ratio=coverage_result.coverage_ratio,
        )
    
    def _validate_section_coverage(self, artifacts: List[SectionArtifact]) -> 'CoverageResult':
        """Check which canonical sections are present."""
        present_ids = {art.section_id for art in artifacts}
        
        sections_present = []
        sections_missing = []
        
        # Determine order based on canonical list
        section_order = []
        for section_id in CANONICAL_SECTION_IDS:
            if section_id in present_ids:
                sections_present.append(section_id)
                section_order.append(section_id)
            else:
                sections_missing.append(section_id)
        
        # Add any non-canonical sections at end
        for art in artifacts:
            if art.section_id not in CANONICAL_SECTION_IDS:
                sections_present.append(art.section_id)
                section_order.append(art.section_id)
        
        coverage_ratio = len(sections_present) / len(CANONICAL_SECTION_IDS) if CANONICAL_SECTION_IDS else 0.0
        
        return CoverageResult(
            sections_present=sections_present,
            sections_missing=sections_missing,
            section_order=section_order,
            coverage_ratio=coverage_ratio,
        )
    
    def _assemble_content(self, artifacts: List[SectionArtifact], order: List[str]) -> str:
        """Assemble section content in canonical order."""
        # Build lookup by section_id
        artifact_by_section = {art.section_id: art for art in artifacts}
        
        parts = []
        for section_id in order:
            if section_id in artifact_by_section:
                art = artifact_by_section[section_id]
                parts.append(f"## {section_id}\n")
                parts.append(art.generated_content)
                parts.append("\n\n")
        
        return "".join(parts).strip()


@dataclass(frozen=True)
class CoverageResult:
    """Internal result of section coverage validation."""
    sections_present: List[str]
    sections_missing: List[str]
    section_order: List[str]
    coverage_ratio: float


# Convenience function for direct use
def merge_scored_sections(
    run_id: str,
    section_artifacts: List[SectionArtifact],
    run_context: Optional[Dict[str, Any]] = None,
    source_resume_digest: Optional[str] = None,
) -> MergeResult:
    """Convenience wrapper for merge binding.
    
    Accepts scored SectionArtifacts from W5, returns MergeResult.
    """
    binding = MergeBinding()
    merge_input = MergeInput(
        run_id=run_id,
        section_artifacts=section_artifacts,
        run_context=run_context or {},
        source_resume_digest=source_resume_digest,
    )
    return binding.merge_sections(merge_input)
