"""Research planning implementation for outreach campaigns."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ResearchResult:
    """Result from research operations."""
    query: str = ""
    findings: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    results: Dict[str, Any] = field(default_factory=dict)  # Added for test compatibility
    
    def __post_init__(self):
        # Alias results to findings for backward compatibility
        if self.results and not self.findings:
            self.findings = self.results
        elif self.findings and not self.results:
            self.results = self.findings

@dataclass
class FailureContext:
    """Context for handling research failures."""
    error_type: str = ""
    error_message: str = ""
    retry_count: int = 0
    fallback_strategy: str = "skip"
    metadata: Dict[str, Any] = field(default_factory=dict)

class ResearchRefinementPlanner:
    """Research refinement and planning engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def plan_research(self, query: str, context: Dict[str, Any] = None) -> ResearchResult:
        """Plan research execution based on query and context."""
        return ResearchResult(
            query=query,
            findings={"planned_approach": "comprehensive_search"},
            confidence=0.9,
            sources=["company_research", "individual_analysis"],
            metadata={"context": context or {}}
        )
    
    def refine_query(self, initial_query: str, feedback: Dict[str, Any]) -> str:
        """Refine research query based on feedback."""
        return f"Refined: {initial_query} (based on {feedback})"
    
    def handle_failure(self, error: str, context: Dict[str, Any]) -> FailureContext:
        """Handle research operation failures."""
        return FailureContext(
            error_type="research_failure",
            error_message=error,
            retry_count=0,
            fallback_strategy="use_cached",
            metadata=context
        )
