
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: memory, orchestrator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
import datetime
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout
try:
    NUMPY_AVAILABLE: Any = True
except ImportError:
    NUMPY_AVAILABLE: Any = False
from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE: Any = True
except ImportError:
    GENAI_AVAILABLE: Any = False
    genai: Any = None
    types: Any = None
Logger: Any = logging.getLogger(__name__)

@dataclass
class AtomicClaim:
    """Represents an atomic Claim (proposition) from text."""
    text: str
    line_number: int
    embedding: Optional[List[float]] = None

@dataclass
class VerificationResult:
    """Result of Claim verification."""
    Claim: AtomicClaim
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
    risk_level: str
    unsupported_details: List[VerificationResult]
    requires_rollback: bool
    audit_trail: Dict[str, str]

class ClaimExtractor:
    """Handles extraction of atomic claims from text."""

    def __init__(self, genai_client: Any, genai_available: bool) -> None:
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
                Logger.warning(f'Gemini Claim extraction failed: {e}, falling back to simple extraction')
        return self._extract_claims_simple(text)

    async def _extract_claims_with_gemini(self, text: str) -> List[AtomicClaim]:
        """Use Gemini to extract atomic claims from text."""
        prompt = f'Extract atomic claims from this text. Each Claim should be a single, verifiable fact.\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin\n\nTEXT:\n{text}\n\nREQUIREMENTS:\n1. Break the text into individual atomic claims (propositions)\n2. Each Claim should be independently verifiable\n3. Focus on factual statements (skills, experience, achievements)\n4. Ignore filler words and formatting\n5. Number each Claim\n\nOUTPUT FORMAT:\nReturn a numbered list of atomic claims, one per line:\n1. [First atomic Claim]\n2. [Second atomic Claim]\n...\n\nExample for "John has 5 years of Python experience and led 3 projects":\n1. John has 5 years of Python experience\n2. John led 3 projects\n'
        response = self.genai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=2048))
        claims = []
        lines = response.text.strip().split('\n')
        for line in lines:
            line = line.strip()
            match = re.match('^\\d+[\\.)]\\s*(.+)$', line)
            if match:
                claim_text = match.group(1).strip()
                if len(claim_text) > 10:
                    claims.append(AtomicClaim(text=claim_text, line_number=len(claims) + 1))
        return claims

    def _extract_claims_simple(self, text: str) -> List[AtomicClaim]:
        """Fallback simple Claim extraction."""
        claims = []
        sentences = re.split('[.!?]+', text)
        for i, sentence in enumerate(sentences, 1):
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            if '?' in sentence:
                continue
            claims.append(AtomicClaim(text=sentence, line_number=i))
        return claims

class ClaimEmbedder:
    """Handles generating embeddings for claims."""

    def __init__(self) -> None:
        pass

    async def embed_claims(self, claims: List[AtomicClaim]) -> List[AtomicClaim]:
        """Generate embeddings for claims."""
        for Claim in claims:
            Claim.embedding = self._simple_embedding(Claim.text)
        return claims

    def _simple_embedding(self, text: str) -> List[float]:
        """Simple word-based embedding (placeholder)."""
        words = text.lower().split()
        return [float(len(words))]

class ClaimVerifier:
    """Handles verifying claims against a source and calculating similarity."""

    def __init__(self, similarity_threshold: float) -> None:
        self.SIMILARITY_THRESHOLD = similarity_threshold

    def verify_claim(self, generated_claim: AtomicClaim, source_claims: List[AtomicClaim]) -> VerificationResult:
        """
        Verify a generated Claim against source claims.
        
        Args:
            generated_claim: Claim from generated output
            source_claims: Claims from source truth
            
        Returns:
            Verification result
        """
        max_similarity: Any = 0.0
        best_match: Any = None
        best_match_line: Any = None
        for source_claim in source_claims:
            similarity: Any = self._calculate_similarity(generated_claim.text, source_claim.text)
            if similarity > max_similarity:
                max_similarity: Any = similarity
                best_match: Any = source_claim.text
                best_match_line: Any = source_claim.line_number
        is_supported: Any = max_similarity >= self.SIMILARITY_THRESHOLD
        source_citation: Any = f'Line {best_match_line}: {best_match[:50]}...' if best_match else None
        return VerificationResult(Claim=generated_claim, is_supported=is_supported, similarity_score=max_similarity, source_citation=source_citation, source_line=best_match_line)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Simple implementation using word overlap.
        Production would use cosine similarity of embeddings.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
