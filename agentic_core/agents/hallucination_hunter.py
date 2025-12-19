"""
⚛️ Hallucination Hunter - Ground Truth Verifier

Audits data integrity in HOP pipeline by comparing generated output against source truth.
Uses vector similarity to verify every claim can be traced to input data.

Mission: Trust data integrity, stop fixing resumes in production
Strategy: Atomic claim verification with citation mapping

Impact: Deployment speed increases through verified data integrity
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from agentic_core.agents.base import SubAtomicAgent

logger = logging.getLogger(__name__)


@dataclass
class AtomicClaim:
    """Represents an atomic claim (proposition) from text."""
    text: str
    line_number: int
    embedding: Optional[List[float]] = None


@dataclass
class VerificationResult:
    """Result of claim verification."""
    claim: AtomicClaim
    is_supported: bool
    similarity_score: float
    source_citation: Optional[str]
    source_line: Optional[int]


@dataclass
class IntegrityReport:
    """Data integrity audit report."""
    total_claims: int
    supported_claims: int
    unsupported_claims: int
    integrity_score: float
    risk_level: str  # "low", "medium", "high", "critical"
    unsupported_details: List[VerificationResult]
    requires_rollback: bool


class HallucinationHunter(SubAtomicAgent):
    """
    The Hallucination Hunter - Ground Truth Verifier
    
    Runs in HOP inference stages (Phase 2 & 3).
    Compares generated output against source truth.
    Flags unsupported claims as FACTUAL_RISK.
    
    Process:
    1. Break source and generated text into atomic claims
    2. For each generated claim, search source via vector similarity
    3. If similarity < 0.85, flag as unsupported
    4. Inject citation metadata for supported claims
    5. Block deployment if integrity score too low
    """
    
    def __init__(self, ctx):
        """
        Initialize Hallucination Hunter.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        
        # Similarity threshold
        self.SIMILARITY_THRESHOLD = 0.85
        
        # Risk thresholds
        self.LOW_RISK_THRESHOLD = 0.95  # >95% supported
        self.MEDIUM_RISK_THRESHOLD = 0.85  # >85% supported
        self.HIGH_RISK_THRESHOLD = 0.70  # >70% supported
        # <70% is critical
    
    async def execute(self):
        """
        Execute hallucination hunting.
        
        Audits data integrity of pipeline outputs.
        """
        logger.info("🔍 Hallucination Hunter: Auditing data integrity...")
        
        # Check if we have source and generated data
        if not hasattr(self.ctx, 'pipeline_data'):
            logger.info("   No pipeline data to audit")
            return
        
        # Audit each stage
        for stage_name, stage_data in self.ctx.pipeline_data.items():
            if 'source_truth' in stage_data and 'generated_artifact' in stage_data:
                report = await self._audit_integrity(
                    stage_name,
                    stage_data['source_truth'],
                    stage_data['generated_artifact']
                )
                
                # Store report
                if not hasattr(self.ctx, 'integrity_reports'):
                    self.ctx.integrity_reports = {}
                self.ctx.integrity_reports[stage_name] = report
                
                # Display report
                self._display_report(stage_name, report)
                
                # Block if critical
                if report.requires_rollback:
                    self._trigger_rollback(stage_name, report)
    
    async def _audit_integrity(self, stage_name: str, source_truth: str,
                               generated_artifact: str) -> IntegrityReport:
        """
        Audit integrity of generated artifact against source truth.
        
        Args:
            stage_name: Name of pipeline stage
            source_truth: Ground truth source data
            generated_artifact: Generated output
            
        Returns:
            Integrity report
        """
        # Extract atomic claims from both
        source_claims = self._extract_claims(source_truth)
        generated_claims = self._extract_claims(generated_artifact)
        
        # Generate embeddings
        source_claims = await self._embed_claims(source_claims)
        generated_claims = await self._embed_claims(generated_claims)
        
        # Verify each generated claim
        verification_results = []
        for gen_claim in generated_claims:
            result = self._verify_claim(gen_claim, source_claims)
            verification_results.append(result)
        
        # Calculate metrics
        total_claims = len(generated_claims)
        supported_claims = sum(1 for r in verification_results if r.is_supported)
        unsupported_claims = total_claims - supported_claims
        
        integrity_score = (supported_claims / total_claims) if total_claims > 0 else 1.0
        
        # Determine risk level
        if integrity_score >= self.LOW_RISK_THRESHOLD:
            risk_level = "low"
        elif integrity_score >= self.MEDIUM_RISK_THRESHOLD:
            risk_level = "medium"
        elif integrity_score >= self.HIGH_RISK_THRESHOLD:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Determine if rollback required
        requires_rollback = risk_level in ["high", "critical"]
        
        # Get unsupported details
        unsupported_details = [r for r in verification_results if not r.is_supported]
        
        return IntegrityReport(
            total_claims=total_claims,
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            integrity_score=integrity_score,
            risk_level=risk_level,
            unsupported_details=unsupported_details[:10],  # First 10
            requires_rollback=requires_rollback
        )
    
    def _extract_claims(self, text: str) -> List[AtomicClaim]:
        """
        Extract atomic claims (propositions) from text.
        
        Simple implementation: Split by sentences and filter.
        Production would use more sophisticated NLP.
        """
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence in enumerate(sentences, 1):
            sentence = sentence.strip()
            
            # Filter out very short sentences
            if len(sentence) < 10:
                continue
            
            # Filter out questions
            if '?' in sentence:
                continue
            
            claims.append(AtomicClaim(
                text=sentence,
                line_number=i
            ))
        
        return claims
    
    async def _embed_claims(self, claims: List[AtomicClaim]) -> List[AtomicClaim]:
        """Generate embeddings for claims."""
        # In production, would use actual embedding model
        # For now, use simple word-based similarity
        
        for claim in claims:
            # Placeholder: In production, use OpenAI/Gemini embeddings
            claim.embedding = self._simple_embedding(claim.text)
        
        return claims
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple word-based embedding (placeholder)."""
        # Convert text to simple vector based on word presence
        # In production, use actual embedding model
        words = text.lower().split()
        return [float(len(words))]  # Placeholder
    
    def _verify_claim(self, generated_claim: AtomicClaim,
                     source_claims: List[AtomicClaim]) -> VerificationResult:
        """
        Verify a generated claim against source claims.
        
        Args:
            generated_claim: Claim from generated output
            source_claims: Claims from source truth
            
        Returns:
            Verification result
        """
        # Find most similar source claim
        max_similarity = 0.0
        best_match = None
        best_match_line = None
        
        for source_claim in source_claims:
            similarity = self._calculate_similarity(
                generated_claim.text,
                source_claim.text
            )
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = source_claim.text
                best_match_line = source_claim.line_number
        
        # Check if supported
        is_supported = max_similarity >= self.SIMILARITY_THRESHOLD
        
        # Generate citation
        source_citation = f"Line {best_match_line}: {best_match[:50]}..." if best_match else None
        
        return VerificationResult(
            claim=generated_claim,
            is_supported=is_supported,
            similarity_score=max_similarity,
            source_citation=source_citation,
            source_line=best_match_line
        )
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Simple implementation using word overlap.
        Production would use cosine similarity of embeddings.
        """
        # Normalize texts
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _display_report(self, stage_name: str, report: IntegrityReport):
        """Display integrity report."""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 HALLUCINATION HUNTER REPORT - {stage_name}")
        logger.info(f"{'='*80}")
        logger.info(f"Total Claims: {report.total_claims}")
        logger.info(f"  Supported: {report.supported_claims}")
        logger.info(f"  Unsupported: {report.unsupported_claims}")
        logger.info(f"Integrity Score: {report.integrity_score:.1%}")
        logger.info(f"Risk Level: {report.risk_level.upper()}")
        
        if report.risk_level in ["high", "critical"]:
            logger.error(f"\n⚠️  {report.risk_level.upper()} RISK DETECTED")
            logger.error(f"Rollback Required: {report.requires_rollback}")
        
        if report.unsupported_details:
            logger.warning(f"\n⚠️  UNSUPPORTED CLAIMS (showing first 10):")
            for i, result in enumerate(report.unsupported_details, 1):
                logger.warning(f"  {i}. {result.claim.text[:80]}...")
                logger.warning(f"     Similarity: {result.similarity_score:.2f} (threshold: {self.SIMILARITY_THRESHOLD})")
                if result.source_citation:
                    logger.warning(f"     Best match: {result.source_citation}")
        
        logger.info(f"{'='*80}\n")
    
    def _trigger_rollback(self, stage_name: str, report: IntegrityReport):
        """Trigger rollback to previous stage."""
        logger.error(f"🚨 TRIGGERING ROLLBACK for {stage_name}")
        logger.error(f"   Reason: Integrity score {report.integrity_score:.1%} below threshold")
        logger.error(f"   Action: Rolling back to previous stage with higher temperature")
        
        # Emit signal for orchestrator
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals.add(f"FACTUAL_RISK:{stage_name}:ROLLBACK_REQUIRED")
    
    def inject_citations(self, generated_text: str, source_text: str) -> str:
        """
        Inject citation metadata into generated text.
        
        Args:
            generated_text: Generated output
            source_text: Source truth
            
        Returns:
            Text with citation metadata
        """
        # Extract claims
        generated_claims = self._extract_claims(generated_text)
        source_claims = self._extract_claims(source_text)
        
        # Add embeddings
        import asyncio
        generated_claims = asyncio.run(self._embed_claims(generated_claims))
        source_claims = asyncio.run(self._embed_claims(source_claims))
        
        # Build cited text
        cited_lines = []
        for claim in generated_claims:
            result = self._verify_claim(claim, source_claims)
            
            if result.is_supported and result.source_line:
                # Add citation
                cited_lines.append(f"{claim.text} [Source: Line {result.source_line}]")
            else:
                # Mark as unsupported
                cited_lines.append(f"{claim.text} [⚠️  UNSUPPORTED]")
        
        return "\n".join(cited_lines)


# Singleton instance
_hallucination_hunter = None

def get_hallucination_hunter(ctx) -> HallucinationHunter:
    """Get or create global Hallucination Hunter instance."""
    global _hallucination_hunter
    if _hallucination_hunter is None:
        _hallucination_hunter = HallucinationHunter(ctx)
    return _hallucination_hunter
