# Ownership: apps_rg / L1_cognition
# -*- coding: utf-8 -*-
"""RAG configuration for resume generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RAGConfig:
    """Enhanced configuration for resilient web RAG system."""

    model: str = "gemini-1.5-flash"
    max_tokens: int = 4000
    temperature: float = 0.7
    phase1_min_searches: int = 15
    phase2_min_searches: int = 10
    phase3_min_searches: int = 10
    api_max_retries: int = 7
    api_timeout_seconds: int = 30
    api_initial_backoff_seconds: float = 2.0
    api_max_backoff_seconds: float = 64.0
    api_backoff_multiplier: float = 2.0
    api_backoff_jitter: float = 0.1
    phase_max_retries: int = 3
    phase_timeout_seconds: int = 60
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    cache_dir: str = "/tmp/jd_cache"
    cache_ttl_days: int = 30
    telemetry_enabled: bool = True
    telemetry_log_dir: str = "/tmp/rag_telemetry"
    source_weights: Dict[str, float] = field(default_factory=lambda: {
        "SOURCE_JD": 1.8, "SOURCE_COMPANY_BLOG": 1.5, "SOURCE_TARGET_EMPLOYEE": 1.4,
        "SOURCE_GARTNER_MQ": 1.2, "SOURCE_PEER_JD": 0.8, "SOURCE_GENERIC_PROFILE": 0.5,
        "LOCAL_NLP": 0.2,
    })


@dataclass
class CompetitiveAnalysisConfig:
    """Configuration for competitive analysis phase of RAG."""

    enabled: bool = True
    min_peer_jds: int = 3
    search_pattern: str = '"{role_title}" at "{peer_company}"'
    selection_criteria: List[str] = field(default_factory=lambda: [
        "same_industry", "similar_company_size", "recent_posting_date"
    ])
    table_stakes_threshold: float = 0.8
    differentiator_threshold: float = 0.2


@dataclass
class RAGMission:
    """Defines the mission for the RAG process based on pre-analysis."""

    target_company_name: str
    precise_role_title: str
    key_technologies: List[str]
    core_responsibilities: List[str]
    signal_gap_keywords: List[str]
    signal_overlap_keywords: List[str]


@dataclass
class CompetitiveIntelligence:
    """Stores competitive intelligence insights."""

    peer_jds_analyzed_count: int = 0
    differentiator_keywords: List[str] = field(default_factory=list)
    differentiator_keywords_raw: List[str] = field(default_factory=list)
    differentiator_keywords_weighted: List[Dict] = field(default_factory=list)

    def get_top_differentiators(self, count: int) -> List[str]:
        """Returns the top N differentiator keywords."""
        return self.differentiator_keywords[:count]


@dataclass
class RetrievalSource:
    """Metadata about a data retrieval source."""

    id: str
    type: str
    confidence: float = 0.0
    status: str = "UNKNOWN"
    specific_source: Optional[str] = None
