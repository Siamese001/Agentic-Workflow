"""K2 Insights Executor - Second hop in the sequential K1-K7 execution pipeline.

Incorporated from L2 lic_k2_insights.py to process K1 research output, extract
claims, score them against sources, and generate validated insights with
confidence metrics for K3 draft generation.

This is the second execution phase in the hop-based architecture that follows:
L1 Planning → K1 Research → K2 Insights → K3 Draft → K4 Regeneration → K5 Validation → K6 CTA → K7 Assembly
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ClaimScore:
    """Individual claim with confidence scoring."""
    claim: str
    confidence_score: float
    supporting_sources: List[str]
    source_count: int
    signal_strength: str  # "high", "medium", "low"
    validation_status: str  # "validated", "questionable", "unverified"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InsightOutput:
    """Output from K2 insights execution phase."""
    per_claim_scores: List[ClaimScore]
    aggregate_confidence: float
    validated_claims: List[str]
    confidence_violations: List[str]
    key_insights: List[str]
    signal_summary: Dict[str, Any]
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: Optional[int] = None


class K2InsightsExecutor:
    """K2 insights executor - second hop in sequential execution pipeline.
    
    Processes K1 research output to extract claims, score them against sources,
    and generate validated insights for K3 draft generation.
    """
    
    def __init__(self, insight_plan: Optional[Any] = None, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize K2 insights executor."""
        self.insight_plan = insight_plan
        self.telemetry_bus = telemetry_bus
        
        # Default insight configuration
        self.default_config = {
            "signal_weights": {
                "source_relevance": 0.3,
                "web_authority": 0.2,
                "internal_authority": 0.4,
                "company_verified": 0.5
            },
            "min_signal_threshold": 0.6,
            "per_claim_min_confidence": 0.5,
            "aggregate_min_confidence": 0.7,
            "confidence_enforcement": True
        }
        
        # Claim extraction patterns
        self.claim_patterns = {
            "achievement": r"(?:achieved|delivered|completed|launched|increased|decreased|improved|generated)\s+[^.!?]*",
            "responsibility": r"(?:responsible for|managed|led|directed|oversaw|coordinated)\s+[^.!?]*",
            "expertise": r"(?:expert in|specialized in|skilled in|experienced with)\s+[^.!?]*",
            "impact": r"(?:resulted in|led to|caused|enabled)\s+[^.!?]*"
        }
        
        # Signal strength thresholds
        self.strength_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }


