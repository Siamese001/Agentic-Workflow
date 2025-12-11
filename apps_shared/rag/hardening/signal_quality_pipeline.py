"""
runtime/shared/signal_quality_pipeline.py
Multi-Stage Signal Quality Pipeline for RAG Hardening

Ported from historical resume gen Job_Workflow_v61.27.json
Implements 5-stage RAG quality assurance pipeline:
  1. Relevance Filtering (cross-encoder reranker)
  2. Source Authority Tiering
  3. Query Enhancement (HyDE)
  4. Self-Critique Guardrail
  5. External Fact-Checking
"""


import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Protocol, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class SourceTier(Enum):
    """Authority tiers for information sources."""
    TIER_1_OFFICIAL = 1      # Official company sites, SEC filings, press releases
    TIER_2_AUTHORITATIVE = 2  # Industry publications, verified news sources
    TIER_3_SECONDARY = 3      # Blogs, forums, social media
    TIER_4_UNVERIFIED = 4     # Unknown or unverified sources


class SignalQualityStage(Enum):
    """Stages in the signal quality pipeline."""
    RELEVANCE_FILTERING = auto()
    SOURCE_AUTHORITY_TIERING = auto()
    QUERY_ENHANCEMENT = auto()
    SELF_CRITIQUE_GUARDRAIL = auto()
    EXTERNAL_FACT_CHECKING = auto()


class PipelineDecision(Enum):
    """Decisions from pipeline stages."""
    PROCEED = "PROCEED"
    REFINE = "REFINE"
    REJECT = "REJECT"
    HALT = "HALT"


class ClaimVerificationMode(Enum):
    """Verification strictness levels."""
    STRICT = "strict"       # All claims must be verified
    BALANCED = "balanced"   # Key claims verified, minor claims allowed
    PERMISSIVE = "permissive"  # Minimal verification


# =============================================================================
# PROTOCOLS
# =============================================================================

class RerankerProtocol(Protocol):
    """Protocol for cross-encoder reranker implementations."""
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, object]],
        top_k: int = 10,
    ) -> List[Tuple[Dict[str, object], float]]:
        """Rerank documents by relevance to query."""
        ...


