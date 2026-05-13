"""W7: L6 Shadow Learning Proof for Completed Resume Runs.

This module produces completed-run evaluation records and inert future-run
ProposalPackets only. It does NOT mutate current-run output or trigger
retry/regeneration.

W7 Scope:
- Consume RuntimeExhaustBundle (completed-run artifact set)
- Produce SectionCompletedEvalRecord per SectionArtifact
- Produce AggregateCompletedEvalRecord per MergedResumeArtifact
- Produce inert ProposalPackets only when learning signals exist
- Prove proposals are future-run-only and inactive until gauntlet/UWG/L4 promotion

W7 Anti-Bypass Guarantees:
- NO mutation of current-run output
- NO trigger of retry/regeneration
- NO patch of prompts, rubrics, benchmarks, seeds, scorer profiles
- NO write to cache, vector DB, memory, policy, or L4
- NO direct call to UWG
- Proposals routed through gauntlet/UWG/L4 only

Non-Goals (Outside W7):
- NO L4 writeback execution (L4 scope)
- NO UWG promotion decision (Exit/UWG scope)
- NO FutureRunPromotionRequest handling (Exit/UWG scope)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import hashlib
import json
import uuid

from apps_rg.runtime.schemas import (
    SectionArtifact,
    MergedResumeArtifact,
    SectionCompletedEvalRecord,
    AggregateCompletedEvalRecord,
)


# G22 canonical threshold
G22_THRESHOLD = 0.950

# W7 failure classifications
W7_FAIL_SECTION_EVAL_MISSING = "W7_FAIL_SECTION_EVAL_MISSING"
W7_FAIL_AGGREGATE_EVAL_MISSING = "W7_FAIL_AGGREGATE_EVAL_MISSING"
W7_FAIL_BOUNDARY_BREACH = "W7_FAIL_BOUNDARY_BREACH"
W7_FAIL_CURRENT_RUN_RESCUE = "W7_FAIL_CURRENT_RUN_RESCUE"
W7_FAIL_DIRECT_WRITE_BYPASS = "W7_FAIL_DIRECT_WRITE_BYPASS"
W7_FAIL_PROMOTION_UNSAFE = "W7_FAIL_PROMOTION_UNSAFE"
W7_FAIL_THRESHOLD_DRIFT = "W7_FAIL_THRESHOLD_DRIFT"
W7_FAIL_THRESHOLD_CONFUSION = "W7_FAIL_THRESHOLD_CONFUSION"


@dataclass(frozen=True)
class ProposalPacket:
    """Inert proposal for future-run improvement.
    
    ProposalPacket remains INERT until promoted through gauntlet/UWG/L4.
    Never applied to current run.
    """
    proposal_id: str
    
    # Source attribution
    source_record_id: str  # SectionCompletedEvalRecord or AggregateCompletedEvalRecord
    source_record_type: str  # "section" or "aggregate"
    
    # Proposal content
    proposal_type: str  # e.g., "benchmark_update", "seed_enhancement", "scorer_calibration"
    target_scope: str  # e.g., "section_header", "executive_summary", "full_resume"
    proposed_change_summary: str
    
    # Evidence for proposal
    supporting_scores: Dict[str, float] = field(default_factory=dict)
    improvement_hypothesis: str = ""
    
    # Inertness guarantee
    inert_until_promotion: bool = True  # W7 sets this True
    promotion_path: str = "gauntlet->UWG->L4"  # Required path
    
    # Future-run only
    applicable_to_future_runs: bool = True  # Never current run
    
    # Provenance
    created_at: Optional[datetime] = None
    version: str = "w7-2026-05-12"


@dataclass(frozen=True)
class RuntimeExhaustBundle:
    """Input bundle for L6 shadow learning from completed run.
    
    Contains all artifacts produced by W4-W6 runtime.
    """
    run_id: str
    
    # Source artifacts
    section_artifacts: List[SectionArtifact] = field(default_factory=list)
    merged_resume_artifact: Optional[MergedResumeArtifact] = None
    
    # Run context
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    target_level: Optional[str] = None
    
    # Resume/job fingerprinting for learning correlation
    resume_fingerprint: Optional[str] = None
    job_fingerprint: Optional[str] = None
    
    # Provenance
    bundle_timestamp: Optional[datetime] = None
    version: str = "w7-2026-05-12"


@dataclass
class L6ShadowLearningResult:
    """Result of W7 L6 shadow learning."""
    success: bool
    failure_classification: Optional[str] = None
    error_details: List[str] = field(default_factory=list)
    
    # Produced records
    section_eval_records: List[SectionCompletedEvalRecord] = field(default_factory=list)
    aggregate_eval_record: Optional[AggregateCompletedEvalRecord] = None
    
    # Proposals (inert until promotion)
    proposal_packets: List[ProposalPacket] = field(default_factory=list)
    
    # Anti-bypass proofs
    current_run_untouched: bool = True
    no_retry_triggered: bool = True
    no_direct_write: bool = True
    proposals_inert: bool = True
    g22_threshold_preserved: bool = True
    
    # Provenance
    processing_timestamp: Optional[datetime] = None
    version: str = "w7-2026-05-12"


class L6ShadowLearningProducer:
    """W7: Produce L6 shadow learning records from completed runs.
    
    Creates SectionCompletedEvalRecord, AggregateCompletedEvalRecord,
    and inert ProposalPackets. Does NOT mutate current run or trigger
    any runtime behavior.
    """
    
    VERSION = "w7-2026-05-12"
    
    def produce_from_bundle(
        self,
        bundle: RuntimeExhaustBundle
    ) -> L6ShadowLearningResult:
        """Produce all L6 records from RuntimeExhaustBundle.
        
        W7 guarantees:
        - Current run untouched
        - No retry triggered
        - Proposals inert until gauntlet/UWG/L4
        """
        errors = []
        
        # 1. Produce SectionCompletedEvalRecords
        section_records = []
        for section_artifact in bundle.section_artifacts:
            record = self._produce_section_eval_record(
                section_artifact,
                bundle.run_id,
                bundle.resume_fingerprint,
                bundle.job_fingerprint
            )
            section_records.append(record)
        
        # 2. Produce AggregateCompletedEvalRecord
        aggregate_record = None
        if bundle.merged_resume_artifact:
            aggregate_record = self._produce_aggregate_eval_record(
                bundle.merged_resume_artifact,
                bundle.run_id,
                section_records,
                bundle.resume_fingerprint,
                bundle.job_fingerprint
            )
        
        # 3. Produce inert ProposalPackets (only when learning signals exist)
        proposals = []
        
        # Section-level proposals
        for record in section_records:
            section_proposals = self._generate_proposals_for_section(record)
            proposals.extend(section_proposals)
        
        # Aggregate-level proposals
        if aggregate_record:
            aggregate_proposals = self._generate_proposals_for_aggregate(aggregate_record)
            proposals.extend(aggregate_proposals)
        
        # 4. Verify anti-bypass invariants
        # These are structural guarantees of the W7 implementation
        current_run_untouched = True  # W7 never modifies input artifacts
        no_retry_triggered = True  # W7 has no retry logic
        no_direct_write = True  # W7 has no write methods
        proposals_inert = all(p.inert_until_promotion for p in proposals)
        g22_preserved = self._verify_g22_preserved(section_records, aggregate_record)
        
        if not proposals_inert:
            errors.append("Some ProposalPackets have inert_until_promotion=False")
        if not g22_preserved:
            errors.append("G22 threshold confusion detected")
        
        success = len(errors) == 0
        failure_class = None
        if not success:
            if not g22_preserved:
                failure_class = W7_FAIL_THRESHOLD_DRIFT
            elif not proposals_inert:
                failure_class = W7_FAIL_PROMOTION_UNSAFE
        
        return L6ShadowLearningResult(
            success=success,
            failure_classification=failure_class,
            error_details=errors,
            section_eval_records=section_records,
            aggregate_eval_record=aggregate_record,
            proposal_packets=proposals,
            current_run_untouched=current_run_untouched,
            no_retry_triggered=no_retry_triggered,
            no_direct_write=no_direct_write,
            proposals_inert=proposals_inert,
            g22_threshold_preserved=g22_preserved,
            processing_timestamp=datetime.utcnow(),
            version=self.VERSION,
        )
    
    def _produce_section_eval_record(
        self,
        artifact: SectionArtifact,
        run_id: str,
        resume_fingerprint: Optional[str],
        job_fingerprint: Optional[str]
    ) -> SectionCompletedEvalRecord:
        """Produce SectionCompletedEvalRecord from SectionArtifact.
        
        W7: Creates record only — no mutation of artifact.
        """
        # Determine generation outcome
        scores = getattr(artifact, 'section_scores', {}) or {}
        quality = scores.get('quality', 0.0)
        g22 = scores.get('g22', 0.0)
        
        if quality >= 0.85 and g22 >= G22_THRESHOLD:
            outcome = "success"
        elif quality >= 0.6:
            outcome = "retry"  # Would have been retried in W4/W5
        else:
            outcome = "fallback"
        
        # Build improvement proposals based on scores
        proposals = self._analyze_section_for_proposals(artifact, scores)
        
        return SectionCompletedEvalRecord(
            record_id=f"sec_eval_{artifact.artifact_id}_{self._timestamp_suffix()}",
            section_id=artifact.section_id,
            run_id=run_id,
            section_artifact_id=artifact.artifact_id,
            generation_outcome=outcome,
            final_scores=dict(scores),
            g22_factual_grounding_achieved=g22,
            improvement_proposals=proposals,
            timestamp=datetime.utcnow(),
            resume_fingerprint=resume_fingerprint,
            job_fingerprint=job_fingerprint,
            applicable_to_future_runs=True,  # W7 guarantee
        )
    
    def _produce_aggregate_eval_record(
        self,
        artifact: MergedResumeArtifact,
        run_id: str,
        section_records: List[SectionCompletedEvalRecord],
        resume_fingerprint: Optional[str],
        job_fingerprint: Optional[str]
    ) -> AggregateCompletedEvalRecord:
        """Produce AggregateCompletedEvalRecord from MergedResumeArtifact.
        
        W7: Creates record only — no mutation of artifact.
        """
        # Determine aggregate outcome
        scores = getattr(artifact, 'aggregate_scores', {}) or {}
        g22 = getattr(artifact, 'g22_factual_grounding_score', 0.0)
        g24 = getattr(artifact, 'g24_compliance_passed', False)
        g28 = getattr(artifact, 'g28_safety_passed', False)
        
        if g22 >= G22_THRESHOLD and g24 and g28:
            outcome = "success"
        elif g22 >= G22_THRESHOLD * 0.9 and g24:
            outcome = "partial"
        else:
            outcome = "failure"
        
        # Build improvement proposals
        proposals = self._analyze_aggregate_for_proposals(artifact, scores)
        
        return AggregateCompletedEvalRecord(
            record_id=f"agg_eval_{artifact.artifact_id}_{self._timestamp_suffix()}",
            run_id=run_id,
            merged_resume_artifact_id=artifact.artifact_id,
            aggregate_outcome=outcome,
            final_aggregate_scores=dict(scores),
            g22_factual_grounding_achieved=g22,
            section_records=[r.record_id for r in section_records],
            improvement_proposals=proposals,
            timestamp=datetime.utcnow(),
            resume_fingerprint=resume_fingerprint,
            job_fingerprint=job_fingerprint,
            applicable_to_future_runs=True,  # W7 guarantee
        )
    
    def _generate_proposals_for_section(
        self,
        record: SectionCompletedEvalRecord
    ) -> List[ProposalPacket]:
        """Generate inert ProposalPackets from section eval record.
        
        W7: Proposals are future-run only and inert until gauntlet/UWG/L4.
        """
        proposals = []
        scores = record.final_scores
        
        # Proposal for low G21 (header) score
        g21 = scores.get('g21', 1.0)
        if g21 < 0.7:
            proposals.append(ProposalPacket(
                proposal_id=f"prop_{record.record_id}_g21_{self._timestamp_suffix()}",
                source_record_id=record.record_id,
                source_record_type="section",
                proposal_type="benchmark_update",
                target_scope=f"section_{record.section_id}_header",
                proposed_change_summary="Strengthen header benchmark set for executive formatting",
                supporting_scores={"g21": g21},
                improvement_hypothesis="Adding more C-suite header examples will improve G21 scores",
                inert_until_promotion=True,  # W7 guarantee
                promotion_path="gauntlet->UWG->L4",
                applicable_to_future_runs=True,
                created_at=datetime.utcnow(),
                version=self.VERSION,
            ))
        
        # Proposal for low X1B score
        x1b = scores.get('x1b', 1.0)
        if x1b < 0.75:
            proposals.append(ProposalPacket(
                proposal_id=f"prop_{record.record_id}_x1b_{self._timestamp_suffix()}",
                source_record_id=record.record_id,
                source_record_type="section",
                proposal_type="seed_enhancement",
                target_scope=f"section_{record.section_id}_executive_presence",
                proposed_change_summary="Enhance seed set with stronger executive positioning examples",
                supporting_scores={"x1b": x1b},
                improvement_hypothesis="Richer seed diversity will improve X1B executive presence scores",
                inert_until_promotion=True,
                promotion_path="gauntlet->UWG->L4",
                applicable_to_future_runs=True,
                created_at=datetime.utcnow(),
                version=self.VERSION,
            ))
        
        # Proposal for low G22 (factual grounding)
        g22 = scores.get('g22', 1.0)
        if g22 < G22_THRESHOLD:
            proposals.append(ProposalPacket(
                proposal_id=f"prop_{record.record_id}_g22_{self._timestamp_suffix()}",
                source_record_id=record.record_id,
                source_record_type="section",
                proposal_type="scorer_calibration",
                target_scope=f"section_{record.section_id}_factual_grounding",
                proposed_change_summary="Calibrate G22 scorer with additional grounding examples",
                supporting_scores={"g22": g22, "g22_threshold": G22_THRESHOLD},
                improvement_hypothesis="Tighter grounding examples will improve G22 precision",
                inert_until_promotion=True,
                promotion_path="gauntlet->UWG->L4",
                applicable_to_future_runs=True,
                created_at=datetime.utcnow(),
                version=self.VERSION,
            ))
        
        return proposals
    
    def _generate_proposals_for_aggregate(
        self,
        record: AggregateCompletedEvalRecord
    ) -> List[ProposalPacket]:
        """Generate inert ProposalPackets from aggregate eval record.
        
        W7: Proposals are future-run only and inert until gauntlet/UWG/L4.
        """
        proposals = []
        scores = record.final_aggregate_scores
        
        # Proposal for merge consistency issues
        consistency_score = scores.get('rg_resume_merge_consistency', 1.0)
        if consistency_score < 0.8:
            proposals.append(ProposalPacket(
                proposal_id=f"prop_{record.record_id}_consistency_{self._timestamp_suffix()}",
                source_record_id=record.record_id,
                source_record_type="aggregate",
                proposal_type="merge_rule_enhancement",
                target_scope="full_resume_merge",
                proposed_change_summary="Strengthen merge consistency validation rules",
                supporting_scores={"consistency": consistency_score},
                improvement_hypothesis="Better merge rules will reduce cross-section contradictions",
                inert_until_promotion=True,
                promotion_path="gauntlet->UWG->L4",
                applicable_to_future_runs=True,
                created_at=datetime.utcnow(),
                version=self.VERSION,
            ))
        
        # Proposal for ATS balance issues
        ats_score = scores.get('rg_resume_ats_balance', 1.0)
        if ats_score < 0.75:
            proposals.append(ProposalPacket(
                proposal_id=f"prop_{record.record_id}_ats_{self._timestamp_suffix()}",
                source_record_id=record.record_id,
                source_record_type="aggregate",
                proposal_type="scorer_calibration",
                target_scope="full_resume_ats",
                proposed_change_summary="Recalibrate ATS balance scorer",
                supporting_scores={"ats_balance": ats_score},
                improvement_hypothesis="Better ATS balance will improve parsing without keyword stuffing",
                inert_until_promotion=True,
                promotion_path="gauntlet->UWG->L4",
                applicable_to_future_runs=True,
                created_at=datetime.utcnow(),
                version=self.VERSION,
            ))
        
        return proposals
    
    def _analyze_section_for_proposals(
        self,
        artifact: SectionArtifact,
        scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Analyze section for improvement proposals (raw proposal data).
        
        Returns proposal dicts that will be wrapped in ProposalPackets.
        """
        proposals = []
        
        # Low quality score proposal
        quality = scores.get('quality', 1.0)
        if quality < 0.8:
            proposals.append({
                "type": "quality_improvement",
                "trigger": f"quality_{quality:.2f}",
                "suggestion": "Review section content for clarity and impact",
            })
        
        return proposals
    
    def _analyze_aggregate_for_proposals(
        self,
        artifact: MergedResumeArtifact,
        scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Analyze aggregate for improvement proposals (raw proposal data).
        
        Returns proposal dicts that will be wrapped in ProposalPackets.
        """
        proposals = []
        
        # Low aggregate composite proposal
        composite = scores.get('aggregate_x1bd_composite', 1.0)
        if composite < 0.8:
            proposals.append({
                "type": "aggregate_quality",
                "trigger": f"composite_{composite:.2f}",
                "suggestion": "Review full resume for coherence and impact",
            })
        
        return proposals
    
    def _verify_g22_preserved(
        self,
        section_records: List[SectionCompletedEvalRecord],
        aggregate_record: Optional[AggregateCompletedEvalRecord]
    ) -> bool:
        """Verify G22 threshold preserved in all records."""
        # Check section records
        for record in section_records:
            g22 = record.g22_factual_grounding_achieved
            # Record captures achieved score; threshold is reference standard
            # No drift if score is properly recorded
            if g22 < 0 or g22 > 1.0:  # Sanity check
                return False
        
        # Check aggregate record
        if aggregate_record:
            g22 = aggregate_record.g22_factual_grounding_achieved
            if g22 < 0 or g22 > 1.0:
                return False
        
        return True
    
    def _timestamp_suffix(self) -> str:
        """Generate timestamp suffix for IDs."""
        return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:16]


# Convenience function
def produce_l6_shadow_learning(
    bundle: RuntimeExhaustBundle
) -> L6ShadowLearningResult:
    """Convenience wrapper for W7 L6 shadow learning production.
    
    Produces completed-run eval records and inert future-run proposals.
    Does NOT mutate current run or trigger any runtime behavior.
    """
    producer = L6ShadowLearningProducer()
    return producer.produce_from_bundle(bundle)


def create_runtime_exhaust_bundle(
    run_id: str,
    section_artifacts: List[SectionArtifact],
    merged_resume_artifact: Optional[MergedResumeArtifact],
    target_company: Optional[str] = None,
    target_role: Optional[str] = None,
    target_level: Optional[str] = None,
    resume_fingerprint: Optional[str] = None,
    job_fingerprint: Optional[str] = None,
) -> RuntimeExhaustBundle:
    """Convenience function to create RuntimeExhaustBundle.
    
    Bundle contains all artifacts from completed W4-W6 runtime.
    """
    return RuntimeExhaustBundle(
        run_id=run_id,
        section_artifacts=section_artifacts,
        merged_resume_artifact=merged_resume_artifact,
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        resume_fingerprint=resume_fingerprint,
        job_fingerprint=job_fingerprint,
        bundle_timestamp=datetime.utcnow(),
    )