# Alias for backward compatibility with tests
LIC_K2_Insights = K2InsightsExecutor
    
    def execute(
        self,
        *,
        research_output: Any,
        insight_plan: Optional[Any] = None,
        outreach_context: Dict[str, Any] = None,
    ) -> InsightOutput:
        """Execute K2 insights phase.
        
        Args:
            research_output: Output from K1 research execution
            insight_plan: Optional insight plan from L1 planning
            outreach_context: Additional context for insights
            
        Returns:
            Complete insights output with scored claims and validation
        """
        outreach_context = outreach_context or {}
        
        # Use provided plan or fall back to default
        plan = insight_plan or self.insight_plan
        
        # 1. Extract claims from research sources
        claims = self._extract_claims_from_research(research_output)
        
        # 2. Score individual claims against sources
        claim_scores = self._score_claims(claims, research_output, plan)
        
        # 3. Calculate aggregate confidence
        aggregate_confidence = self._calculate_aggregate_confidence(claim_scores, plan)
        
        # 4. Identify validated claims and violations
        validated_claims, confidence_violations = self._validate_claims(claim_scores, plan)
        
        # 5. Generate key insights
        key_insights = self._generate_key_insights(claim_scores, research_output)
        
        # 6. Create signal summary
        signal_summary = self._create_signal_summary(claim_scores, research_output)
        
        # 7. Build execution metadata
        execution_metadata = {
            "claims_extracted": len(claims),
            "claims_scored": len(claim_scores),
            "validated_claims": len(validated_claims),
            "violations": len(confidence_violations),
            "aggregate_confidence": aggregate_confidence,
            "insight_plan_used": plan is not None
        }
        
        # 8. Create insights output
        output = InsightOutput(
            per_claim_scores=claim_scores,
            aggregate_confidence=aggregate_confidence,
            validated_claims=validated_claims,
            confidence_violations=confidence_violations,
            key_insights=key_insights,
            signal_summary=signal_summary,
            execution_metadata=execution_metadata
        )
        
        # 9. Record telemetry (best-effort)
        self._safe_record_telemetry(output)
        
        return output
    
    def _extract_claims_from_research(self, research_output: Any) -> List[str]:
        """Extract claims from research sources and context."""
        claims = []
        
        # Get sources from research output
        sources = getattr(research_output, 'rag_sources', [])
        
        # Extract claims from each source
        for source in sources:
            content = source.get("content", "")
            source_claims = self.extract_claims_from_text(content)
            claims.extend(source_claims)
        
        # Extract claims from enriched context
        enriched_context = getattr(research_output, 'enriched_context', {})
        key_insights = enriched_context.get("key_insights", [])
        claims.extend(key_insights)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_claims = []
        for claim in claims:
            normalized = claim.lower().strip()
            if normalized not in seen and len(normalized) > 10:
                seen.add(normalized)
                unique_claims.append(claim.strip())
        
        return unique_claims[:20]  # Limit to top 20 claims
    
    def extract_claims_from_text(self, text: str) -> List[str]:
        """Extract individual claims from text using pattern matching."""
        claims = []
        
        # Split by sentence delimiters
        splitters = r'[.!?]\s+|and\s+|while\s+|by\s+|with\s+'
        raw_claims = re.split(splitters, text)
        
        # Filter and clean claims
        for claim in raw_claims:
            claim = claim.strip()
            if len(claim) > 10 and len(claim) < 200:  # Reasonable length
                # Check if claim contains meaningful content
                if any(pattern in claim.lower() for pattern in ["achieved", "led", "managed", "developed", "improved", "responsible"]):
                    claims.append(claim)
        
        return claims
    
    def _score_claims(self, claims: List[str], research_output: Any, plan: Optional[Any]) -> List[ClaimScore]:
        """Score individual claims against research sources."""
        claim_scores = []
        sources = getattr(research_output, 'rag_sources', [])
        
        for claim in claims:
            # Calculate confidence score
            confidence_score = self._score_individual_claim(claim, sources, plan)
            
            # Identify supporting sources
            supporting_sources = self._find_supporting_sources(claim, sources)
            
            # Determine signal strength
            signal_strength = self._determine_signal_strength(confidence_score)
            
            # Set validation status
            validation_status = self._determine_validation_status(confidence_score, plan)
            
            # Create claim score
            claim_score = ClaimScore(
                claim=claim,
                confidence_score=confidence_score,
                supporting_sources=supporting_sources,
                source_count=len(supporting_sources),
                signal_strength=signal_strength,
                validation_status=validation_status,
                metadata={
                    "claim_length": len(claim),
                    "source_types": list(set(s.get("source_type", "unknown") for s in sources if self._claim_supported_by_source(claim, s)))
                }
            )
            claim_scores.append(claim_score)
        
        # Sort by confidence score (descending)
        claim_scores.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return claim_scores
    
    def _score_individual_claim(self, claim: str, sources: List[Dict[str, Any]], plan: Optional[Any]) -> float:
        """Score individual claim against research sources."""
        if not sources:
            return 0.5
        
        # Get signal weights from plan or use defaults
        if plan and hasattr(plan, 'signal_weights'):
            signal_weights = plan.signal_weights
        else:
            signal_weights = self.default_config["signal_weights"]
        
        score = 0.0
        claim_words = claim.lower().split()
        significant_words = [w for w in claim_words if len(w) > 3]
        
        # Score against top sources
        top_sources = sorted(sources, key=lambda x: x.get("relevance_score", 0), reverse=True)[:5]
        
        for source in top_sources:
            content = source.get("content", "").lower()
            source_relevance = source.get("relevance_score", 0.5)
            
            # Check for word overlap
            word_overlap = sum(1 for word in significant_words if word in content)
            if word_overlap >= 2:  # At least 2 significant words overlap
                score += signal_weights.get("source_relevance", 0.3) * source_relevance
            
            # Source type bonuses
            source_type = source.get("source_type", "")
            if source_type == "company":
                score += signal_weights.get("company_verified", 0.5) * source_relevance
            elif source_type == "internal":
                score += signal_weights.get("internal_authority", 0.4) * source_relevance
            elif source_type == "web":
                score += signal_weights.get("web_authority", 0.2) * source_relevance
        
        # Normalize score
        max_possible_score = len(top_sources) * max(signal_weights.values())
        if max_possible_score > 0:
            normalized_score = min(score / max_possible_score, 1.0)
        else:
            normalized_score = 0.5
        
        return round(normalized_score, 3)
    
    def _find_supporting_sources(self, claim: str, sources: List[Dict[str, Any]]) -> List[str]:
        """Find sources that support the claim."""
        supporting = []
        claim_words = claim.lower().split()
        significant_words = [w for w in claim_words if len(w) > 3]
        
        for source in sources:
            if self._claim_supported_by_source(claim, source):
                supporting.append(source.get("title", "Unknown source"))
        
        return supporting[:5]  # Limit to top 5 supporting sources
    
    def _claim_supported_by_source(self, claim: str, source: Dict[str, Any]) -> bool:
        """Check if a source supports the claim."""
        content = source.get("content", "").lower()
        claim_words = claim.lower().split()
        significant_words = [w for w in claim_words if len(w) > 3]
        
        # Need at least 2 significant words to match
        word_overlap = sum(1 for word in significant_words if word in content)
        return word_overlap >= 2
    
    def _determine_signal_strength(self, confidence_score: float) -> str:
        """Determine signal strength category."""
        if confidence_score >= self.strength_thresholds["high"]:
            return "high"
        elif confidence_score >= self.strength_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _determine_validation_status(self, confidence_score: float, plan: Optional[Any]) -> str:
        """Determine validation status for claim."""
        # Get minimum confidence from plan or use default
        if plan and hasattr(plan, 'per_claim_min_confidence'):
            min_confidence = plan.per_claim_min_confidence
        else:
            min_confidence = self.default_config["per_claim_min_confidence"]
        
        if confidence_score >= min_confidence:
            return "validated"
        elif confidence_score >= min_confidence * 0.7:
            return "questionable"
        else:
            return "unverified"
    
    def _calculate_aggregate_confidence(self, claim_scores: List[ClaimScore], plan: Optional[Any]) -> float:
        """Calculate aggregate confidence from all claim scores."""
        if not claim_scores:
            return 0.0
        
        # Weight by signal strength
        weighted_scores = []
        for claim_score in claim_scores:
            weight = 1.0
            if claim_score.signal_strength == "high":
                weight = 1.2
            elif claim_score.signal_strength == "low":
                weight = 0.8
            
            weighted_scores.append(claim_score.confidence_score * weight)
        
        # Calculate weighted average
        aggregate = sum(weighted_scores) / sum(weight for _ in weighted_scores)
        
        return round(aggregate, 3)
    
    def _validate_claims(self, claim_scores: List[ClaimScore], plan: Optional[Any]) -> tuple[List[str], List[str]]:
        """Identify validated claims and confidence violations."""
        validated_claims = []
        confidence_violations = []
        
        # Get thresholds from plan or use defaults
        if plan and hasattr(plan, 'aggregate_min_confidence'):
            aggregate_threshold = plan.aggregate_min_confidence
        else:
            aggregate_threshold = self.default_config["aggregate_min_confidence"]
        
        for claim_score in claim_scores:
            if claim_score.validation_status == "validated":
                validated_claims.append(claim_score.claim)
            elif claim_score.confidence_score < aggregate_threshold * 0.5:
                confidence_violations.append(f"Low confidence: {claim_score.claim[:50]}...")
        
        return validated_claims, confidence_violations
    
    def _generate_key_insights(self, claim_scores: List[ClaimScore], research_output: Any) -> List[str]:
        """Generate key insights from validated claims."""
        insights = []
        
        # Get top validated claims
        validated_claims = [cs for cs in claim_scores if cs.validation_status == "validated"]
        top_claims = validated_claims[:5]
        
        for claim_score in top_claims:
            insight = f"{claim_score.claim} (confidence: {claim_score.confidence_score:.2f})"
            insights.append(insight)
        
        # Add research context insights
        enriched_context = getattr(research_output, 'enriched_context', {})
        context_insights = enriched_context.get("key_insights", [])
        insights.extend(context_insights[:3])
        
        return insights[:8]  # Limit to top 8 insights
    
    def _create_signal_summary(self, claim_scores: List[ClaimScore], research_output: Any) -> Dict[str, Any]:
        """Create summary of signal analysis."""
        if not claim_scores:
            return {"total_claims": 0}
        
        # Signal strength distribution
        strength_counts = {
            "high": len([cs for cs in claim_scores if cs.signal_strength == "high"]),
            "medium": len([cs for cs in claim_scores if cs.signal_strength == "medium"]),
            "low": len([cs for cs in claim_scores if cs.signal_strength == "low"])
        }
        
        # Validation status distribution
        validation_counts = {
            "validated": len([cs for cs in claim_scores if cs.validation_status == "validated"]),
            "questionable": len([cs for cs in claim_scores if cs.validation_status == "questionable"]),
            "unverified": len([cs for cs in claim_scores if cs.validation_status == "unverified"])
        }
        
        # Source analysis
        avg_sources = sum(cs.source_count for cs in claim_scores) / len(claim_scores)
        
        return {
            "total_claims": len(claim_scores),
            "strength_distribution": strength_counts,
            "validation_distribution": validation_counts,
            "average_sources_per_claim": round(avg_sources, 1),
            "highest_confidence": max(cs.confidence_score for cs in claim_scores),
            "lowest_confidence": min(cs.confidence_score for cs in claim_scores)
        }
    
    def _safe_record_telemetry(self, output: InsightOutput) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("k2_insights_executed", {
                    "claims_scored": len(output.per_claim_scores),
                    "validated_claims": len(output.validated_claims),
                    "aggregate_confidence": output.aggregate_confidence,
                    "violations": len(output.confidence_violations)
                })
        except Exception as e:
            logger.debug(f"Failed to record telemetry: {e}")
    
    def get_insights_summary(self, output: InsightOutput) -> Dict[str, Any]:
        """Get a summary of the insights execution for debugging/telemetry."""
        return {
            "execution_id": "k2_insights",
            "claims_scored": len(output.per_claim_scores),
            "validated_claims": len(output.validated_claims),
            "confidence_violations": len(output.confidence_violations),
            "aggregate_confidence": output.aggregate_confidence,
            "key_insights_count": len(output.key_insights),
            "signal_summary": output.signal_summary,
            "validation_distribution": {
                status: len([cs for cs in output.per_claim_scores if cs.validation_status == status])
                for status in ["validated", "questionable", "unverified"]
            }
        }





