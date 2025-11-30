# lic_k1_research - K1 research execution engine
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class K1ResearchResult:
    """K1 research execution result"""
    research_data: Dict[str, Any] = None
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.research_data is None:
            self.research_data = {}
        if self.metadata is None:
            self.metadata = {}

class LIC_K1_Research:
    """K1 research execution engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def execute_research(self, query: str, context: Dict[str, Any] = None) -> K1ResearchResult:
        """Execute K1 research query"""
        if context is None:
            context = {}
        
        # Mock research execution
        return K1ResearchResult(
            research_data={
                "query": query,
                "results": ["mock_result_1", "mock_result_2"],
                "sources": ["source_1", "source_2"]
            },
            confidence_score=0.85,
            metadata={"execution_time": 0.5, "model": "mock_k1"}
        )
    
    def run(self, input_data: Dict[str, Any]) -> K1ResearchResult:
        """Run K1 research (alias for execute_research)"""
        query = input_data.get("query", "")
        context = input_data.get("context", {})
        return self.execute_research(query, context)

# Global K1 research instance
_global_k1_research: Optional[LIC_K1_Research] = None

def get_k1_research() -> LIC_K1_Research:
    """Get the global K1 research instance"""
    global _global_k1_research
    if _global_k1_research is None:
        _global_k1_research = LIC_K1_Research()
    return _global_k1_research

def reset_k1_research() -> None:
    """Reset the global K1 research instance (for testing)"""
    global _global_k1_research
    _global_k1_research = None
