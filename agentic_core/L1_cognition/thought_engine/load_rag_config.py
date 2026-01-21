from __future__ import annotations

import logging

'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''

from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)
# Ownership: apps_rg / L1_cognition
# -*- coding: utf-8 -*-
"""RAG configuration for resume generation."""


# [SSOT IMPORT] Structure blueprint is the single source of truth



@dataclass
# NAMING FIXED: RAGConfig → RagConfig
class RagConfig:
    """Enhanced configuration for resilient web RAG system."""

    _model: str = "gemini-1.5-flash"
    _max_tokens: int = 4000
    _temperature: float = 0.7
    _phase1_min_searches: int = 15
    _phase2_min_searches: int = 10
    _phase3_min_searches: int = 10
    _api_max_retries: int = 7
    _api_timeout_seconds: int = 30
    _api_initial_backoff_seconds: float = 2.0
    _api_max_backoff_seconds: float = 64.0
    _api_backoff_multiplier: float = 2.0
    _api_backoff_jitter: float = 0.1
    _phase_max_retries: int = 3
    _phase_timeout_seconds: int = 60
    _circuit_breaker_threshold: int = 5
    _circuit_breaker_timeout: int = 60
    _cache_dir: str = "/staging/jd_cache"
    _cache_ttl_days: int = 30
    _telemetry_enabled: bool = True
    _telemetry_log_dir: str = "/staging/rag_telemetry"
    _source_weights: dict[str, float] = field(
        default_factory=lambda: {
            "SOURCE_JD": 1.8,
            "SOURCE_COMPANY_BLOG": 1.5,
            "SOURCE_TARGET_EMPLOYEE": 1.4,
            "SOURCE_GARTNER_MQ": 1.2,
            "SOURCE_PEER_JD": 0.8,
            "SOURCE_GENERIC_PROFILE": 0.5,
            "LOCAL_NLP": 0.2,
        }
    )
