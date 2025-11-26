"""
LIC-specific RAG policies and constraints.

Defines LIC-specific RAG constraints including source priorities,
temporal windows, vector search vs KG blending weights, and
filters for outreach domains. No actual hit logic - just constants
and small rule functions.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class RAGSearchMode(str, Enum):
    """RAG search modes for LIC operations."""
    VECTOR_ONLY = "vector_only"
    KG_ONLY = "kg_only"
    HYBRID = "hybrid"
    TEMPORAL = "temporal"


@dataclass
class RAGPolicy:
    """LIC-specific RAG policy configuration."""
    
    # Search Configuration
    enable_vector_search: bool = True
    enable_hybrid_search: bool = True
    enable_kg_search: bool = True
    search_mode: RAGSearchMode = RAGSearchMode.HYBRID
    
    # Result Limits
    default_max_results: int = 10
    max_vector_results: int = 5
    max_kg_results: int = 5
    max_hybrid_results: int = 8
    
    # Quality Filters
    confidence_threshold: float = 0.7
    similarity_threshold: float = 0.6
    recency_days: Optional[int] = None
    
    # Source Priorities (lower number = higher priority)
    source_priorities: Dict[str, int] = None
    source_weights: Dict[str, float] = None
    
    # Temporal Configuration
    default_temporal_window: int = 365
    enable_temporal_kg: bool = True
    temporal_boost_factor: float = 1.2
    
    # Domain Filtering
    outreach_domains: List[str] = None
    blocked_sources: List[str] = None
    required_source_types: List[str] = None
    
    # Blending Configuration
    vector_weight: float = 0.6
    kg_weight: float = 0.4
    hybrid_weight: float = 0.8
    
    def __post_init__(self):
        """Initialize defaults for complex fields."""
        if self.source_priorities is None:
            self.source_priorities = {
                "company_kg": 1,
                "executive_insights": 2,
                "industry_reports": 3,
                "news_articles": 4,
                "web_search": 5,
                "social_media": 6
            }
        
        if self.source_weights is None:
            self.source_weights = {
                "vector": self.vector_weight,
                "kg": self.kg_weight,
                "hybrid": self.hybrid_weight
            }
        
        if self.outreach_domains is None:
            self.outreach_domains = [
                "technology", "healthcare", "finance", "manufacturing",
                "consulting", "education", "government", "nonprofit"
            ]
        
        if self.blocked_sources is None:
            self.blocked_sources = [
                "social_media_rumors", "unverified_blogs", "spam_sources"
            ]
        
        if self.required_source_types is None:
            self.required_source_types = [
                "company_data", "industry_analysis", "market_intelligence"
            ]


# Default LIC Policy
DEFAULT_LIC_RAG_POLICY = RAGPolicy()


# Named Policies for Different Use Cases
def get_rag_policy(policy_name: Optional[str] = None) -> RAGPolicy:
    """Get RAG policy by name."""
    if policy_name is None:
        return DEFAULT_LIC_RAG_POLICY
    
    policies = {
        "conservative": RAGPolicy(
            confidence_threshold=0.8,
            enable_kg_search=True,
            enable_hybrid_search=False,
            source_priorities={
                "company_kg": 1,
                "executive_insights": 2,
                "industry_reports": 3,
                "verified_news": 4
            },
            blocked_sources=["social_media", "web_search", "forums"]
        ),
        
        "comprehensive": RAGPolicy(
            default_max_results=20,
            max_vector_results=8,
            max_kg_results=8,
            max_hybrid_results=12,
            confidence_threshold=0.5,
            enable_temporal_kg=True,
            temporal_boost_factor=1.5
        ),
        
        "real_time": RAGPolicy(
            recency_days=30,
            default_temporal_window=90,
            enable_temporal_kg=True,
            temporal_boost_factor=2.0,
            source_priorities={
                "news_articles": 1,
                "social_media": 2,
                "company_kg": 3,
                "executive_insights": 4
            }
        ),
        
        "research": RAGPolicy(
            default_max_results=30,
            confidence_threshold=0.4,
            enable_hybrid_search=True,
            enable_temporal_kg=True,
            recency_days=None,  # No recency limit for research
            source_weights={
                "vector": 0.4,
                "kg": 0.6,
                "hybrid": 0.7
            }
        )
    }
    
    return policies.get(policy_name, DEFAULT_LIC_RAG_POLICY)


# Policy Helper Functions
def create_custom_rag_policy(**kwargs) -> RAGPolicy:
    """Create custom RAG policy with overrides."""
    return RAGPolicy(**kwargs)


def validate_rag_policy(policy: RAGPolicy) -> List[str]:
    """Validate RAG policy configuration."""
    issues = []
    
    # Check weight sum
    total_weight = sum(policy.source_weights.values())
    if abs(total_weight - 1.0) > 0.1:
        issues.append(f"Source weights sum to {total_weight}, should be ~1.0")
    
    # Check thresholds
    if policy.confidence_threshold < 0 or policy.confidence_threshold > 1:
        issues.append("Confidence threshold must be between 0 and 1")
    
    if policy.similarity_threshold < 0 or policy.similarity_threshold > 1:
        issues.append("Similarity threshold must be between 0 and 1")
    
    # Check result limits
    if policy.default_max_results < 1:
        issues.append("Default max results must be positive")
    
    return issues


# Domain-specific policy functions
def get_outreach_domain_policy(domain: str) -> RAGPolicy:
    """Get policy optimized for specific outreach domain."""
    domain_configs = {
        "technology": RAGPolicy(
            source_priorities={
                "company_kg": 1,
                "tech_blogs": 2,
                "github_data": 3,
                "industry_reports": 4
            },
            recency_days=180
        ),
        
        "healthcare": RAGPolicy(
            confidence_threshold=0.9,
            source_priorities={
                "medical_journals": 1,
                "clinical_trials": 2,
                "regulatory_data": 3,
                "company_kg": 4
            },
            blocked_sources=["social_media", "forums"]
        ),
        
        "finance": RAGPolicy(
            confidence_threshold=0.85,
            source_priorities={
                "sec_filings": 1,
                "financial_reports": 2,
                "market_data": 3,
                "company_kg": 4
            },
            recency_days=90
        )
    }
    
    return domain_configs.get(domain, DEFAULT_LIC_RAG_POLICY)
