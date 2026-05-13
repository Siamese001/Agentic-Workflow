"""W5C: Section and Aggregate Writeback Candidate Emission with Inertness Proof.

This module emits SectionWritebackCandidate and AggregateWritebackCandidate objects
for scored SectionArtifacts and MergedResumeArtifacts.

W5C Scope:
- Emit SectionWritebackCandidate for scored SectionArtifacts
- Emit AggregateWritebackCandidate for scored MergedResumeArtifacts
- Preserve section_id, section_artifact_refs, prompt_hash, evidence refs, scorer refs,
  benchmark/seed refs, quality scores, factual grounding scores, reuse eligibility,
  embedding metadata, vector namespace, write_scope
- Set inert_until_exit_uwg = true on every candidate
- Attach candidate refs to SectionArtifact/MergedResumeArtifact as inert refs

Inertness Guarantee (W5C Scope):
- Candidates are INERT — they contain metadata only
- NO write to semantic cache (L4 responsibility)
- NO write to vector DB (L4 responsibility)
- NO call to UWG (Exit responsibility)
- NO Exit commit (Exit responsibility)

Non-Goals (L4/Exit/W6/W7 scope):
- NO semantic cache writes (L4 scope)
- NO vector DB writes (L4 scope)
- NO UWG routing (Exit scope)
- NO Exit commit (Exit scope)
- NO L6 shadow learning (W7 scope)
"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import hashlib
import json

from apps_rg.runtime.schemas import (
    SectionArtifact,
    MergedResumeArtifact,
    SectionWritebackCandidate,
    AggregateWritebackCandidate,
)


# Canonical vector namespace for resume sections
SECTION_VECTOR_NAMESPACE = "apps_rg_resume_sections_v1"
AGGREGATE_VECTOR_NAMESPACE = "apps_rg_resume_aggregates_v1"

# Write scope enum values
WRITE_SCOPE_SECTION = "section_cache"
WRITE_SCOPE_AGGREGATE = "aggregate_cache"
WRITE_SCOPE_INDEX = "semantic_index"

# Reuse eligibility thresholds
REUSE_ELIGIBILITY_MIN_SCORE = 0.75
REUSE_ELIGIBILITY_G22_MIN = 0.950


@dataclass(frozen=True)
class WritebackCandidateResult:
    """Result of W5C writeback candidate emission.
    
    Contains inert candidates ready for L4/Exit gating.
    """
    success: bool
    error_message: Optional[str] = None
    
    # Candidates (INERT — not written until Exit/UWG/L4)
    section_candidates: List[SectionWritebackCandidate] = field(default_factory=list)
    aggregate_candidate: Optional[AggregateWritebackCandidate] = None
    
    # Source artifact refs (for traceability)
    source_section_artifact_ids: List[str] = field(default_factory=list)
    source_merged_artifact_id: Optional[str] = None
    
    # Inertness proof
    all_candidates_inert: bool = True  # W5C guarantees this
    inert_until_exit_uwg_verified: bool = True  # W5C guarantees this
    
    # Provenance
    writeback_version: str = "w5c-2026-05-12"
    emission_timestamp: Optional[datetime] = None


class WritebackCandidateEmitter:
    """W5C: Emit inert writeback candidates for scored artifacts.
    
    This class creates writeback candidates with full provenance metadata.
    All candidates remain INERT until processed by Exit/UWG/L4.
    """
    
    # Version for provenance
    WRITEBACK_VERSION = "w5c-2026-05-12"
    
    def emit_section_candidates(
        self,
        section_artifacts: List[SectionArtifact],
        run_context: Optional[Dict[str, Any]] = None
    ) -> WritebackCandidateResult:
        """Emit SectionWritebackCandidate for each scored SectionArtifact.
        
        W5C creates candidates only — no writes to cache/DB.
        """
        candidates = []
        source_ids = []
        
        for artifact in section_artifacts:
            # Build candidate with full provenance
            candidate = self._build_section_candidate(artifact, run_context)
            candidates.append(candidate)
            source_ids.append(artifact.artifact_id)
        
        return WritebackCandidateResult(
            success=True,
            section_candidates=candidates,
            source_section_artifact_ids=source_ids,
            all_candidates_inert=True,
            inert_until_exit_uwg_verified=True,
            writeback_version=self.WRITEBACK_VERSION,
            emission_timestamp=datetime.utcnow(),
        )
    
    def emit_aggregate_candidate(
        self,
        merged_artifact: MergedResumeArtifact,
        run_context: Optional[Dict[str, Any]] = None
    ) -> WritebackCandidateResult:
        """Emit AggregateWritebackCandidate for scored MergedResumeArtifact.
        
        W5C creates candidate only — no writes to cache/DB.
        """
        candidate = self._build_aggregate_candidate(merged_artifact, run_context)
        
        return WritebackCandidateResult(
            success=True,
            aggregate_candidate=candidate,
            source_merged_artifact_id=merged_artifact.artifact_id,
            all_candidates_inert=True,
            inert_until_exit_uwg_verified=True,
            writeback_version=self.WRITEBACK_VERSION,
            emission_timestamp=datetime.utcnow(),
        )
    
    def emit_all_candidates(
        self,
        section_artifacts: List[SectionArtifact],
        merged_artifact: MergedResumeArtifact,
        run_context: Optional[Dict[str, Any]] = None
    ) -> WritebackCandidateResult:
        """Emit both section and aggregate candidates.
        
        W5C bulk emission — all candidates remain INERT.
        """
        # Emit section candidates
        section_candidates = []
        section_source_ids = []
        
        for artifact in section_artifacts:
            candidate = self._build_section_candidate(artifact, run_context)
            section_candidates.append(candidate)
            section_source_ids.append(artifact.artifact_id)
        
        # Emit aggregate candidate
        aggregate_candidate = self._build_aggregate_candidate(merged_artifact, run_context)
        
        return WritebackCandidateResult(
            success=True,
            section_candidates=section_candidates,
            aggregate_candidate=aggregate_candidate,
            source_section_artifact_ids=section_source_ids,
            source_merged_artifact_id=merged_artifact.artifact_id,
            all_candidates_inert=True,
            inert_until_exit_uwg_verified=True,
            writeback_version=self.WRITEBACK_VERSION,
            emission_timestamp=datetime.utcnow(),
        )
    
    def _build_section_candidate(
        self,
        artifact: SectionArtifact,
        run_context: Optional[Dict[str, Any]]
    ) -> SectionWritebackCandidate:
        """Build SectionWritebackCandidate from scored SectionArtifact."""
        ctx = run_context or {}
        
        # Compute content hash for deduplication
        content_hash = self._compute_content_hash(artifact.generated_content)
        
        # Compute prompt hash from provenance
        prompt_hash = self._compute_prompt_hash(
            artifact.prompt_version,
            artifact.section_id,
            ctx.get("target_role"),
            ctx.get("target_level")
        )
        
        # Determine reuse eligibility
        reuse_eligible = self._determine_reuse_eligibility(artifact)
        
        # Extract scorer refs
        scorer_refs = self._extract_scorer_refs(artifact)
        
        # Extract benchmark/seed refs
        benchmark_refs = ctx.get("section_benchmark_refs", [])
        seed_refs = ctx.get("section_seed_refs", [])
        
        # Build candidate ID
        candidate_id = f"swb_{artifact.artifact_id}_{self._timestamp_suffix()}"
        
        return SectionWritebackCandidate(
            candidate_id=candidate_id,
            section_artifact_ref=artifact.artifact_id,
            section_id=artifact.section_id,
            
            # Content hash for deduplication
            content_hash=content_hash,
            prompt_hash=prompt_hash,
            
            # Evidence refs
            evidence_refs=ctx.get("evidence_refs", []),
            scorer_refs=scorer_refs,
            benchmark_refs=benchmark_refs,
            seed_refs=seed_refs,
            
            # Quality scores
            quality_score=artifact.section_scores.get("quality", 0.0),
            x1b_score=artifact.section_scores.get("x1b", 0.0),
            x1d_score=artifact.section_scores.get("x1d", 0.0),
            g21_header_block_score=artifact.section_scores.get("g21", 0.0),
            g22_factual_grounding_score=artifact.section_scores.get("g22", 0.0),
            g24_compliance_passed=artifact.section_scores.get("g24", 0.0) >= 0.5,
            g28_safety_passed=artifact.section_scores.get("g28", 0.0) >= 0.5,
            
            # Reuse eligibility
            reuse_eligible=reuse_eligible,
            reuse_eligibility_reason=self._reuse_reason(artifact) if reuse_eligible else "below_threshold",
            
            # Embedding metadata (for L4 to use)
            embedding_model_ref="text-embedding-3-large",  # L4 will use this
            embedding_dimensions=3072,
            
            # Vector namespace (for L4 routing)
            vector_namespace=SECTION_VECTOR_NAMESPACE,
            
            # Write scope
            write_scope=[WRITE_SCOPE_SECTION, WRITE_SCOPE_INDEX],
            
            # INERTNESS GUARANTEE — W5C sets this true
            inert_until_exit_uwg=True,
            
            # Provenance
            created_at=datetime.utcnow(),
            version=self.WRITEBACK_VERSION,
        )
    
    def _build_aggregate_candidate(
        self,
        artifact: MergedResumeArtifact,
        run_context: Optional[Dict[str, Any]]
    ) -> AggregateWritebackCandidate:
        """Build AggregateWritebackCandidate from scored MergedResumeArtifact."""
        ctx = run_context or {}
        
        # Compute content hash
        content_hash = self._compute_content_hash(artifact.merged_content)
        
        # Compute prompt hash
        prompt_hash = self._compute_prompt_hash(
            None,  # Aggregate has no single prompt version
            "aggregate",
            ctx.get("target_role"),
            ctx.get("target_level")
        )
        
        # Determine reuse eligibility
        g22_score = artifact.g22_factual_grounding_score
        g24_passed = artifact.g24_compliance_passed
        g28_passed = artifact.g28_safety_passed
        
        reuse_eligible = (
            g22_score >= REUSE_ELIGIBILITY_G22_MIN and
            g24_passed and
            g28_passed
        )
        
        # Extract scorer refs from aggregate_scores
        scorer_refs = list(artifact.aggregate_scores.keys()) if artifact.aggregate_scores else []
        
        # Build candidate ID
        candidate_id = f"awb_{artifact.artifact_id}_{self._timestamp_suffix()}"
        
        return AggregateWritebackCandidate(
            candidate_id=candidate_id,
            merged_resume_artifact_ref=artifact.artifact_id,
            
            # Content hash
            content_hash=content_hash,
            prompt_hash=prompt_hash,
            
            # Evidence refs
            evidence_refs=ctx.get("evidence_refs", []),
            scorer_refs=scorer_refs,
            benchmark_refs=ctx.get("aggregate_benchmark_refs", []),
            seed_refs=ctx.get("aggregate_seed_refs", []),
            
            # Quality scores
            quality_score=artifact.aggregate_scores.get("aggregate_x1bd_composite", 0.0),
            x1b_score=artifact.aggregate_scores.get("aggregate_x1b_result_ref", 0.0),
            x1d_score=artifact.aggregate_scores.get("aggregate_x1d_result_ref", 0.0),
            g22_factual_grounding_score=g22_score,
            g24_compliance_passed=g24_passed,
            g28_safety_passed=g28_passed,
            
            # Source section refs (traceability)
            source_section_artifact_refs=list(artifact.source_section_artifacts),
            
            # Reuse eligibility
            reuse_eligible=reuse_eligible,
            reuse_eligibility_reason="aggregate_g22_g24_g28_pass" if reuse_eligible else "below_threshold",
            
            # Embedding metadata
            embedding_model_ref="text-embedding-3-large",
            embedding_dimensions=3072,
            
            # Vector namespace
            vector_namespace=AGGREGATE_VECTOR_NAMESPACE,
            
            # Write scope
            write_scope=[WRITE_SCOPE_AGGREGATE, WRITE_SCOPE_INDEX],
            
            # INERTNESS GUARANTEE — W5C sets this true
            inert_until_exit_uwg=True,
            
            # Provenance
            created_at=datetime.utcnow(),
            version=self.WRITEBACK_VERSION,
        )
    
    def attach_candidates_to_artifacts(
        self,
        section_artifacts: List[SectionArtifact],
        merged_artifact: MergedResumeArtifact,
        candidate_result: WritebackCandidateResult
    ) -> tuple:
        """Attach inert candidate refs to artifacts.
        
        Returns new artifact instances with writeback_candidate field populated.
        Does NOT write to cache/DB.
        """
        # Attach section candidates
        updated_sections = []
        for artifact in section_artifacts:
            # Find matching candidate
            matching = [
                c for c in candidate_result.section_candidates
                if c.section_artifact_ref == artifact.artifact_id
            ]
            if matching:
                # Create new artifact with candidate attached
                updated = replace(artifact, writeback_candidate=matching[0])
                updated_sections.append(updated)
            else:
                updated_sections.append(artifact)
        
        # Attach aggregate candidate
        updated_merged = merged_artifact
        if candidate_result.aggregate_candidate:
            updated_merged = replace(
                merged_artifact,
                writeback_candidate=candidate_result.aggregate_candidate
            )
        
        return updated_sections, updated_merged
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]
    
    def _compute_prompt_hash(
        self,
        prompt_version: Optional[str],
        section_id: str,
        target_role: Optional[str],
        target_level: Optional[str]
    ) -> str:
        """Compute hash of prompt configuration for versioning."""
        data = {
            "prompt_version": prompt_version or "unknown",
            "section_id": section_id,
            "target_role": target_role or "default",
            "target_level": target_level or "default",
        }
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()[:32]
    
    def _determine_reuse_eligibility(self, artifact: SectionArtifact) -> bool:
        """Determine if section is eligible for reuse."""
        quality = artifact.section_scores.get("quality", 0.0)
        g22 = artifact.section_scores.get("g22", 0.0)
        g24 = artifact.section_scores.get("g24", 0.0) >= 0.5
        g28 = artifact.section_scores.get("g28", 0.0) >= 0.5
        
        return (
            quality >= REUSE_ELIGIBILITY_MIN_SCORE and
            g22 >= REUSE_ELIGIBILITY_G22_MIN and
            g24 and
            g28
        )
    
    def _extract_scorer_refs(self, artifact: SectionArtifact) -> List[str]:
        """Extract scorer references from artifact scores."""
        # Build scorer refs from score keys
        refs = []
        for key in artifact.section_scores.keys():
            if key in ["x1b", "x1d", "quality", "g21", "g22", "g24", "g28"]:
                refs.append(f"section_scorer:{key}")
        return refs if refs else ["section_scorer:default"]
    
    def _reuse_reason(self, artifact: SectionArtifact) -> str:
        """Generate reuse eligibility reason."""
        return "quality_g22_g24_g28_pass"
    
    def _timestamp_suffix(self) -> str:
        """Generate timestamp suffix for candidate IDs."""
        return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:16]


# Convenience functions for direct use

def emit_section_writeback_candidates(
    section_artifacts: List[SectionArtifact],
    run_context: Optional[Dict[str, Any]] = None
) -> WritebackCandidateResult:
    """Convenience wrapper for section candidate emission.
    
    W5C: Creates inert candidates only — no writes.
    """
    emitter = WritebackCandidateEmitter()
    return emitter.emit_section_candidates(section_artifacts, run_context)


def emit_aggregate_writeback_candidate(
    merged_artifact: MergedResumeArtifact,
    run_context: Optional[Dict[str, Any]] = None
) -> WritebackCandidateResult:
    """Convenience wrapper for aggregate candidate emission.
    
    W5C: Creates inert candidate only — no writes.
    """
    emitter = WritebackCandidateEmitter()
    return emitter.emit_aggregate_candidate(merged_artifact, run_context)


def emit_all_writeback_candidates(
    section_artifacts: List[SectionArtifact],
    merged_artifact: MergedResumeArtifact,
    run_context: Optional[Dict[str, Any]] = None
) -> WritebackCandidateResult:
    """Convenience wrapper for bulk candidate emission.
    
    W5C: Creates all inert candidates — no writes.
    """
    emitter = WritebackCandidateEmitter()
    return emitter.emit_all_candidates(section_artifacts, merged_artifact, run_context)


def attach_writeback_candidates(
    section_artifacts: List[SectionArtifact],
    merged_artifact: MergedResumeArtifact,
    candidate_result: WritebackCandidateResult
) -> tuple:
    """Attach inert candidates to artifacts.
    
    W5C: Attaches refs only — no cache/DB writes.
    """
    emitter = WritebackCandidateEmitter()
    return emitter.attach_candidates_to_artifacts(
        section_artifacts, merged_artifact, candidate_result
    )
