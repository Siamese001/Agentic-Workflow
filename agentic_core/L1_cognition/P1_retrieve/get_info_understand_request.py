"""
get_info_understand_request.py - Shared Execution Module.

This module provides the core implementation for GetInfoUnderstandRequest, handling
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

class GetInfoUnderstandRequest:
    """
    Executor for shared get_info_understand_request operations.
    
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
        """Internal logic for understanding information requests."""
        # Initialize result
        result = {
            "request_understanding": {},
            "extracted_info": {},
            "query_analysis": {},
            "context_insights": {},
            "recommendations": []
        }
        
        # Parse the request
        if isinstance(data, dict):
            request = data
        elif isinstance(data, str):
            request = {"query": data, "type": "text_query"}
        else:
            request = {"query": str(data), "type": "unknown"}
        
        # Analyze the request
        query = request.get("query", "")
        request_type = request.get("type", "unknown")
        
        # Extract key information
        result["extracted_info"] = {
            "query": query,
            "type": request_type,
            "keywords": self._extract_keywords(query),
            "entities": self._extract_entities(query),
            "intent": self._determine_intent(query)
        }
        
        # Analyze query structure
        result["query_analysis"] = {
            "query_length": len(query),
            "word_count": len(query.split()),
            "has_question_words": self._has_question_words(query),
            "query_complexity": self._assess_complexity(query),
            "information_type": self._classify_information_type(query)
        }
        
        # Generate context insights
        if context:
            result["context_insights"] = {
                "has_context": True,
                "context_keys": list(context.keys()),
                "context_relevance": self._assess_context_relevance(query, context),
                "suggested_filters": self._suggest_filters(query, context)
            }
        else:
            result["context_insights"] = {
                "has_context": False,
                "message": "No context provided for enhanced understanding"
            }
        
        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(query, context)
        
        # Overall understanding
        result["request_understanding"] = {
            "primary_intent": result["extracted_info"]["intent"],
            "information_needed": result["query_analysis"]["information_type"],
            "confidence": self._calculate_understanding_confidence(query, context),
            "processing_strategy": self._determine_processing_strategy(query, request_type)
        }
        
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Simple keyword extraction
        import re
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "what", "when", "where", "who", "why", "how"}
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return unique keywords
        return list(set(keywords))[:10]  # Limit to top 10
    
    def _extract_entities(self, query: str) -> List[Dict]:
        """Extract entities from query."""
        entities = []
        
        # Simple pattern matching for common entities
        import re
        
        # Email pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
        for email in emails:
            entities.append({"type": "email", "value": email})
        
        # Number patterns
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', query)
        for number in numbers:
            entities.append({"type": "number", "value": number})
        
        # Date patterns
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', query)
        for date in dates:
            entities.append({"type": "date", "value": date})
        
        return entities
    
    def _determine_intent(self, query: str) -> str:
        """Determine the primary intent of the query."""
        query_lower = query.lower()
        
        # Check for different intents
        if any(word in query_lower for word in ["what", "define", "explain", "describe"]):
            return "information_seeking"
        elif any(word in query_lower for word in ["how", "tutorial", "guide", "steps"]):
            return "procedural"
        elif any(word in query_lower for word in ["find", "search", "locate", "where"]):
            return "search"
        elif any(word in query_lower for word in ["compare", "difference", "versus", "vs"]):
            return "comparison"
        elif any(word in query_lower for word in ["why", "reason", "cause"]):
            return "explanation"
        elif any(word in query_lower for word in ["list", "show", "display"]):
            return "enumeration"
        else:
            return "general_query"
    
    def _has_question_words(self, query: str) -> bool:
        """Check if query contains question words."""
        question_words = ["what", "when", "where", "who", "why", "how", "which", "whose", "whom"]
        return any(word in query.lower() for word in question_words)
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        word_count = len(query.split())
        
        if word_count <= 3:
            return "simple"
        elif word_count <= 10:
            return "moderate"
        elif word_count <= 20:
            return "complex"
        else:
            return "very_complex"
    
    def _classify_information_type(self, query: str) -> str:
        """Classify the type of information being requested."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["person", "people", "who", "name"]):
            return "person_information"
        elif any(word in query_lower for word in ["place", "location", "where", "address"]):
            return "location_information"
        elif any(word in query_lower for word in ["time", "when", "date", "schedule"]):
            return "temporal_information"
        elif any(word in query_lower for word in ["amount", "price", "cost", "how much", "how many"]):
            return "quantitative_information"
        elif any(word in query_lower for word in ["process", "how to", "steps", "procedure"]):
            return "procedural_information"
        elif any(word in query_lower for word in ["reason", "why", "cause", "explanation"]):
            return "causal_information"
        else:
            return "general_information"
    
    def _assess_context_relevance(self, query: str, context: Dict) -> float:
        """Assess how relevant the context is to the query."""
        if not context:
            return 0.0
        
        relevance_score = 0.0
        query_words = set(query.lower().split())
        
        # Check context values for matching words
        for key, value in context.items():
            if isinstance(value, str):
                context_words = set(value.lower().split())
                overlap = len(query_words.intersection(context_words))
                relevance_score += overlap * 0.1
        
        return min(1.0, relevance_score)
    
    def _suggest_filters(self, query: str, context: Dict) -> List[str]:
        """Suggest filters based on query and context."""
        filters = []
        query_lower = query.lower()
        
        if "recent" in query_lower or "latest" in query_lower:
            filters.append("time_filter:recent")
        if "important" in query_lower or "priority" in query_lower:
            filters.append("priority_filter:high")
        if context and "user_id" in context:
            filters.append("user_filter:context_user")
        
        return filters
    
    def _generate_recommendations(self, query: str, context: Optional[Dict]) -> List[str]:
        """Generate recommendations for processing the query."""
        recommendations = []
        
        # Based on query complexity
        if len(query.split()) > 15:
            recommendations.append("Consider breaking down complex query into smaller parts")
        
        # Based on intent
        intent = self._determine_intent(query)
        if intent == "search":
            recommendations.append("Use indexed search for faster results")
        elif intent == "comparison":
            recommendations.append("Prepare side-by-side comparison format")
        
        # Based on context availability
        if not context:
            recommendations.append("Consider providing context for more accurate results")
        
        return recommendations
    
    def _calculate_understanding_confidence(self, query: str, context: Optional[Dict]) -> float:
        """Calculate confidence score for query understanding."""
        confidence = 0.5  # Base confidence
        
        # Increase based on query clarity
        if self._has_question_words(query):
            confidence += 0.2
        
        # Increase based on context availability
        if context:
            confidence += 0.2
        
        # Increase based on query length (reasonable range)
        word_count = len(query.split())
        if 5 <= word_count <= 20:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _determine_processing_strategy(self, query: str, request_type: str) -> str:
        """Determine the best processing strategy for the request."""
        intent = self._determine_intent(query)
        complexity = self._assess_complexity(query)
        
        if intent == "search" and complexity in ["simple", "moderate"]:
            return "direct_search"
        elif intent == "information_seeking":
            return "knowledge_retrieval"
        elif complexity in ["complex", "very_complex"]:
            return "multi_step_processing"
        elif request_type == "text_query":
            return "nlp_processing"
        else:
            return "standard_processing"

def run_process(data: Union[str, int, float, bool, list, dict]) -> ExecutionResult:
    """Module-level entry point."""
    executor = GetInfoUnderstandRequest()
    return executor.process(data)
