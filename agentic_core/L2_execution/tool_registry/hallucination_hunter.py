import datetime
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

try:
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

# Removed import from apps_shared.canon_validator_agentic_v2 as it is a downstream dependency
# and the components (get_fission_manager, get_safety_guardrail, get_subatomic_engine)
# were not used elsewhere in this class after initialization.

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

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
    hallucination_percentage: float
    risk_level: str  # "low", "medium", "high", "critical"
    unsupported_details: List[VerificationResult]
    requires_rollback: bool
    audit_trail: Dict[str, str]  # Maps output claims to source citations


class ClaimExtractor:
    """Handles extraction of atomic claims from text."""
    def __init__(self, genai_client, genai_available):
        self.genai_client = genai_client
        self.genai_available = genai_available

    async def extract_claims(self, text: str) -> List[AtomicClaim]:
        """
        Extract atomic claims (propositions) from text using Gemini or fallback.
        """
        if self.genai_available:
            try:
                return await self._extract_claims_with_gemini(text)
            except Exception as e:
                logger.warning(f"Gemini claim extraction failed: {e}, falling back to simple extraction")
        
        # Fallback to simple extraction
        return self._extract_claims_simple(text)

    async def _extract_claims_with_gemini(self, text: str) -> List[AtomicClaim]:
        """Use Gemini to extract atomic claims from text."""
        prompt = f"""Extract atomic claims from this text. Each claim should be a single, verifiable fact.

TEXT:
{text}

REQUIREMENTS:
1. Break the text into individual atomic claims (propositions)
2. Each claim should be independently verifiable
3. Focus on factual statements (skills, experience, achievements)
4. Ignore filler words and formatting
5. Number each claim

OUTPUT FORMAT:
Return a numbered list of atomic claims, one per line:
1. [First atomic claim]
2. [Second atomic claim]
...

Example for "John has 5 years of Python experience and led 3 projects":
1. John has 5 years of Python experience
2. John led 3 projects
"""
        
        response = self.genai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048
            )
        )
        
        # Parse response into claims
        claims = []
        lines = response.text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Match numbered claims: "1. Claim text" or "1) Claim text"
            match = re.match(r'^\d+[\.)]\s*(.+)$', line)
            if match:
                claim_text = match.group(1).strip()
                if len(claim_text) > 10:  # Filter very short claims
                    claims.append(AtomicClaim(
                        text=claim_text,
                        line_number=len(claims) + 1
                    ))
        
        return claims

    def _extract_claims_simple(self, text: str) -> List[AtomicClaim]:
        """Fallback simple claim extraction."""
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


class ClaimEmbedder:
    """Handles generating embeddings for claims."""
    def __init__(self):
        pass

    async def embed_claims(self, claims: List[AtomicClaim]) -> List[AtomicClaim]:
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


