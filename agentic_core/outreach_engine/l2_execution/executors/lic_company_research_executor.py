"""Company research executor for outreach campaigns."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CompanySearchConfig:
    """Configuration for company search operations."""
    search_depth: str = "standard"
    include_financials: bool = False
    include_news: bool = True
    max_results: int = 10
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompanyResearchResult:
    """Result from company research operations."""
    company_name: str = ""
    domain: str = ""
    size: str = ""
    industry: str = ""
    description: str = ""
    key_findings: List[str] = field(default_factory=list)
    confidence: float = 0.8
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

# KG fallback archetypes for company research
KG_FALLBACK_ARCHETYPES = {
    "technology": {
        "default_archetype": "SENIOR_TA",
        "fallback_reasoning": "technical_focus",
        "confidence_adjustment": 0.9
    },
    "finance": {
        "default_archetype": "EXECUTIVE",
        "fallback_reasoning": "business_focus",
        "confidence_adjustment": 0.8
    },
    "healthcare": {
        "default_archetype": "SENIOR_TA",
        "fallback_reasoning": "specialized_technical",
        "confidence_adjustment": 0.85
    },
    "consulting": {
        "default_archetype": "EXECUTIVE",
        "fallback_reasoning": "strategic_focus",
        "confidence_adjustment": 0.8
    }
}

class CompanyResearchExecutor:
    """Company research execution engine."""

    def __init__(self, config: Optional[CompanySearchConfig] = None):
        self.config = config or CompanySearchConfig()
        self.research_sources = ["linkedin", "company_website", "news_articles"]

    def execute_research(self, company_name: str, domain: str = None) -> CompanyResearchResult:
        """Execute company research and return results."""
        # Mock implementation
        return CompanyResearchResult(
            company_name=company_name,
            domain=domain or f"{company_name.lower().replace(' ', '')}.com",
            size="1000-5000",
            industry="Technology",
            description="Leading technology company specializing in innovative solutions",
            key_findings=[
                "Established player in technology sector",
                "Focus on innovation and growth",
                "Strong market presence"
            ],
            confidence=0.8,
            sources=["company_website", "linkedin", "industry_reports"],
            metadata={"search_depth": self.config.search_depth}
        )

    def get_kg_fallback_archetype(self, industry: str) -> Dict[str, Any]:
        """Get KG fallback archetype for given industry."""
        return KG_FALLBACK_ARCHETYPES.get(industry.lower(), {
            "default_archetype": "RECRUITER",
            "fallback_reasoning": "general_fallback",
            "confidence_adjustment": 0.7
        })

    def refine_search(self, initial_result: CompanyResearchResult, feedback: Dict[str, Any]) -> CompanyResearchResult:
        """Refine company research based on feedback."""
        refined = CompanyResearchResult(
            company_name=initial_result.company_name,
            domain=initial_result.domain,
            size=feedback.get("size", initial_result.size),
            industry=feedback.get("industry", initial_result.industry),
            description=initial_result.description,
            key_findings=initial_result.key_findings + feedback.get("additional_findings", []),
            confidence=min(1.0, initial_result.confidence + 0.1),
            sources=initial_result.sources,
            metadata={**initial_result.metadata, "refined": True}
        )
        return refined
