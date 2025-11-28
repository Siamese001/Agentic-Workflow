from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class InsightOutput:
    per_claim_scores: List[Dict[str, Any]]
    aggregate_confidence: float
    validated_claims: List[str]
    confidence_violations: List[str]

class LIC_K2_Insights:
    def __init__(self, insight_plan):
        self.plan = insight_plan
        
    def extract_claims_from_text(self, text: str) -> List[str]:
        import re
        
        splitters = r'[.]\s+|and\s+|while\s+|by\s+'
        claims = re.split(splitters, text)
        
        claims = [claim.strip() for claim in claims if claim.strip()]
        
        return claims
    
    def score_individual_claim(self, claim: str, sources: List[Dict[str, Any]]) -> float:
        if not sources:
            return 0.5
            
        signal_weights = self.plan.signal_weights
        
        score = 0.0
        for source in sources[:3]:
            content = source.get("content", "").lower()
            claim_lower = claim.lower()
            
            if any(word in content for word in claim_lower.split() if len(word) > 3):
                score += signal_weights.get("source_relevance", 0.3)
                
            if source.get("source_type") == "web_search":
                score += signal_weights.get("web_authority", 0.2)
            elif source.get("source_type") == "project_knowledge":
                score += signal_weights.get("internal_authority", 0.4)
                
        return min(1.0, score / len(sources[:3]))
    
    def calculate_aggregate_confidence(self, claim_scores: List[float]) -> float:
        if not claim_scores:
            return 0.0
        return sum(claim_scores) / len(claim_scores)
    
    def validate_confidence_thresholds(self, claim_scores: List[float], aggregate_score: float) -> Dict[str, Any]:
        violations = []
        
        per_claim_min = self.plan["per_claim_min_confidence"]
        aggregate_min = self.plan["aggregate_min_confidence"]
        
        for i, score in enumerate(claim_scores):
            if score < per_claim_min:
                violations.append(f"Claim {i+1} below threshold: {score:.3f} < {per_claim_min}")
                
        if aggregate_score < aggregate_min:
            violations.append(f"Aggregate below threshold: {aggregate_score:.3f} < {aggregate_min}")
            
        return {
            "violations": violations,
            "per_claim_met": all(score >= per_claim_min for score in claim_scores),
            "aggregate_met": aggregate_score >= aggregate_min,
            "enforcement": self.plan["confidence_enforcement"]
        }
    
    def extract_key_insights(self, sources: List[Dict[str, Any]]) -> List[str]:
        insights = []
        
        for source in sources[:5]:
            content = source.get("content", "")
            
            if "initiative" in content.lower():
                insights.append("Strategic initiative focus identified")
            elif "growth" in content.lower():
                insights.append("Growth-oriented priorities detected")
            elif "technology" in content.lower():
                insights.append("Technology leadership emphasis noted")
            elif "team" in content.lower():
                insights.append("Team development priorities found")
                
        return insights[:3]
    
    def execute(self, research_output, draft_text: Optional[str] = None) -> InsightOutput:
        sources = research_output.rag_sources if hasattr(research_output, 'rag_sources') else research_output.get("rag_sources", [])
        
        if not draft_text:
            claims = self.extract_key_insights(sources)
            claim_scores = [0.9] * len(claims)
        else:
            claims = self.extract_claims_from_text(draft_text)
            claim_scores = [self.score_individual_claim(claim, sources) for claim in claims]
        
        aggregate_confidence = self.calculate_aggregate_confidence(claim_scores)
        
        validation_result = self.validate_confidence_thresholds(claim_scores, aggregate_confidence)
        
        validated_claims = []
        for i, (claim, score) in enumerate(zip(claims, claim_scores)):
            if score >= self.plan["per_claim_min_confidence"]:
                validated_claims.append(claim)
                
        return InsightOutput(
            per_claim_scores=[
                {
                    "claim": claim,
                    "score": score,
                    "valid": score >= self.plan["per_claim_min_confidence"]
                }
                for claim, score in zip(claims, claim_scores)
            ],
            aggregate_confidence=aggregate_confidence,
            validated_claims=validated_claims,
            confidence_violations=validation_result["violations"]
        )
