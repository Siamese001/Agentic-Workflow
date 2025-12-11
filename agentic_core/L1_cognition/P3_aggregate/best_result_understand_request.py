"""
pick_best_result_understand_request.py - Shared Execution Module.

This module provides the core implementation for PickBestResultUnderstandRequest, handling
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

class PickBestResultUnderstandRequest:
    """
    Executor for shared pick_best_result_understand_request operations.
    
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
        """Internal logic for picking the best result based on request understanding."""
        # Initialize result
        result = {
            "best_result": None,
            "understanding": {},
            "confidence": 0.0,
            "alternatives": []
        }
        
        # Handle different data types
        if isinstance(data, list):
            # Pick best from list of results
            result = self._pick_from_list(data, result, context)
        elif isinstance(data, dict):
            # Analyze single result with context
            result = self._analyze_single_result(data, result, context)
        else:
            # Convert to dict format
            result["best_result"] = data
            result["confidence"] = 0.5
            result["understanding"] = {"type": "single_value", "value_type": type(data).__name__}
        
        return result
    
    def _pick_from_list(self, data_list: list, result: dict, context: Optional[Dict]) -> dict:
        """Pick best result from a list of options."""
        if not data_list:
            result["best_result"] = None
            result["confidence"] = 0.0
            result["understanding"]["error"] = "Empty list provided"
            return result
        
        # Score each item
        scored_items = []
        for i, item in enumerate(data_list):
            score = self._score_item(item, context)
            scored_items.append((score, i, item))
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Get best and alternatives
        best_score, best_idx, best_item = scored_items[0]
        result["best_result"] = best_item
        result["confidence"] = best_score
        result["understanding"] = {
            "total_items": len(data_list),
            "best_index": best_idx,
            "selection_criteria": self.config.get("selection_criteria", "relevance_score"),
            "score_distribution": [score for score, _, _ in scored_items[:5]]  # Top 5 scores
        }
        
        # Add top alternatives
        result["alternatives"] = [
            {"item": item, "score": score, "index": idx}
            for score, idx, item in scored_items[1:4]  # Top 3 alternatives
        ]
        
        return result
    
    def _analyze_single_result(self, data: dict, result: dict, context: Optional[Dict]) -> dict:
        """Analyze a single result with context understanding."""
        result["best_result"] = data
        
        # Extract key information
        understanding = {
            "type": "single_result",
            "keys_present": list(data.keys()) if isinstance(data, dict) else [],
            "data_size": len(str(data)) if data else 0
        }
        
        # Check for relevance indicators
        relevance_score = self._calculate_relevance(data, context)
        result["confidence"] = relevance_score
        understanding["relevance_indicators"] = self._get_relevance_indicators(data, context)
        
        result["understanding"] = understanding
        return result
    
    def _score_item(self, item: Any, context: Optional[Dict]) -> float:
        """Score an item based on various criteria."""
        score = 0.0
        
        # Base score on type
        if isinstance(item, dict):
            score += 0.3
            # Check for important keys
            important_keys = self.config.get("important_keys", ["score", "relevance", "confidence"])
            for key in important_keys:
                if key in item:
                    score += 0.2
        elif isinstance(item, str):
            score += 0.2
            # Check string length
            if 10 < len(item) < 500:
                score += 0.1
        elif isinstance(item, (int, float)):
            score += 0.1
        
        # Context-based scoring
        if context:
            context_boost = self._calculate_context_score(item, context)
            score += context_boost
        
        # Normalize to 0-1 range
        return min(1.0, score)
    
    def _calculate_relevance(self, data: dict, context: Optional[Dict]) -> float:
        """Calculate relevance score for data."""
        relevance = 0.5  # Base relevance
        
        # Check for explicit relevance indicators
        if isinstance(data, dict):
            if "relevance" in data:
                relevance = float(data["relevance"])
            elif "score" in data:
                relevance = float(data["score"])
            elif "confidence" in data:
                relevance = float(data["confidence"])
        
        # Adjust based on context
        if context and "query" in context:
            query = context["query"].lower()
            data_str = str(data).lower()
            if query in data_str:
                relevance += 0.2
        
        return min(1.0, relevance)
    
    def _get_relevance_indicators(self, data: dict, context: Optional[Dict]) -> list:
        """Get list of relevance indicators found in data."""
        indicators = []
        
        if isinstance(data, dict):
            # Check for common relevance keys
            relevance_keys = ["relevance", "score", "confidence", "match", "rank"]
            for key in relevance_keys:
                if key in data:
                    indicators.append(f"has_{key}")
        
        # Check context matching
        if context and "query" in context:
            query = context["query"].lower()
            data_str = str(data).lower()
            if any(word in data_str for word in query.split()):
                indicators.append("query_match")
        
        return indicators
    
    def _calculate_context_score(self, item: Any, context: Optional[Dict]) -> float:
        """Calculate context-based score boost."""
        if not context:
            return 0.0
        
        boost = 0.0
        
        # Check for type preference
        preferred_type = context.get("preferred_type")
        if preferred_type and isinstance(item, preferred_type):
            boost += 0.2
        
        # Check for keyword matching
        keywords = context.get("keywords", [])
        if keywords and isinstance(item, str):
            item_lower = item.lower()
            matches = sum(1 for kw in keywords if kw.lower() in item_lower)
            boost += min(0.3, matches * 0.1)
        
        return boost

def run_process(data: Union[str, int, float, bool, list, dict]) -> ExecutionResult:
    """Module-level entry point."""
    executor = PickBestResultUnderstandRequest()
    return executor.process(data)