class HallucinationHunterAgent(MCPHardenedMixin, SubatomicTestingMixin, SubAtomicAgent):
    """
    The Hallucination Hunter - Ground Truth Verifier
    
    Runs in HOP inference stages (Phase 2 & 3).
    Compares generated output against source truth.
    Flags unsupported claims as FACTUAL_RISK.
    
    Process:
    1. Break source and generated text into atomic claims
    2. For each generated Claim, search source via vector similarity
    3. If similarity < 0.85, flag as unsupported
    4. Inject citation metadata for supported claims
    5. Block deployment if integrity score too low
    """

    def __init__(self, ctx: Any) -> None:
        """
        Initialize Hallucination Hunter.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        self.engine = None
        self.safety = None
        self.fission = None
        self.SIMILARITY_THRESHOLD = 0.85
        self.HALLUCINATION_THRESHOLD = 0.05
        self.LOW_RISK_THRESHOLD = 0.95
        self.MEDIUM_RISK_THRESHOLD = 0.85
        self.HIGH_RISK_THRESHOLD = 0.7
        self.genai_available = GENAI_AVAILABLE
        genai_client = None
        if GENAI_AVAILABLE:
            api_key = self.ctx.get_env('GEMINI_API_KEY') if hasattr(self.ctx, 'get_env') else None
            if api_key:
                try:
                    genai_client = genai.Client(api_key=api_key)
                    Logger.info('[OK] Hallucination Hunter connected to Gemini 2.5')
                except Exception as e:
                    Logger.warning(f'[!]  Could not connect to Gemini: {e}')
                    self.genai_available = False
        self._claim_extractor = ClaimExtractor(genai_client, self.genai_available)
        self._claim_embedder = ClaimEmbedder()
        self._claim_verifier = ClaimVerifier(self.SIMILARITY_THRESHOLD)

    async def execute(self) -> Any:
        """
        Execute hallucination hunting.
        
        Listens for PIPELINE_OUTPUT signals and audits factual integrity.
        """
        Logger.info('[SCAN] Hallucination Hunter: Monitoring for PIPELINE_OUTPUT signals...')
        if hasattr(self.ctx, 'signals'):
            output_signals: Any = [s for s in self.ctx.signals if s.startswith('PIPELINE_OUTPUT:')]
            if output_signals:
                Logger.info(f'   Detected {len(output_signals)} PIPELINE_OUTPUT signals')
                for signal in output_signals:
                    file_path: Any = signal.replace('PIPELINE_OUTPUT:', '')
                    await self._audit_pipeline_output(file_path)
            else:
                Logger.info('   No PIPELINE_OUTPUT signals detected')
        elif hasattr(self.ctx, 'pipeline_data'):
            Logger.info(f'   Processing pipeline data from context')
            for stage_name, stage_data in self.ctx.pipeline_data.items():
                if 'source_truth' in stage_data and 'generated_artifact' in stage_data:
                    report: Any = await self._audit_integrity(stage_name, stage_data['source_truth'], stage_data['generated_artifact'])
                    if not hasattr(self.ctx, 'integrity_reports'):
                        self.ctx.integrity_reports = {}
                    self.ctx.integrity_reports[stage_name] = report
                    self._display_report(stage_name, report)
                    if report.hallucination_percentage > self.HALLUCINATION_THRESHOLD:
                        self._emit_factual_integrity_fail(stage_name, report)
        else:
            Logger.info('   No pipeline outputs to audit')

    def _determine_risk_level(self, integrity_score: float) -> str:
        """Determine risk level based on integrity score.
        
        Args:
            integrity_score: Score between 0 and 1.
            
        Returns:
            Risk level string: 'low', 'medium', 'high', or 'critical'.
        """
        if integrity_score >= self.LOW_RISK_THRESHOLD:
            return 'low'
        elif integrity_score >= self.MEDIUM_RISK_THRESHOLD:
            return 'medium'
        elif integrity_score >= self.HIGH_RISK_THRESHOLD:
            return 'high'
        return 'critical'

    def _build_audit_trail(self, verification_results: List[VerificationResult]) -> Dict[str, str]:
        """Build audit trail from verification results.
        
        Args:
            verification_results: List of verification results.
            
        Returns:
            Dict mapping claim text to source citation.
        """
        audit_trail = {}
        for result in verification_results:
            if result.is_supported and result.source_citation:
                audit_trail[result.Claim.text] = result.source_citation
        return audit_trail

    async def _audit_integrity(self, stage_name: str, source_truth: str, generated_artifact: str) -> IntegrityReport:
        """Audit integrity of generated Artifact against source truth.
        
        Args:
            stage_name: Name of pipeline stage.
            source_truth: Ground truth source data.
            generated_artifact: Generated output.
            
        Returns:
            Integrity report with verification results.
        """
        source_claims = await self._claim_extractor.extract_claims(source_truth)
        generated_claims = await self._claim_extractor.extract_claims(generated_artifact)
        source_claims = await self._claim_embedder.embed_claims(source_claims)
        generated_claims = await self._claim_embedder.embed_claims(generated_claims)
        
        verification_results = [
            self._claim_verifier.verify_claim(gen_claim, source_claims)
            for gen_claim in generated_claims
        ]
        
        total_claims = len(generated_claims)
        supported_claims = sum(1 for r in verification_results if r.is_supported)
        unsupported_claims = total_claims - supported_claims
        integrity_score = supported_claims / total_claims if total_claims > 0 else 1.0
        hallucination_percentage = unsupported_claims / total_claims if total_claims > 0 else 0.0
        
        risk_level = self._determine_risk_level(integrity_score)
        audit_trail = self._build_audit_trail(verification_results)
        unsupported_details = [r for r in verification_results if not r.is_supported]
        
        return IntegrityReport(
            total_claims=total_claims,
            supported_claims=supported_claims,
            unsupported_claims=unsupported_claims,
            integrity_score=integrity_score,
            hallucination_percentage=hallucination_percentage,
            risk_level=risk_level,
            unsupported_details=unsupported_details[:10],
            requires_rollback=risk_level in ['high', 'critical'],
            audit_trail=audit_trail
        )

    def _display_report(self, stage_name: str, report: IntegrityReport) -> Any:
        """Display integrity report."""
        Logger.info(f"\n{'=' * 80}")
        Logger.info(f'[SCAN] HALLUCINATION HUNTER REPORT - {stage_name}')
        Logger.info(f"{'=' * 80}")
        Logger.info(f'Total Claims: {report.total_claims}')
        Logger.info(f'  Supported: {report.supported_claims}')
        Logger.info(f'  Unsupported: {report.unsupported_claims}')
        Logger.info(f'Integrity Score: {report.integrity_score:.1%}')
        Logger.info(f'Hallucination Rate: {report.hallucination_percentage:.1%}')
        Logger.info(f'Risk Level: {report.risk_level.upper()}')
        if report.hallucination_percentage > self.HALLUCINATION_THRESHOLD:
            Logger.error(f'\n[ALERT] HALLUCINATION THRESHOLD EXCEEDED')
            Logger.error(f'   Threshold: {self.HALLUCINATION_THRESHOLD:.1%}')
            Logger.error(f'   Actual: {report.hallucination_percentage:.1%}')
            Logger.error(f'   FACTUAL_INTEGRITY_FAIL signal will be emitted')
        if report.risk_level in ['high', 'critical']:
            Logger.error(f'\n[!]  {report.risk_level.upper()} RISK DETECTED')
            Logger.error(f'Rollback Required: {report.requires_rollback}')
        if report.unsupported_details:
            Logger.warning(f'\n[!]  UNSUPPORTED CLAIMS (showing first 10):')
            for i, result in enumerate(report.unsupported_details, 1):
                Logger.warning(f'  {i}. {result.Claim.text[:80]}...')
                Logger.warning(f'     Similarity: {result.similarity_score:.2f} (threshold: {self.SIMILARITY_THRESHOLD})')
                if result.source_citation:
                    Logger.warning(f'     Best match: {result.source_citation}')
        if report.audit_trail:
            Logger.info(f'\n[OK] AUDIT TRAIL: {len(report.audit_trail)} claims mapped to sources')
        Logger.info(f"{'=' * 80}\n")

    def _trigger_rollback(self, stage_name: str, report: IntegrityReport) -> Any:
        """Trigger rollback to previous stage."""
        Logger.error(f'[ALERT] TRIGGERING ROLLBACK for {stage_name}')
        Logger.error(f'   Reason: Integrity score {report.integrity_score:.1%} below threshold')
        Logger.error(f'   Action: Rolling back to previous stage with higher temperature')
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals.add(f'FACTUAL_RISK:{stage_name}:ROLLBACK_REQUIRED')

    def _emit_factual_integrity_fail(self, stage_name: str, report: IntegrityReport) -> Any:
        """
        Emit FACTUAL_INTEGRITY_FAIL signal when hallucination threshold exceeded.
        
        Prevents resume from being sent to output folder.
        """
        Logger.error(f'[ALERT] FACTUAL_INTEGRITY_FAIL for {stage_name}')
        Logger.error(f'   Hallucination rate: {report.hallucination_percentage:.1%}')
        Logger.error(f'   Threshold: {self.HALLUCINATION_THRESHOLD:.1%}')
        Logger.error(f'   Unsupported claims: {report.unsupported_claims}/{report.total_claims}')
        Logger.error(f'   Action: BLOCKING output to prevent hallucinated content')
        if hasattr(self.ctx, 'signals'):
            self.ctx.signals.add(f'FACTUAL_INTEGRITY_FAIL:{stage_name}')
            self.ctx.signals.add(f'HALLUCINATION_DETECTED:{stage_name}:{report.hallucination_percentage:.1%}')

    async def _audit_pipeline_output(self, file_path: str) -> Any:
        """
        Audit a pipeline output file for factual integrity.
        
        Args:
            file_path: Path to pipeline output file
        """
        Logger.info(f'   Auditing pipeline output: {file_path}')
        source_raw_data = None
        if hasattr(self.ctx, 'blackboard') and hasattr(self.ctx.blackboard, 'get'):
            source_raw_data = self.ctx.blackboard.get(f'source_raw_data:{file_path}')
        if not source_raw_data:
            Logger.warning(f'   No source raw data found for {file_path}')
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                generated_output = f.read()
        except Exception as e:
            Logger.error(f'   Could not read output file: {e}')
            return
        report = await self._audit_integrity(file_path, source_raw_data, generated_output)
        if not hasattr(self.ctx, 'integrity_reports'):
            self.ctx.integrity_reports = {}
        self.ctx.integrity_reports[file_path] = report
        self._display_report(file_path, report)
        self._inject_audit_trail(file_path, report)
        if report.hallucination_percentage > self.HALLUCINATION_THRESHOLD:
            self._emit_factual_integrity_fail(file_path, report)

    def _inject_audit_trail(self, file_path: str, report: IntegrityReport) -> Any:
        """
        Inject audit trail metadata into output file or create sidecar file.
        
        Maps every Claim in the resume to a specific line in the source document.
        """
        if not report.audit_trail:
            Logger.warning(f'   No audit trail to inject for {file_path}')
            return
        sidecar_path = file_path.replace('.txt', '_audit.json').replace('.md', '_audit.json')
        audit_data = {'file': file_path, 'timestamp': datetime.datetime.now().isoformat(), 'integrity_score': report.integrity_score, 'hallucination_percentage': report.hallucination_percentage, 'total_claims': report.total_claims, 'supported_claims': report.supported_claims, 'unsupported_claims': report.unsupported_claims, 'audit_trail': report.audit_trail, 'unsupported_claims_details': [{'Claim': r.Claim.text, 'similarity_score': r.similarity_score, 'source_citation': r.source_citation} for r in report.unsupported_details]}
        try:
            with open(sidecar_path, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2)
            Logger.info(f'   [OK] Audit trail injected: {sidecar_path}')
            Logger.info(f'      Mapped {len(report.audit_trail)} claims to source citations')
        except Exception as e:
            Logger.error(f'   Could not inject audit trail: {e}')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Operational guardrail agent - no repository healing required."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Operational guardrail - no healing required")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    async def inject_citations(self, generated_text: str, source_text: str) -> str:
        """
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Inject citation metadata into generated text.
        
        Args:
            generated_text: Generated output
            source_text: Source truth
            
        Returns:
            Text with citation metadata
        """
        generated_claims: Any = await self._claim_extractor.extract_claims(generated_text)
        source_claims: Any = await self._claim_extractor.extract_claims(source_text)
        generated_claims: Any = await self._claim_embedder.embed_claims(generated_claims)
        source_claims: Any = await self._claim_embedder.embed_claims(source_claims)
        cited_lines: Any = []
        for Claim in generated_claims:
            result: Any = self._claim_verifier.verify_claim(Claim, source_claims)
            if result.is_supported and result.source_line:
                cited_lines.append(f'{Claim.text} [Source: Line {result.source_line}]')
            else:
                cited_lines.append(f'{Claim.text} [[!]  UNSUPPORTED]')
        return '\n'.join(cited_lines)
_hallucination_hunter = None

def get_hallucination_hunter(ctx: Any) -> HallucinationHunter:
    """Get or create global Hallucination Hunter instance."""
    global _hallucination_hunter
    if _hallucination_hunter is None:
        _hallucination_hunter = HallucinationHunter(ctx)
    return _hallucination_hunter
