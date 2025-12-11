"""
pick_best_result.py - Shared Execution Module.

This module provides the core implementation for PickBestResult, handling
standardized execution flows, error management, and context propagation
within the shared application layer.
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Standardized operation result container."""
    success: bool
    data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class PickBestResult:
    """
    Executor for shared pick_best_result operations.
    
    Ensures consistent handling of configuration context and error boundaries
    across the sovereign domain.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def process(self, payload: Union[str, int, float, bool, list, dict], context: Optional[Dict] = None) -> ExecutionResult:
        """
        Execute the primary logic for this module.
        
        Args:
            payload: The input data to process
            context: Optional execution context
            
        Returns:
            ExecutionResult indicating success or failure
        """
        try:
            self._logger.info("Starting processing execution")
            result = self._execute_logic(payload, context)
            return ExecutionResult(success=True, data=result)
        except (ValueError, TypeError, KeyError) as e:
            self._logger.error(f"Validation error during processing: {e}")
            return ExecutionResult(success=False, error_message=str(e))
        except Exception as e:
            self._logger.error(f"Unexpected system error: {e}", exc_info=True)
            return ExecutionResult(success=False, error_message="Internal System Error")

    def _execute_logic(self, data: Union[str, int, float, bool, list, dict], context: Optional[Dict]) -> Union[str, int, float, bool, list, dict]:
        """Internal logic for picking the best result from multiple options."""
        # Initialize result
        result = {
            "best_result": None,
            "scoring_method": self.config.get("scoring_method", "weighted"),
            "all_scores": [],
            "selection_rationale": {},
            "confidence": 0.0,
            "alternatives": []
        }
        
        # Handle different input types
        if isinstance(data, list):
            # Multiple results to evaluate
            scored_results = self._score_multiple_results(data, context)
        elif isinstance(data, dict):
            # Single result or already scored results
            if "results" in data:
                scored_results = self._score_multiple_results(data["results"], context)
            else:
                scored_results = [{"result": data, "score": 0.5, "reasoning": "Single result provided"}]
        else:
            # Single value
            scored_results = [{"result": data, "score": 0.5, "reasoning": "Single value"}]
        
        # Sort by score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Select best result
        if scored_results:
            best = scored_results[0]
            result["best_result"] = best["result"]
            result["confidence"] = best["score"]
            result["selection_rationale"] = {
                "selected_score": best["score"],
                "reasoning": best.get("reasoning", "Highest score"),
                "total_evaluated": len(scored_results),
                "score_distribution": self._calculate_score_distribution(scored_results)
            }
            
            # Store all scores
            result["all_scores"] = [
                {"score": item["score"], "index": idx}
                for idx, item in enumerate(scored_results)
            ]
            
            # Add alternatives
            result["alternatives"] = [
                {"result": item["result"], "score": item["score"], "rank": idx + 1}
                for idx, item in enumerate(scored_results[1:4])  # Top 3 alternatives
            ]
        
        return result
    
    def _score_multiple_results(self, results: list, context: Optional[Dict]) -> list:
        """Score multiple results based on various criteria."""
        scored = []
        
        for idx, result in enumerate(results):
            score = 0.0
            reasoning = []
            
            # Base scoring
            if isinstance(result, dict):
                # Check for explicit score
                if "score" in result:
                    score = float(result["score"]) * 0.5
                    reasoning.append(f"Explicit score: {result['score']}")
                
                # Check for relevance
                if "relevance" in result:
                    score += float(result["relevance"]) * 0.3
                    reasoning.append(f"Relevance: {result['relevance']}")
                
                # Check for confidence
                if "confidence" in result:
                    score += float(result["confidence"]) * 0.2
                    reasoning.append(f"Confidence: {result['confidence']}")
                
                # Content-based scoring
                content_score = self._score_content(result)
                score += content_score * 0.3
                if content_score > 0:
                    reasoning.append(f"Content quality: {content_score:.2f}")
                
            elif isinstance(result, str):
                # String-based scoring
                score = self._score_string(result)
                reasoning.append(f"String quality: {score:.2f}")
            
            else:
                # Generic scoring
                score = 0.5
                reasoning.append("Generic result type")
            
            # Context-based adjustments
            if context:
                context_boost = self._calculate_context_boost(result, context)
                score += context_boost
                if context_boost > 0:
                    reasoning.append(f"Context boost: {context_boost:.2f}")
            
            # Normalize score
            score = min(1.0, max(0.0, score))
            
            scored.append({
                "result": result,
                "score": score,
                "reasoning": "; ".join(reasoning),
                "original_index": idx
            })
        
        return scored
    
    def _score_content(self, result: dict) -> float:
        """Score content based on various factors."""
        score = 0.0
        
        # Check for completeness
        required_fields = self.config.get("required_fields", [])
        if required_fields:
            present_fields = sum(1 for field in required_fields if field in result)
            score += (present_fields / len(required_fields)) * 0.3
        
        # Check for data richness
        field_count = len(result)
        if field_count > 5:
            score += 0.2
        elif field_count > 10:
            score += 0.3
        
        # Check for nested data
        if any(isinstance(value, (dict, list)) for value in result.values()):
            score += 0.2
        
        return score
    
    def _score_string(self, text: str) -> float:
        """Score string based on quality metrics."""
        score = 0.5  # Base score
        
        # Length scoring
        if 10 < len(text) < 100:
            score += 0.2
        elif 100 <= len(text) < 500:
            score += 0.3
        elif len(text) >= 500:
            score += 0.1  # Too long might be less relevant
        
        # Content indicators
        if any(indicator in text.lower() for indicator in ["important", "key", "critical"]):
            score += 0.1
        
        # Penalize empty or very short strings
        if len(text) < 5:
            score = 0.1
        
        return score
    
    def _calculate_context_boost(self, result: Any, context: Dict) -> float:
        """Calculate score boost based on context relevance."""
        boost = 0.0
        
        # Check for matching keywords
        if "keywords" in context:
            result_str = str(result).lower()
            matches = sum(1 for kw in context["keywords"] if kw.lower() in result_str)
            boost += matches * 0.1
        
        # Check for preferred type
        if "preferred_type" in context:
            if isinstance(result, context["preferred_type"]):
                boost += 0.2
        
        # Check for domain relevance
        if "domain" in context:
            if self._is_domain_relevant(result, context["domain"]):
                boost += 0.15
        
        return min(0.5, boost)  # Cap the boost
    
    def _is_domain_relevant(self, result: Any, domain: str) -> bool:
        """Check if result is relevant to the specified domain."""
        if not isinstance(result, dict):
            return False
        
        domain_keywords = {
            "user": ["user", "customer", "client", "account"],
            "product": ["product", "item", "inventory", "catalog"],
            "order": ["order", "purchase", "transaction", "sale"],
            "analytics": ["metric", "analytics", "report", "statistic"]
        }
        
        keywords = domain_keywords.get(domain, [])
        result_str = str(result).lower()
        
        return any(kw in result_str for kw in keywords)
    
    def _calculate_score_distribution(self, scored_results: list) -> dict:
        """Calculate distribution statistics for scores."""
        scores = [item["score"] for item in scored_results]
        
        if not scores:
            return {}
        
        return {
            "mean": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores),
            "median": sorted(scores)[len(scores) // 2],
            "std_dev": self._calculate_std_dev(scores)
        }
    
    def _calculate_std_dev(self, values: list) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

def run_process(data: Union[str, int, float, bool, list, dict]) -> ExecutionResult:
    """Module-level entry point."""
    executor = PickBestResult()
    return executor.process(data)
