#!/usr/bin/env python3
"""
Arbitration Engine
Section 6: Orchestration - Critic/verifier/arbiter logic for agentic workflows
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ArbitrationEngine:
    """Critic/verifier/arbiter logic for agentic workflow decisions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.max_arbitration_rounds = self.config.get("max_arbitration_rounds", 3)
        self.arbitration_strategy = self.config.get("arbitration_strategy", "consensus")
    
    def arbitrate_decision(self, proposals: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Arbitrate between multiple proposals to reach consensus"""
        try:
            if not proposals:
                return {"decision": None, "reason": "No proposals provided", "confidence": 0.0}
            
            # Evaluate each proposal
            evaluated_proposals = []
            for proposal in proposals:
                evaluation = self._evaluate_proposal(proposal, context)
                evaluated_proposals.append({
                    "proposal": proposal,
                    "evaluation": evaluation,
                    "confidence": evaluation.get("confidence", 0.0)
                })
            
            # Select best proposal based on strategy
            if self.arbitration_strategy == "highest_confidence":
                selected = self._select_highest_confidence(evaluated_proposals)
            elif self.arbitration_strategy == "consensus":
                selected = self._select_consensus(evaluated_proposals)
            else:
                selected = self._select_weighted(evaluated_proposals)
            
            result = {
                "decision": selected["proposal"],
                "confidence": selected["confidence"],
                "reasoning": selected["evaluation"].get("reasoning", ""),
                "arbitration_metadata": {
                    "total_proposals": len(proposals),
                    "strategy": self.arbitration_strategy,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            logger.info(f"Arbitration completed: {result['confidence']:.2f} confidence")
            return result
            
        except Exception as e:
            logger.error(f"Arbitration failed: {e}")
            return {"decision": None, "reason": f"Arbitration error: {e}", "confidence": 0.0}
    
    def verify_output(self, output: Any, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Verify output against requirements"""
        try:
            verification_result = {
                "is_valid": True,
                "violations": [],
                "compliance_score": 1.0,
                "details": {}
            }
            
            # Check format requirements
            format_reqs = requirements.get("format", {})
            format_check = self._check_format_requirements(output, format_reqs)
            verification_result["details"]["format"] = format_check
            
            if not format_check["passed"]:
                verification_result["is_valid"] = False
                verification_result["violations"].extend(format_check["violations"])
                verification_result["compliance_score"] -= 0.3
            
            # Check content requirements
            content_reqs = requirements.get("content", {})
            content_check = self._check_content_requirements(output, content_reqs)
            verification_result["details"]["content"] = content_check
            
            if not content_check["passed"]:
                verification_result["is_valid"] = False
                verification_result["violations"].extend(content_check["violations"])
                verification_result["compliance_score"] -= 0.4
            
            # Check quality requirements
            quality_reqs = requirements.get("quality", {})
            quality_check = self._check_quality_requirements(output, quality_reqs)
            verification_result["details"]["quality"] = quality_check
            
            if not quality_check["passed"]:
                verification_result["is_valid"] = False
                verification_result["violations"].extend(quality_check["violations"])
                verification_result["compliance_score"] -= 0.3
            
            # Ensure compliance score doesn't go negative
            verification_result["compliance_score"] = max(0.0, verification_result["compliance_score"])
            
            logger.info(f"Output verification: {'valid' if verification_result['is_valid'] else 'invalid'}")
            return verification_result
            
        except Exception as e:
            logger.error(f"Output verification failed: {e}")
            return {"is_valid": False, "error": str(e), "compliance_score": 0.0}
    
    def critique_proposal(self, proposal: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        """Critique proposal based on specified criteria"""
        try:
            critique_result = {
                "overall_score": 0.0,
                "criteria_scores": {},
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
            
            total_score = 0.0
            valid_criteria = 0
            
            for criterion in criteria:
                score = self._evaluate_criterion(proposal, criterion)
                critique_result["criteria_scores"][criterion] = score
                
                if score >= 0.7:
                    critique_result["strengths"].append(f"Strong {criterion}")
                elif score <= 0.4:
                    critique_result["weaknesses"].append(f"Weak {criterion}")
                    critique_result["suggestions"].append(f"Improve {criterion}")
                
                total_score += score
                valid_criteria += 1
            
            if valid_criteria > 0:
                critique_result["overall_score"] = total_score / valid_criteria
            
            logger.info(f"Proposal critique completed: {critique_result['overall_score']:.2f} overall score")
            return critique_result
            
        except Exception as e:
            logger.error(f"Proposal critique failed: {e}")
            return {"overall_score": 0.0, "error": str(e)}
    
    def _evaluate_proposal(self, proposal: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate individual proposal"""
        try:
            # Base evaluation factors
            relevance_score = self._calculate_relevance(proposal, context)
            feasibility_score = self._calculate_feasibility(proposal, context)
            quality_score = self._calculate_quality(proposal)
            
            # Weighted confidence calculation
            confidence = (relevance_score * 0.4 + feasibility_score * 0.3 + quality_score * 0.3)
            
            reasoning = f"Relevance: {relevance_score:.2f}, Feasibility: {feasibility_score:.2f}, Quality: {quality_score:.2f}"
            
            return {
                "confidence": confidence,
                "reasoning": reasoning,
                "factors": {
                    "relevance": relevance_score,
                    "feasibility": feasibility_score,
                    "quality": quality_score
                }
            }
            
        except Exception as e:
            logger.error(f"Proposal evaluation failed: {e}")
            return {"confidence": 0.0, "reasoning": f"Evaluation error: {e}"}
    
    def _select_highest_confidence(self, evaluated_proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select proposal with highest confidence"""
        return max(evaluated_proposals, key=lambda x: x["confidence"])
    
    def _select_consensus(self, evaluated_proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select proposal based on consensus"""
        if not evaluated_proposals:
            return {"proposal": None, "confidence": 0.0}
        
        # Simple consensus: average confidence above threshold
        avg_confidence = sum(p["confidence"] for p in evaluated_proposals) / len(evaluated_proposals)
        
        if avg_confidence >= self.confidence_threshold:
            # Return highest confidence as consensus representative
            return self._select_highest_confidence(evaluated_proposals)
        else:
            # No consensus, return highest confidence but flag as low consensus
            selected = self._select_highest_confidence(evaluated_proposals)
            selected["evaluation"]["consensus_warning"] = f"Low consensus: {avg_confidence:.2f}"
            return selected
    
    def _select_weighted(self, evaluated_proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select proposal using weighted scoring"""
        for proposal in evaluated_proposals:
            # Apply additional weights based on proposal metadata
            metadata = proposal["proposal"].get("metadata", {})
            priority_weight = metadata.get("priority", 1.0)
            proposal["weighted_confidence"] = proposal["confidence"] * priority_weight
        
        return max(evaluated_proposals, key=lambda x: x.get("weighted_confidence", 0))
    
    def _calculate_relevance(self, proposal: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate relevance score"""
        proposal_keywords = set(str(proposal.get("content", "")).lower().split())
        context_keywords = set(str(context.get("requirements", "")).lower().split())
        
        if not context_keywords:
            return 0.5  # Default relevance
        
        overlap = len(proposal_keywords & context_keywords)
        relevance = overlap / len(context_keywords) if context_keywords else 0.0
        
        return min(1.0, relevance)
    
    def _calculate_feasibility(self, proposal: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate feasibility score"""
        # Simple feasibility based on proposal complexity and constraints
        complexity = proposal.get("complexity", "medium")
        constraints = context.get("constraints", {})
        
        complexity_scores = {"low": 0.9, "medium": 0.7, "high": 0.5}
        base_score = complexity_scores.get(complexity, 0.7)
        
        # Adjust for constraints
        if constraints.get("time_limit"):
            base_score *= 0.8
        
        if constraints.get("resource_limit"):
            base_score *= 0.9
        
        return base_score
    
    def _calculate_quality(self, proposal: Dict[str, Any]) -> float:
        """Calculate quality score"""
        quality_factors = proposal.get("quality_factors", {})
        
        # Default quality factors
        completeness = quality_factors.get("completeness", 0.8)
        accuracy = quality_factors.get("accuracy", 0.8)
        clarity = quality_factors.get("clarity", 0.8)
        
        return (completeness + accuracy + clarity) / 3
    
    def _check_format_requirements(self, output: Any, format_reqs: Dict[str, Any]) -> Dict[str, Any]:
        """Check format requirements"""
        result = {"passed": True, "violations": []}
        
        if format_reqs.get("type") == "json":
            if not isinstance(output, dict):
                result["passed"] = False
                result["violations"].append("Output must be JSON/dict")
        
        if format_reqs.get("max_length"):
            if len(str(output)) > format_reqs["max_length"]:
                result["passed"] = False
                result["violations"].append(f"Output exceeds max length: {format_reqs['max_length']}")
        
        return result
    
    def _check_content_requirements(self, output: Any, content_reqs: Dict[str, Any]) -> Dict[str, Any]:
        """Check content requirements"""
        result = {"passed": True, "violations": []}
        
        required_fields = content_reqs.get("required_fields", [])
        if isinstance(output, dict) and required_fields:
            for field in required_fields:
                if field not in output:
                    result["passed"] = False
                    result["violations"].append(f"Missing required field: {field}")
        
        return result
    
    def _check_quality_requirements(self, output: Any, quality_reqs: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality requirements"""
        result = {"passed": True, "violations": []}
        
        if quality_reqs.get("min_confidence"):
            # Placeholder confidence check
            result["passed"] = True  # Would implement actual confidence calculation
        
        return result
    
    def _evaluate_criterion(self, proposal: Dict[str, Any], criterion: str) -> float:
        """Evaluate proposal against specific criterion"""
        # Simple criterion evaluation (placeholder)
        criterion_scores = {
            "relevance": 0.8,
            "clarity": 0.7,
            "completeness": 0.9,
            "feasibility": 0.6,
            "innovation": 0.7
        }
        
        return criterion_scores.get(criterion, 0.5)

def create_arbitration_engine(config: Optional[Dict[str, Any]] = None) -> ArbitrationEngine:
    """Factory function to create arbitration engine instance"""
    return ArbitrationEngine(config)

# Re-export components
__all__ = [
    'ArbitrationEngine', 'create_arbitration_engine'
]