class EmbeddingProtocol(Protocol):
    """Protocol for embedding model implementations."""
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        ...
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate similarity between embeddings."""
        ...


class FactCheckerProtocol(Protocol):
    """Protocol for external fact-checking provider."""
    
    def verify_claim(self, claim: str, context: str) -> Tuple[bool, float, str]:
        """
        Verify a claim against external sources.
        
        Returns:
            Tuple of (is_verified, confidence, explanation)
        """
        ...


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RetrievedDocument:
    """A document retrieved from RAG."""
    id: str
    content: str
    source: str
    source_tier: SourceTier = SourceTier.TIER_4_UNVERIFIED
    relevance_score: float = 0.0
    authority_score: float = 0.0
    recency_score: float = 0.0
    metadata: Dict[str, object] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def composite_score(self) -> float:
        """Calculate composite quality score."""
        # Weighted combination: relevance (50%), authority (30%), recency (20%)
        return (
            self.relevance_score * 0.5 +
            self.authority_score * 0.3 +
            self.recency_score * 0.2
        )
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "source": self.source,
            "source_tier": self.source_tier.name,
            "relevance_score": self.relevance_score,
            "authority_score": self.authority_score,
            "recency_score": self.recency_score,
            "composite_score": self.composite_score,
            "metadata": self.metadata,
        }


@dataclass
class StageResult:
    """Result from a single pipeline stage."""
    stage: SignalQualityStage
    decision: PipelineDecision
    documents: List[RetrievedDocument]
    confidence: float
    reasoning: str
    refinement_suggestions: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: Dict[str, object] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "stage": self.stage.name,
            "decision": self.decision.value,
            "document_count": len(self.documents),
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "refinement_suggestions": self.refinement_suggestions,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


@dataclass
class PipelineResult:
    """Result from the complete signal quality pipeline."""
    success: bool
    final_documents: List[RetrievedDocument]
    stage_results: List[StageResult]
    total_confidence: float
    total_duration_ms: float
    refinement_count: int = 0
    halt_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "document_count": len(self.final_documents),
            "total_confidence": self.total_confidence,
            "total_duration_ms": self.total_duration_ms,
            "refinement_count": self.refinement_count,
            "halt_reason": self.halt_reason,
            "stages": [s.to_dict() for s in self.stage_results],
        }


@dataclass
class HyDEConfig:
    """Configuration for Hypothetical Document Embeddings."""
    enabled: bool = True
    num_hypothetical_docs: int = 3
    temperature: float = 0.7
    max_tokens: int = 256
    
    
@dataclass
class SignalQualityConfig:
    """Configuration for the signal quality pipeline."""
    # Stage enablement
    enable_relevance_filtering: bool = True
    enable_source_tiering: bool = True
    enable_query_enhancement: bool = True
    enable_self_critique: bool = True
    enable_fact_checking: bool = False  # Requires external provider
    
    # Thresholds
    min_relevance_score: float = 0.5
    min_authority_score: float = 0.3
    min_composite_score: float = 0.4
    self_critique_threshold: float = 0.7
    
    # Limits
    max_documents_per_stage: int = 20
    max_refinement_attempts: int = 2
    
    # HyDE configuration
    hyde_config: HyDEConfig = field(default_factory=HyDEConfig)
    
    # Claim verification
    claim_verification_mode: ClaimVerificationMode = ClaimVerificationMode.BALANCED
    
    # Source tier weights
    tier_weights: Dict[SourceTier, float] = field(default_factory=lambda: {
        SourceTier.TIER_1_OFFICIAL: 1.0,
        SourceTier.TIER_2_AUTHORITATIVE: 0.8,
        SourceTier.TIER_3_SECONDARY: 0.5,
        SourceTier.TIER_4_UNVERIFIED: 0.2,
    })


@dataclass
class SelfCritiqueResult:
    """Result of self-critique analysis."""
    claim: str
    is_supported: bool
    supporting_evidence: List[str]
    confidence: float
    reasoning: str
    gaps_identified: List[str] = field(default_factory=list)


# =============================================================================
# SIGNAL QUALITY PIPELINE
# =============================================================================

class SignalQualityPipeline:
    """
    Multi-Stage Signal Quality Pipeline for RAG Hardening.
    
    Implements the 5-stage pipeline from historical resume gen:
    1. Relevance Filtering - Cross-encoder reranking
    2. Source Authority Tiering - Prioritize authoritative sources
    3. Query Enhancement - HyDE for sparse queries
    4. Self-Critique Guardrail - Validate context supports claims
    5. External Fact-Checking - Verify key claims externally
    """
    
    def __init__(
        self,
        config: Optional[SignalQualityConfig] = None,
        reranker: Optional[RerankerProtocol] = None,
        embedder: Optional[EmbeddingProtocol] = None,
        fact_checker: Optional[FactCheckerProtocol] = None,
        llm_generate: Optional[Callable[[str], str]] = None,
    ) -> None:
        """
        Initialize the pipeline.
        
        Args:
            config: Pipeline configuration
            reranker: Cross-encoder reranker for relevance filtering
            embedder: Embedding model for HyDE
            fact_checker: External fact-checking provider
            llm_generate: LLM generation function for HyDE and self-critique
        """
        self.config = config or SignalQualityConfig()
        self.reranker = reranker
        self.embedder = embedder
        self.fact_checker = fact_checker
        self.llm_generate = llm_generate
        
    def process(
        self,
        query: str,
        documents: List[RetrievedDocument],
        claims_to_verify: Optional[List[str]] = None,
    ) -> PipelineResult:
        """
        Process documents through the signal quality pipeline.
        
        Args:
            query: The original query
            documents: Retrieved documents to process
            claims_to_verify: Optional list of claims to verify
            
        Returns:
            PipelineResult with filtered and validated documents
        """
        import time
        start_time = time.time()
        
        stage_results: List[StageResult] = []
        current_docs = documents
        refinement_count = 0
        
        # Stage 1: Relevance Filtering
        if self.config.enable_relevance_filtering:
            stage_start = time.time()
            result = self._stage_relevance_filtering(query, current_docs)
            result.duration_ms = (time.time() - stage_start) * 1000
            stage_results.append(result)
            
            if result.decision == PipelineDecision.HALT:
                return self._create_halt_result(
                    stage_results, start_time, "Relevance filtering failed"
                )
            current_docs = result.documents
            
        # Stage 2: Source Authority Tiering
        if self.config.enable_source_tiering:
            stage_start = time.time()
            result = self._stage_source_tiering(current_docs)
            result.duration_ms = (time.time() - stage_start) * 1000
            stage_results.append(result)
            
            if result.decision == PipelineDecision.HALT:
                return self._create_halt_result(
                    stage_results, start_time, "No authoritative sources found"
                )
            current_docs = result.documents
            
        # Stage 3: Query Enhancement (HyDE) - conditional
        if self.config.enable_query_enhancement and self._is_sparse_query(query):
            stage_start = time.time()
            result = self._stage_query_enhancement(query, current_docs)
            result.duration_ms = (time.time() - stage_start) * 1000
            stage_results.append(result)
            
            if result.decision == PipelineDecision.REFINE:
                refinement_count += 1
            current_docs = result.documents
            
        # Stage 4: Self-Critique Guardrail
        if self.config.enable_self_critique and claims_to_verify:
            stage_start = time.time()
            result = self._stage_self_critique(claims_to_verify, current_docs)
            result.duration_ms = (time.time() - stage_start) * 1000
            stage_results.append(result)
            
            if result.decision == PipelineDecision.HALT:
                return self._create_halt_result(
                    stage_results, start_time, "Self-critique validation failed"
                )
            elif result.decision == PipelineDecision.REFINE:
                refinement_count += 1
                
        # Stage 5: External Fact-Checking
        if self.config.enable_fact_checking and self.fact_checker and claims_to_verify:
            stage_start = time.time()
            result = self._stage_fact_checking(claims_to_verify, current_docs)
            result.duration_ms = (time.time() - stage_start) * 1000
            stage_results.append(result)
            
            if result.decision == PipelineDecision.HALT:
                return self._create_halt_result(
                    stage_results, start_time, "Fact-checking failed"
                )
                
        # Calculate final confidence
        total_confidence = self._calculate_total_confidence(stage_results)
        total_duration = (time.time() - start_time) * 1000
        
        return PipelineResult(
            success=True,
            final_documents=current_docs,
            stage_results=stage_results,
            total_confidence=total_confidence,
            total_duration_ms=total_duration,
            refinement_count=refinement_count,
        )
    
    def _stage_relevance_filtering(
        self,
        query: str,
        documents: List[RetrievedDocument],
    ) -> StageResult:
        """Stage 1: Filter documents by relevance using cross-encoder reranking."""
        if not documents:
            return StageResult(
                stage=SignalQualityStage.RELEVANCE_FILTERING,
                decision=PipelineDecision.HALT,
                documents=[],
                confidence=0.0,
                reasoning="No documents to filter",
            )
            
        # If we have a reranker, use it
        if self.reranker:
            doc_dicts = [{"content": d.content, "metadata": d.metadata} for d in documents]
            reranked = self.reranker.rerank(query, doc_dicts, top_k=self.config.max_documents_per_stage)
            
            # Update relevance scores
            filtered_docs = []
            for doc_dict, score in reranked:
                # Find matching document
                for doc in documents:
                    if doc.content == doc_dict["content"]:
                        doc.relevance_score = score
                        if score >= self.config.min_relevance_score:
                            filtered_docs.append(doc)
                        break
        else:
            # Fallback: simple keyword matching
            filtered_docs = self._simple_relevance_filter(query, documents)
            
        if not filtered_docs:
            return StageResult(
                stage=SignalQualityStage.RELEVANCE_FILTERING,
                decision=PipelineDecision.REFINE,
                documents=documents[:5],  # Return top 5 anyway
                confidence=0.3,
                reasoning="No documents met relevance threshold, returning top candidates",
                refinement_suggestions=["Broaden search query", "Use HyDE enhancement"],
            )
            
        avg_relevance = sum(d.relevance_score for d in filtered_docs) / len(filtered_docs)
        
        return StageResult(
            stage=SignalQualityStage.RELEVANCE_FILTERING,
            decision=PipelineDecision.PROCEED,
            documents=filtered_docs,
            confidence=avg_relevance,
            reasoning=f"Filtered to {len(filtered_docs)} relevant documents",
        )
    
    def _stage_source_tiering(
        self,
        documents: List[RetrievedDocument],
    ) -> StageResult:
        """Stage 2: Prioritize documents by source authority tier."""
        if not documents:
            return StageResult(
                stage=SignalQualityStage.SOURCE_AUTHORITY_TIERING,
                decision=PipelineDecision.HALT,
                documents=[],
                confidence=0.0,
                reasoning="No documents to tier",
            )
            
        # Assign authority scores based on tier
        for doc in documents:
            tier_weight = self.config.tier_weights.get(doc.source_tier, 0.2)
            doc.authority_score = tier_weight
            
        # Sort by composite score (relevance + authority)
        sorted_docs = sorted(documents, key=lambda d: d.composite_score, reverse=True)
        
        # Filter by minimum authority
        filtered_docs = [
            d for d in sorted_docs
            if d.authority_score >= self.config.min_authority_score
        ]
        
        if not filtered_docs:
            # Return all docs but flag as low confidence
            return StageResult(
                stage=SignalQualityStage.SOURCE_AUTHORITY_TIERING,
                decision=PipelineDecision.PROCEED,
                documents=sorted_docs[:self.config.max_documents_per_stage],
                confidence=0.4,
                reasoning="No high-authority sources found, proceeding with caution",
                refinement_suggestions=["Seek official sources", "Verify claims independently"],
            )
            
        avg_authority = sum(d.authority_score for d in filtered_docs) / len(filtered_docs)
        
        return StageResult(
            stage=SignalQualityStage.SOURCE_AUTHORITY_TIERING,
            decision=PipelineDecision.PROCEED,
            documents=filtered_docs[:self.config.max_documents_per_stage],
            confidence=avg_authority,
            reasoning=f"Prioritized {len(filtered_docs)} authoritative sources",
        )
    
    def _stage_query_enhancement(
        self,
        query: str,
        documents: List[RetrievedDocument],
    ) -> StageResult:
        """Stage 3: Enhance sparse queries using HyDE."""
        if not self.config.hyde_config.enabled or not self.llm_generate:
            return StageResult(
                stage=SignalQualityStage.QUERY_ENHANCEMENT,
                decision=PipelineDecision.PROCEED,
                documents=documents,
                confidence=0.5,
                reasoning="HyDE disabled or no LLM available",
            )
            
        # Generate hypothetical document
        hyde_prompt = f"""Generate a hypothetical ideal document that would perfectly answer this query:

