#!/usr/bin/env python3
"""
Outreach Engine Insights - Lift & Shift + Enhanced from LIC
Signal quality scoring and claim confidence modeling
"""

from typing import Dict, List, Optional, Any, Tuple
import re
from datetime import datetime, timedelta

from .models import (
    RAGEvidence, ValidationResult, ValidationSeverity
)


class SignalQualityScorer:
    """Signal quality scoring - Lift & Shift from LIC"""
    
    def __init__(self, insight_patterns: Dict[str, Any]):
        self.signal_config = insight_patterns.get("signal_quality_scorer", {})
        self.source_weights = self.signal_config.get("source_weights", {})
        self.minimum_signal_threshold = self.signal_config.get("minimum_signal_threshold", 0.7)
    
    def calculate_signal_quality(self, rag_evidence: List[RAGEvidence]) -> Tuple[float, Dict[str, Any]]:
        """Calculate overall signal quality score from RAG evidence"""
        if not rag_evidence:
            return 0.0, {"error": "No RAG evidence provided"}
        
        weighted_scores = []
        source_breakdown = {}
        
        for evidence in rag_evidence:
            # Get source weight
            source_type = evidence.source_type
            weight = self.source_weights.get(source_type, 1.0)
            
            # Calculate weighted score (relevance * authority * recency)
            base_score = evidence.relevance_score * evidence.authority_score * evidence.recency_score
            weighted_score = base_score * weight
            
            weighted_scores.append(weighted_score)
            source_breakdown[source_type] = source_breakdown.get(source_type, {
                "count": 0,
                "total_weighted_score": 0.0,
                "weight": weight
            })
            source_breakdown[source_type]["count"] += 1
            source_breakdown[source_type]["total_weighted_score"] += weighted_score
        
        # Calculate overall quality score
        if weighted_scores:
            overall_score = sum(weighted_scores) / len(weighted_scores)
            # Normalize to 0-1 range
            overall_score = min(1.0, overall_score)
        else:
            overall_score = 0.0
        
        # Prepare breakdown
        for source_type in source_breakdown:
            breakdown = source_breakdown[source_type]
            breakdown["average_score"] = breakdown["total_weighted_score"] / breakdown["count"]
        
        return overall_score, {
            "source_breakdown": source_breakdown,
            "evidence_count": len(rag_evidence),
            "threshold_met": overall_score >= self.minimum_signal_threshold,
            "minimum_threshold": self.minimum_signal_threshold
        }
    
    def validate_signal_quality(self, signal_score: float, breakdown: Dict[str, Any]) -> List[ValidationResult]:
        """Validate signal quality against thresholds"""
        validation_results = []
        
        if signal_score < self.minimum_signal_threshold:
            validation_results.append(ValidationResult(
                rule_id="SIGNAL_QUALITY_BELOW_THRESHOLD",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"Signal quality {signal_score:.3f} below threshold {self.minimum_signal_threshold}",
                details={
                    "signal_score": signal_score,
                    "threshold": self.minimum_signal_threshold,
                    "source_breakdown": breakdown.get("source_breakdown", {})
                }
            ))
        
        # Check for low-quality source types
        source_breakdown = breakdown.get("source_breakdown", {})
        low_quality_sources = [
            source for source, data in source_breakdown.items()
            if data.get("average_score", 0) < 0.5
        ]
        
        if low_quality_sources:
            validation_results.append(ValidationResult(
                rule_id="LOW_QUALITY_SOURCES_DETECTED",
                passed=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Low quality sources: {', '.join(low_quality_sources)}",
                details={"low_quality_sources": low_quality_sources}
            ))
        
        return validation_results
    
    def get_source_weight_summary(self) -> Dict[str, Any]:
        """Get summary of source weights"""
        return {
            "source_weights": self.source_weights,
            "minimum_threshold": self.minimum_signal_threshold,
            "highest_weight": max(self.source_weights.values()) if self.source_weights else 1.0,
            "lowest_weight": min(self.source_weights.values()) if self.source_weights else 1.0
        }


