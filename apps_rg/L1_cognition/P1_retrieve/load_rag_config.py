
# Ownership: apps_rg / L1_cognition
# -*- coding: utf-8 -*-
"""RAG configuration for resume generation."""

from typing import Dict

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
    cache_dir: str = "/staging/jd_cache"
    cache_ttl_days: int = 30
    telemetry_enabled: bool = True
    telemetry_log_dir: str = "/staging/rag_telemetry"
    source_weights: Dict[str, float] = field(default_factory=lambda: {
        "SOURCE_JD": 1.8, "SOURCE_COMPANY_BLOG": 1.5, "SOURCE_TARGET_EMPLOYEE": 1.4,
        "SOURCE_GARTNER_MQ": 1.2, "SOURCE_PEER_JD": 0.8, "SOURCE_GENERIC_PROFILE": 0.5,
        "LOCAL_NLP": 0.2,
    })