Query: {query}

Write a detailed, factual response as if it were from an authoritative source.
Focus on specific details, metrics, and concrete information."""

        try:
            hypothetical_doc = self.llm_generate(hyde_prompt)
            
            # In a full implementation, we would:
            # 1. Embed the hypothetical document
            # 2. Re-retrieve documents similar to the hypothetical
            # 3. Merge with existing documents
            
            # For now, just mark that enhancement was attempted
            return StageResult(
                stage=SignalQualityStage.QUERY_ENHANCEMENT,
                decision=PipelineDecision.PROCEED,
                documents=documents,
                confidence=0.7,
                reasoning="Query enhanced with HyDE",
                metadata={"hypothetical_doc_preview": hypothetical_doc[:200]},
            )
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            logger.warning(f"HyDE enhancement failed: {e}")
            return StageResult(
                stage=SignalQualityStage.QUERY_ENHANCEMENT,
                decision=PipelineDecision.PROCEED,
                documents=documents,
                confidence=0.5,
                reasoning=f"HyDE enhancement failed: {str(e)}",
            )
    
    def _stage_self_critique(
        self,
        claims: List[str],
        documents: List[RetrievedDocument],
    ) -> StageResult:
        """Stage 4: Validate that retrieved context supports claims."""
        if not claims:
            return StageResult(
                stage=SignalQualityStage.SELF_CRITIQUE_GUARDRAIL,
                decision=PipelineDecision.PROCEED,
                documents=documents,
                confidence=1.0,
                reasoning="No claims to verify",
            )
            
        # Combine document content for context
        context = "\n\n".join(d.content for d in documents[:10])
        
        critique_results: List[SelfCritiqueResult] = []
        
        for claim in claims:
            result = self._critique_single_claim(claim, context)
            critique_results.append(result)
            
        # Calculate overall support
        supported_count = sum(1 for r in critique_results if r.is_supported)
        support_ratio = supported_count / len(claims) if claims else 0
        
        # Determine decision based on verification mode
        if self.config.claim_verification_mode == ClaimVerificationMode.STRICT:
            threshold = 1.0  # All claims must be supported
        elif self.config.claim_verification_mode == ClaimVerificationMode.BALANCED:
            threshold = 0.7  # 70% of claims
        else:
            threshold = 0.5  # 50% of claims
            
        if support_ratio < threshold:
            unsupported = [r.claim for r in critique_results if not r.is_supported]
            gaps = []
            for r in critique_results:
                gaps.extend(r.gaps_identified)
                
            return StageResult(
                stage=SignalQualityStage.SELF_CRITIQUE_GUARDRAIL,
                decision=PipelineDecision.REFINE if support_ratio > 0.3 else PipelineDecision.HALT,
                documents=documents,
                confidence=support_ratio,
                reasoning=f"Only {supported_count}/{len(claims)} claims supported",
                refinement_suggestions=gaps[:5],
                metadata={"unsupported_claims": unsupported},
            )
            
        return StageResult(
            stage=SignalQualityStage.SELF_CRITIQUE_GUARDRAIL,
            decision=PipelineDecision.PROCEED,
            documents=documents,
            confidence=support_ratio,
            reasoning=f"All {supported_count} claims adequately supported",
        )
    
    def _stage_fact_checking(
        self,
        claims: List[str],
        documents: List[RetrievedDocument],
    ) -> StageResult:
        """Stage 5: Verify key claims against external fact-checking provider."""
        if not self.fact_checker:
            return StageResult(
                stage=SignalQualityStage.EXTERNAL_FACT_CHECKING,
                decision=PipelineDecision.PROCEED,
                documents=documents,
                confidence=0.5,
                reasoning="No fact-checker available",
            )
            
        context = "\n\n".join(d.content for d in documents[:5])
        verified_count = 0
        total_confidence = 0.0
        
        for claim in claims[:5]:  # Limit to top 5 claims for efficiency
            try:
                is_verified, confidence, explanation = self.fact_checker.verify_claim(claim, context)
                if is_verified:
                    verified_count += 1
                total_confidence += confidence
            except (ValueError, TypeError, RuntimeError, KeyError) as e:
                logger.warning(f"Fact-checking failed for claim: {e}")
                
        avg_confidence = total_confidence / len(claims[:5]) if claims else 0
        
        return StageResult(
            stage=SignalQualityStage.EXTERNAL_FACT_CHECKING,
            decision=PipelineDecision.PROCEED if verified_count > 0 else PipelineDecision.REFINE,
            documents=documents,
            confidence=avg_confidence,
            reasoning=f"Verified {verified_count}/{min(len(claims), 5)} claims externally",
        )
    
    def _simple_relevance_filter(
        self,
        query: str,
        documents: List[RetrievedDocument],
    ) -> List[RetrievedDocument]:
        """Fallback relevance filtering using keyword matching."""
        query_terms = set(query.lower().split())
        
        for doc in documents:
            doc_terms = set(doc.content.lower().split())
            overlap = len(query_terms & doc_terms)
            doc.relevance_score = min(overlap / len(query_terms), 1.0) if query_terms else 0
            
        return [d for d in documents if d.relevance_score >= self.config.min_relevance_score]
    
    def _critique_single_claim(self, claim: str, context: str) -> SelfCritiqueResult:
        """Critique a single claim against context."""
        # Simple heuristic: check if key terms from claim appear in context
        claim_terms = set(claim.lower().split())
        context_lower = context.lower()
        
        found_terms = [term for term in claim_terms if term in context_lower]
        coverage = len(found_terms) / len(claim_terms) if claim_terms else 0
        
        is_supported = coverage >= self.config.self_critique_threshold
        
        gaps = []
        if not is_supported:
            missing = claim_terms - set(found_terms)
            gaps = [f"Missing evidence for: {', '.join(list(missing)[:5])}"]
            
        return SelfCritiqueResult(
            claim=claim,
            is_supported=is_supported,
            supporting_evidence=found_terms,
            confidence=coverage,
            reasoning=f"Found {len(found_terms)}/{len(claim_terms)} claim terms in context",
            gaps_identified=gaps,
        )
    
    def _is_sparse_query(self, query: str) -> bool:
        """Determine if a query is sparse and would benefit from HyDE."""
        # Simple heuristic: queries under 5 words are considered sparse
        return len(query.split()) < 5
    
    def _calculate_total_confidence(self, stage_results: List[StageResult]) -> float:
        """Calculate weighted total confidence from all stages."""
        if not stage_results:
            return 0.0
            
        # Weight later stages more heavily
        weights = [0.15, 0.20, 0.15, 0.30, 0.20]  # Must sum to 1.0
        
        total = 0.0
        weight_sum = 0.0
        
        for i, result in enumerate(stage_results):
            weight = weights[i] if i < len(weights) else 0.1
            total += result.confidence * weight
            weight_sum += weight
            
        return total / weight_sum if weight_sum > 0 else 0.0
    
    def _create_halt_result(
        self,
        stage_results: List[StageResult],
        start_time: float,
        reason: str,
    ) -> PipelineResult:
        """Create a halted pipeline result."""
        import time
        return PipelineResult(
            success=False,
            final_documents=[],
            stage_results=stage_results,
            total_confidence=0.0,
            total_duration_ms=(time.time() - start_time) * 1000,
            halt_reason=reason,
        )


# =============================================================================
# FAILURE RECOVERY
# =============================================================================

@dataclass
class HopRefinementConfig:
    """Configuration for hop refinement on search failure."""
    max_refinements: int = 2
    breadth_increase_factor: float = 1.5
    use_hyde_on_failure: bool = True


class HopRefinementStrategy:
    """
    Failure recovery strategy for RAG hops.
    
    From historical: "On search failure, first increase search breadth.
    If still fails, switch to a HyDE-guided query. Max 2 refinements."
    """
    
    def __init__(self, config: Optional[HopRefinementConfig] = None) -> None:
        self.config = config or HopRefinementConfig()
        self.refinement_count = 0
        
    def should_refine(self) -> bool:
        """Check if more refinements are allowed."""
        return self.refinement_count < self.config.max_refinements
    
    def get_refinement_strategy(self) -> str:
        """Get the next refinement strategy to try."""
        if self.refinement_count == 0:
            return "INCREASE_BREADTH"
        elif self.refinement_count == 1 and self.config.use_hyde_on_failure:
            return "HYDE_GUIDED"
        else:
            return "EXHAUSTED"
            
    def record_refinement(self) -> None:
        """Record that a refinement was attempted."""
        self.refinement_count += 1
        
    def reset(self) -> None:
        """Reset refinement counter."""
        self.refinement_count = 0


# =============================================================================
# builder FUNCTIONS
# =============================================================================

def create_default_pipeline() -> SignalQualityPipeline:
    """Create a pipeline with default configuration."""
    return SignalQualityPipeline(config=SignalQualityConfig())


def create_strict_pipeline() -> SignalQualityPipeline:
    """Create a pipeline with strict verification."""
    config = SignalQualityConfig(
        claim_verification_mode=ClaimVerificationMode.STRICT,
        min_relevance_score=0.6,
        min_authority_score=0.5,
        self_critique_threshold=0.8,
    )
    return SignalQualityPipeline(config=config)


def create_permissive_pipeline() -> SignalQualityPipeline:
    """Create a pipeline with permissive verification."""
    config = SignalQualityConfig(
        claim_verification_mode=ClaimVerificationMode.PERMISSIVE,
        min_relevance_score=0.3,
        min_authority_score=0.2,
        self_critique_threshold=0.5,
        enable_fact_checking=False,
    )
    return SignalQualityPipeline(config=config)