class ClaimConfidenceScorer:
    """Claim confidence scoring - Enhanced from LIC"""
    
    def __init__(self, insight_patterns: Dict[str, Any]):
        self.claim_config = insight_patterns.get("claim_confidence_scorer", {})
        self.per_claim_minimum = self.claim_config.get("per_claim_minimum", 0.8)
        self.aggregate_minimum = self.claim_config.get("aggregate_minimum", 0.95)
        self.scoring_methodology = self.claim_config.get("scoring_methodology", {})
        self.claim_extraction = self.scoring_methodology.get("claim_extraction", {})
        self.per_claim_scoring = self.scoring_methodology.get("per_claim_scoring", {})
    
    def extract_claims(self, message_body: str) -> List[str]:
        """Extract atomic claims from message body"""
        splitters = self.claim_extraction.get("splitters", [".", "and", "while", "by"])
        
        # Split message into potential claims
        claims = [message_body]
        for splitter in splitters:
            new_claims = []
            for claim in claims:
                new_claims.extend(claim.split(splitter))
            claims = new_claims
        
        # Clean and filter claims
        cleaned_claims = []
        for claim in claims:
            claim = claim.strip()
            # Filter out very short or non-claim phrases
            if len(claim) > 10 and any(keyword in claim.lower() for keyword in 
                ["i", "my", "our", "we", "led", "built", "created", "improved", "reduced", "increased"]):
                cleaned_claims.append(claim)
        
        return cleaned_claims
    
    def score_single_claim(self, claim: str, rag_sources: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
        """Score confidence of a single claim"""
        base_score = self.per_claim_scoring.get("base_score", 1.0)
        deductions = self.per_claim_scoring.get("deductions", [])
        
        current_score = base_score
        applied_deductions = []
        
        # Apply deductions based on evidence
        for deduction in deductions:
            condition = deduction.get("condition", "")
            penalty = deduction.get("penalty", 0)
            
            if self._evaluate_condition(condition, claim, rag_sources):
                current_score += penalty
                applied_deductions.append({
                    "condition": condition,
                    "penalty": penalty,
                    "reason": self._get_deduction_reason(condition)
                })
        
        # Ensure score doesn't go below 0
        final_score = max(0.0, current_score)
        
        return final_score, {
            "base_score": base_score,
            "applied_deductions": applied_deductions,
            "final_score": final_score,
            "meets_minimum": final_score >= self.per_claim_minimum
        }
    
    def _evaluate_condition(self, condition: str, claim: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Evaluate if a deduction condition applies"""
        claim_lower = claim.lower()
        
        if "No RAG source found" in condition:
            return not self._claim_in_rag_sources(claim, rag_sources)
        
        elif "Metric has no source mapping" in condition:
            return self._has_unsourced_metric(claim, rag_sources)
        
        elif "Company not in whitelist" in condition:
            return self._has_unauthorized_company(claim, rag_sources)
        
        elif "Role terminology drifted" in condition:
            return self._has_role_drift(claim, rag_sources)
        
        elif "Context coherence" in condition:
            return self._has_low_coherence(claim, rag_sources)
        
        return False
    
    def _claim_in_rag_sources(self, claim: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Check if claim is supported by RAG sources"""
        claim_words = set(claim.lower().split())
        
        for source in rag_sources:
            content = source.get("content", "").lower()
            content_words = set(content.split())
            
            # Simple word overlap check
            overlap = len(claim_words & content_words)
            if overlap >= len(claim_words) * 0.5:  # At least 50% word overlap
                return True
        
        return False
    
    def _has_unsourced_metric(self, claim: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Check if claim has metrics without source mapping"""
        # Extract metrics from claim
        metric_pattern = r'(\d+%|\d+x|\d+\.?\d*\s*(?:million|billion|thousand))'
        metrics_in_claim = re.findall(metric_pattern, claim, re.IGNORECASE)
        
        if not metrics_in_claim:
            return False
        
        # Check if metrics are found in sources
        for metric in metrics_in_claim:
            metric_found = False
            for source in rag_sources:
                if metric.lower() in source.get("content", "").lower():
                    metric_found = True
                    break
            
            if not metric_found:
                return True
        
        return False
    
    def _has_unauthorized_company(self, claim: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Check if claim mentions unauthorized companies"""
        # Extract company names (simplified)
        company_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|LLC|Ltd|Co))?\b'
        companies_in_claim = re.findall(company_pattern, claim)
        
        # Check against authorized companies in sources
        authorized_companies = set()
        for source in rag_sources:
            content = source.get("content", "")
            authorized_companies.update(re.findall(company_pattern, content))
        
        for company in companies_in_claim:
            if company not in authorized_companies:
                return True
        
        return False
    
    def _has_role_drift(self, claim: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Check for role terminology drift"""
        # This is a simplified implementation
        # In practice, would use semantic similarity
        role_keywords = ["engineer", "developer", "manager", "director", "lead", "architect"]
        claim_roles = [kw for kw in role_keywords if kw in claim.lower()]
        
        if not claim_roles:
            return False
        
        # Check if these roles appear in sources
        for role in claim_roles:
            role_found = False
            for source in rag_sources:
                if role in source.get("content", "").lower():
                    role_found = True
                    break
            
            if not role_found:
                return True
        
        return False
    
    def _has_low_coherence(self, claim: str, rag_sources: List[Dict[str, Any]]) -> bool:
        """Check for low context coherence"""
        # Simplified coherence check based on word overlap
        claim_words = set(claim.lower().split())
        
        max_overlap = 0.0
        for source in rag_sources:
            content_words = set(source.get("content", "").lower().split())
            
            if claim_words and content_words:
                overlap = len(claim_words & content_words) / len(claim_words | content_words)
                max_overlap = max(max_overlap, overlap)
        
        return max_overlap < 0.8
    
    def _get_deduction_reason(self, condition: str) -> str:
        """Get human-readable reason for deduction"""
        reason_map = {
            "No RAG source found": "Claim not supported by research sources",
            "Metric has no source mapping": "Metric without verifiable source",
            "Company not in whitelist": "Unauthorized company mentioned",
            "Role terminology drifted": "Role description doesn't match sources",
            "Context coherence": "Claim lacks contextual coherence"
        }
        
        for key, reason in reason_map.items():
            if key in condition:
                return reason
        
        return "Deduction condition met"
    
    def calculate_aggregate_confidence(self, claim_scores: List[float]) -> Tuple[float, Dict[str, Any]]:
        """Calculate aggregate confidence from individual claim scores"""
        if not claim_scores:
            return 0.0, {"error": "No claim scores provided"}
        
        aggregate_score = sum(claim_scores) / len(claim_scores)
        
        # Additional statistics
        min_score = min(claim_scores)
        max_score = max(claim_scores)
        below_threshold = sum(1 for score in claim_scores if score < self.per_claim_minimum)
        
        return aggregate_score, {
            "individual_scores": claim_scores,
            "min_score": min_score,
            "max_score": max_score,
            "claims_below_threshold": below_threshold,
            "total_claims": len(claim_scores),
            "meets_aggregate_minimum": aggregate_score >= self.aggregate_minimum,
            "aggregate_minimum": self.aggregate_minimum,
            "per_claim_minimum": self.per_claim_minimum
        }
    
    def validate_claim_confidence(self, aggregate_score: float, breakdown: Dict[str, Any]) -> List[ValidationResult]:
        """Validate claim confidence against thresholds"""
        validation_results = []
        
        # Check aggregate threshold
        if aggregate_score < self.aggregate_minimum:
            validation_results.append(ValidationResult(
                rule_id="CLAIM_CONFIDENCE_BELOW_AGGREGATE_THRESHOLD",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Aggregate claim confidence {aggregate_score:.3f} below threshold {self.aggregate_minimum}",
                details={
                    "aggregate_score": aggregate_score,
                    "threshold": self.aggregate_minimum,
                    "claims_below_threshold": breakdown.get("claims_below_threshold", 0)
                }
            ))
        
        # Check individual claim thresholds
        below_threshold = breakdown.get("claims_below_threshold", 0)
        if below_threshold > 0:
            validation_results.append(ValidationResult(
                rule_id="INDIVIDUAL_CLAIMS_BELOW_THRESHOLD",
                passed=False,
                severity=ValidationSeverity.HIGH,
                message=f"{below_threshold} claims below minimum threshold {self.per_claim_minimum}",
                details={
                    "below_threshold_count": below_threshold,
                    "total_claims": breakdown.get("total_claims", 0),
                    "minimum_threshold": self.per_claim_minimum
                }
            ))
        
        return validation_results


class InsightsEngine:
    """Main insights engine - Lift & Shift + Enhanced from LIC"""
    
    def __init__(self, lic_capabilities: Dict[str, Any]):
        self.insight_patterns = lic_capabilities.get("insight_patterns", {})
        self.signal_scorer = SignalQualityScorer(self.insight_patterns)
        self.claim_scorer = ClaimConfidenceScorer(self.insight_patterns)
    
    def analyze_message_quality(
        self,
        message_body: str,
        rag_evidence: List[RAGEvidence],
        rag_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive message quality analysis"""
        results = {}
        
        # Signal quality analysis
        signal_score, signal_breakdown = self.signal_scorer.calculate_signal_quality(rag_evidence)
        signal_validations = self.signal_scorer.validate_signal_quality(signal_score, signal_breakdown)
        
        results["signal_quality"] = {
            "score": signal_score,
            "breakdown": signal_breakdown,
            "validations": signal_validations
        }
        
        # Claim confidence analysis
        claims = self.claim_scorer.extract_claims(message_body)
        claim_scores = []
        claim_details = []
        
        for claim in claims:
            score, detail = self.claim_scorer.score_single_claim(claim, rag_sources)
            claim_scores.append(score)
            claim_details.append({
                "claim": claim,
                "score": score,
                "detail": detail
            })
        
        aggregate_confidence, confidence_breakdown = self.claim_scorer.calculate_aggregate_confidence(claim_scores)
        claim_validations = self.claim_scorer.validate_claim_confidence(aggregate_confidence, confidence_breakdown)
        
        results["claim_confidence"] = {
            "aggregate_score": aggregate_confidence,
            "breakdown": confidence_breakdown,
            "validations": claim_validations,
            "individual_claims": claim_details
        }
        
        # Overall quality assessment
        overall_validations = signal_validations + claim_validations
        critical_issues = [v for v in overall_validations if v.severity == ValidationSeverity.CRITICAL]
        
        results["overall_quality"] = {
            "can_proceed": len(critical_issues) == 0,
            "total_validations": len(overall_validations),
            "critical_issues": len(critical_issues),
            "high_issues": len([v for v in overall_validations if v.severity == ValidationSeverity.HIGH]),
            "medium_issues": len([v for v in overall_validations if v.severity == ValidationSeverity.MEDIUM]),
            "low_issues": len([v for v in overall_validations if v.severity == ValidationSeverity.LOW])
        }
        
        return results
    
    def get_insights_summary(self) -> Dict[str, Any]:
        """Get summary of insights configuration"""
        return {
            "signal_quality": {
                "source_weights": self.signal_scorer.source_weights,
                "minimum_threshold": self.signal_scorer.minimum_signal_threshold
            },
            "claim_confidence": {
                "per_claim_minimum": self.claim_scorer.per_claim_minimum,
                "aggregate_minimum": self.claim_scorer.aggregate_minimum,
                "claim_splitters": self.claim_scorer.claim_extraction.get("splitters", [])
            }
        }