class ClaimVerifier:
    """Handles verifying claims against a source and calculating similarity."""
    def __init__(self, similarity_threshold: float):
        self.SIMILARITY_THRESHOLD = similarity_threshold

    def verify_claim(self, generated_claim: AtomicClaim,
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
        # Initialize shared Sub-Atomic Engine components.
        # The original imports from 'apps_shared' have been removed as they are
        # a downstream dependency and the attributes (self.engine, self.safety, self.fission)
        # were not utilized elsewhere in this class. They are initialized to None
        # to maintain the class's expected attribute structure.
        self.engine = None
        self.safety = None
        self.fission = None

        
        # Similarity threshold
        self.SIMILARITY_THRESHOLD = 0.85
        
        # Hallucination threshold (mission requirement: >5% fails)
        self.HALLUCINATION_THRESHOLD = 0.05  # 5%
        
        # Risk thresholds
        self.LOW_RISK_THRESHOLD = 0.95  # >95% supported
        self.MEDIUM_RISK_THRESHOLD = 0.85  # >85% supported
        self.HIGH_RISK_THRESHOLD = 0.70  # >70% supported
        # <70% is critical
        
        # Gemini client for claim extraction
        self.genai_available = GENAI_AVAILABLE
        genai_client = None
        if GENAI_AVAILABLE:
            api_key = self.ctx.get_env("GEMINI_API_KEY") if hasattr(self.ctx, 'get_env') else None
            if api_key:
                try:
                    genai_client = genai.Client(api_key=api_key)
                    logger.info("[OK] Hallucination Hunter connected to Gemini 2.5")
                except Exception as e:
                    logger.warning(f"[!]  Could not connect to Gemini: {e}")
                    self.genai_available = False
        
        # Initialize sub-components
        self._claim_extractor = ClaimExtractor(genai_client, self.genai_available)
        self._claim_embedder = ClaimEmbedder()
        self._claim_verifier = ClaimVerifier(self.SIMILARITY_THRESHOLD)
    
    async def execute(self):
        """
        Execute hallucination hunting.
        
        Listens for PIPELINE_OUTPUT signals and audits factual integrity.
        """
        logger.info("[SCAN] Hallucination Hunter: Monitoring for PIPELINE_OUTPUT signals...")
        
        # Listen for PIPELINE_OUTPUT signals from blackboard
        if hasattr(self.ctx, 'signals'):
            output_signals = [s for s in self.ctx.signals if s.startswith('PIPELINE_OUTPUT:')]
            
            if output_signals:
                logger.info(f"   Detected {len(output_signals)} PIPELINE_OUTPUT signals")
                
                for signal in output_signals:
                    # Extract file path from signal
                    file_path = signal.replace('PIPELINE_OUTPUT:', '')
                    await self._audit_pipeline_output(file_path)
            else:
                logger.info("   No PIPELINE_OUTPUT signals detected")
        
        # Fallback: Check for pipeline data in context
        elif hasattr(self.ctx, 'pipeline_data'):
            logger.info(f"   Processing pipeline data from context")
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
                    
                    # Block if hallucination threshold exceeded
                    if report.hallucination_percentage > self.HALLUCINATION_THRESHOLD:
                        self._emit_factual_integrity_fail(stage_name, report)
        else:
            logger.info("   No pipeline outputs to audit")
    
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
        source_claims = await self._claim_extractor.extract_claims(source_truth)
        generated_claims = await self._claim_extractor.extract_claims(generated_artifact)
        
        # Generate embeddings
        source_claims = await self._claim_embedder.embed_claims(source_claims)
        generated_claims = await self._claim_embedder.embed_claims(generated_claims)
        
        # Verify each generated claim
        verification_results = []
        for gen_claim in generated_claims:
            result = self._claim_verifier.verify_claim(gen_claim, source_claims)
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
        
        # Calculate hallucination percentage
        hallucination_percentage = (unsupported_claims / total_claims) if total_claims > 0 else 0.0
        
        # Build audit trail (maps claims to source citations)
        audit_trail = {}
        for result in verification_results:
            if result.is_supported and result.source_citation:
                audit_trail[result.claim.text] = result.source_citation
        
        return IntegrityReport(
            total_claims=total_claims,
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            integrity_score=integrity_score,
            hallucination_percentage=hallucination_percentage,
            risk_level=risk_level,
            unsupported_details=unsupported_details[:10],  # First 10
            requires_rollback=requires_rollback,
            audit_trail=audit_trail
        )
    
    def _display_report(self, stage_name: str, report: IntegrityReport):
        """Display integrity report."""
        logger.info(f"\n{'='*80}")
        logger.info(f"[SCAN] HALLUCINATION HUNTER REPORT - {stage_name}")
        logger.info(f"{'='*80}")
        logger.info(f"Total Claims: {report.total_claims}")
        logger.info(f"  Supported: {report.supported_claims}")
        logger.info(f"  Unsupported: {report.unsupported_claims}")
        logger.info(f"Integrity Score: {report.integrity_score:.1%}")
        logger.info(f"Hallucination Rate: {report.hallucination_percentage:.1%}")
        logger.info(f"Risk Level: {report.risk_level.upper()}")
        
        # Check hallucination threshold (5%)
        if report.hallucination_percentage > self.HALLUCINATION_THRESHOLD:
            logger.error(f"\n[ALERT] HALLUCINATION THRESHOLD EXCEEDED")
            logger.error(f"   Threshold: {self.HALLUCINATION_THRESHOLD:.1%}")
            logger.error(f"   Actual: {report.hallucination_percentage:.1%}")
            logger.error(f"   FACTUAL_INTEGRITY_FAIL signal will be emitted")
        
        if report.risk_level in ["high", "critical"]:
            logger.error(f"\n[!]  {report.risk_level.upper()} RISK DETECTED")
            logger.error(f"Rollback Required: {report.requires_rollback}")
        
        if report.unsupported_details:
            logger.warning(f"\n[!]  UNSUPPORTED CLAIMS (showing first 10):")
            for i, result in enumerate(report.unsupported_details, 1):
                logger.warning(f"  {i}. {result.claim.text[:80]}...")
                logger.warning(f"     Similarity: {result.similarity_score:.2f} (threshold: {self.SIMILARITY_THRESHOLD})")
                if result.source_citation:
                    logger.warning(f"     Best match: {result.source_citation}")
        
        # Display audit trail summary
        if report.audit_trail:
            logger.info(f"\n[OK] AUDIT TRAIL: {len(report.audit_trail)} claims mapped to sources")
        
        logger.info(f"{'='*80}\n")
    
    def _trigger_rollback(self, stage_name: str, report: IntegrityReport):
        """Trigger rollback to previous stage."""
        logger.error(f"[ALERT] TRIGGERING ROLLBACK for {stage_name}")
        logger.error(f"   Reason: Integrity score {report.integrity_score:.1%} below threshold")
        logger.error(f"   Action: Rolling back to previous stage with higher temperature")
        
        # Emit signal for orchestrator
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals.add(f"FACTUAL_RISK:{stage_name}:ROLLBACK_REQUIRED")
    
    def _emit_factual_integrity_fail(self, stage_name: str, report: IntegrityReport):
        """
        Emit FACTUAL_INTEGRITY_FAIL signal when hallucination threshold exceeded.
        
        Prevents resume from being sent to output folder.
        """
        logger.error(f"[ALERT] FACTUAL_INTEGRITY_FAIL for {stage_name}")
        logger.error(f"   Hallucination rate: {report.hallucination_percentage:.1%}")
        logger.error(f"   Threshold: {self.HALLUCINATION_THRESHOLD:.1%}")
        logger.error(f"   Unsupported claims: {report.unsupported_claims}/{report.total_claims}")
        logger.error(f"   Action: BLOCKING output to prevent hallucinated content")
        
        # Emit signal to blackboard
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals.add(f"FACTUAL_INTEGRITY_FAIL:{stage_name}")
            self.ctx.signals.add(f"HALLUCINATION_DETECTED:{stage_name}:{report.hallucination_percentage:.1%}")
    
    async def _audit_pipeline_output(self, file_path: str):
        """
        Audit a pipeline output file for factual integrity.
        
        Args:
            file_path: Path to pipeline output file
        """
        logger.info(f"   Auditing pipeline output: {file_path}")
        
        # Get source raw data from blackboard
        source_raw_data = None
        if hasattr(self.ctx, 'blackboard') and hasattr(self.ctx.blackboard, 'get'):
            source_raw_data = self.ctx.blackboard.get(f"source_raw_data:{file_path}")
        
        if not source_raw_data:
            logger.warning(f"   No source raw data found for {file_path}")
            return
        
        # Read generated output
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                generated_output = f.read()
        except Exception as e:
            logger.error(f"   Could not read output file: {e}")
            return
        
        # Audit integrity
        report = await self._audit_integrity(
            file_path,
            source_raw_data,
            generated_output
        )
        
        # Store report
        if not hasattr(self.ctx, 'integrity_reports'):
            self.ctx.integrity_reports = {}
        self.ctx.integrity_reports[file_path] = report
        
        # Display report
        self._display_report(file_path, report)
        
        # Inject audit trail metadata
        self._inject_audit_trail(file_path, report)
        
        # Block if hallucination threshold exceeded
        if report.hallucination_percentage > self.HALLUCINATION_THRESHOLD:
            self._emit_factual_integrity_fail(file_path, report)
    
    def _inject_audit_trail(self, file_path: str, report: IntegrityReport):
        """
        Inject audit trail metadata into output file or create sidecar file.
        
        Maps every claim in the resume to a specific line in the source document.
        """
        if not report.audit_trail:
            logger.warning(f"   No audit trail to inject for {file_path}")
            return
        
        # Create sidecar file with audit trail
        sidecar_path = file_path.replace('.txt', '_audit.json').replace('.md', '_audit.json')
        
        audit_data = {
            "file": file_path,
            "timestamp": datetime.datetime.now().isoformat(),
            "integrity_score": report.integrity_score,
            "hallucination_percentage": report.hallucination_percentage,
            "total_claims": report.total_claims,
            "supported_claims": report.supported_claims,
            "unsupported_claims": report.unsupported_claims,
            "audit_trail": report.audit_trail,
            "unsupported_claims_details": [
                {
                    "claim": r.claim.text,
                    "similarity_score": r.similarity_score,
                    "source_citation": r.source_citation
                }
                for r in report.unsupported_details
            ]
        }
        
        try:
            with open(sidecar_path, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2)
            
            logger.info(f"   [OK] Audit trail injected: {sidecar_path}")
            logger.info(f"      Mapped {len(report.audit_trail)} claims to source citations")
        except Exception as e:
            logger.error(f"   Could not inject audit trail: {e}")
    
    async def inject_citations(self, generated_text: str, source_text: str) -> str:
        """
        Inject citation metadata into generated text.
        
        Args:
            generated_text: Generated output
            source_text: Source truth
            
        Returns:
            Text with citation metadata
        """
        generated_claims = await self._claim_extractor.extract_claims(generated_text)
        source_claims = await self._claim_extractor.extract_claims(source_text)
        
        generated_claims = await self._claim_embedder.embed_claims(generated_claims)
        source_claims = await self._claim_embedder.embed_claims(source_claims)
        
        # Build cited text
        cited_lines = []
        for claim in generated_claims:
            result = self._claim_verifier.verify_claim(claim, source_claims)
            
            if result.is_supported and result.source_line:
                # Add citation
                cited_lines.append(f"{claim.text} [Source: Line {result.source_line}]")
            else:
                # Mark as unsupported
                cited_lines.append(f"{claim.text} [[!]  UNSUPPORTED]")
        
        return "\n".join(cited_lines)


# Singleton instance
_hallucination_hunter = None

def get_hallucination_hunter(ctx) -> HallucinationHunter:
    """Get or create global Hallucination Hunter instance."""
    global _hallucination_hunter
    if _hallucination_hunter is None:
        _hallucination_hunter = HallucinationHunter(ctx)
    return _hallucination_hunter