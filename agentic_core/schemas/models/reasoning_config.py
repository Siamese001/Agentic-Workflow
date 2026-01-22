# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Reasoning configuration for LLM generation.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""


from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar


class ModelProvider(str, Enum):
    """Available model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"


@dataclass
class ModelConfig:
    """Configuration for LLM model parameters."""

    Provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    max_retries: int = 3


@dataclass
class RAGConfig:
    """Configuration for Retrieval-Augmented Generation."""

    enabled: bool = True
    vector_store_path: str = "data/vector_store"
    embedding_model: str = "text-embedding-3-large"
    max_context_documents: int = 5
    similarity_threshold: float = 0.8
    rerank_enabled: bool = True
    rerank_model: str = "rerank-multilingual-v3.0"
    cache_enabled: bool = True
    cache_ttl: int = 3600


@dataclass
class GovernorConfig:
    """Configuration for governance and safety controls."""

    safety_enabled: bool = True
    safety_threshold: float = 0.95
    content_filter_enabled: bool = True
    pii_detection_enabled: bool = True
    bias_detection_enabled: bool = True
    audit_logging_enabled: bool = True
    max_requests_per_minute: int = 100
    allowed_models: list[str] = field(
        default_factory=lambda: ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"]
    )


@dataclass
class ReasoningConfig:
    """Centralized reasoning configuration for LLM generation."""

    cot_min_paths: int = 3
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 6
    reflexion: bool = True
    max_reflexion_loops: int = 2

    # Section-specific configurations (ClassVars set after class definition)
    K0_HEADLINE_CONFIG: ClassVar[ReasoningConfig | None] = None
    K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar[ReasoningConfig | None] = None
    K5_UNIFY_BULLETS_CONFIG: ClassVar[ReasoningConfig | None] = None
    K5_UNIFY_OVERVIEW_CONFIG: ClassVar[ReasoningConfig | None] = None
    K6_IBM_BULLETS_CONFIG: ClassVar[ReasoningConfig | None] = None
    K6_IBM_OVERVIEW_CONFIG: ClassVar[ReasoningConfig | None] = None
    K8_EY_BULLETS_CONFIG: ClassVar[ReasoningConfig | None] = None
    K8_EY_OVERVIEW_CONFIG: ClassVar[ReasoningConfig | None] = None
    K9_EARLY_CAREER_BULLETS_CONFIG: ClassVar[ReasoningConfig | None] = None
    K9_EARLY_CAREER_OVERVIEW_CONFIG: ClassVar[ReasoningConfig | None] = None
    K2_SKILLS_CONFIG: ClassVar[ReasoningConfig | None] = None
    K10_COMPETENCIES_CONFIG: ClassVar[ReasoningConfig | None] = None
    DEFAULT: ClassVar[ReasoningConfig | None] = None


# Initialize default config
ReasoningConfig.DEFAULT = ReasoningConfig()

# Global CONFIG singleton for backward compatibility
CONFIG = ReasoningConfig.DEFAULT

# C2 variable for singleton testing
C2 = CONFIG

# Section-specific configurations
_REASONING_CONFIGS = [
    (
        "K0_HEADLINE_CONFIG",
        {
            "cot_min_paths": 4,
            "tot_branches": 3,
            "min_tot_depth": 2,
            "self_consistency": 6,
            "reflexion": True,
        },
    ),
    (
        "K1_EXECUTIVE_SUMMARY_CONFIG",
        {
            "cot_min_paths": 3,
            "tot_branches": 3,
            "min_tot_depth": 3,
            "self_consistency": 12,
            "reflexion": True,
            "max_reflexion_loops": 2,
        },
    ),
    (
        "K5_UNIFY_BULLETS_CONFIG",
        {
            "cot_min_paths": 4,
            "tot_branches": 3,
            "min_tot_depth": 3,
            "self_consistency": 12,
            "reflexion": True,
        },
    ),
    ("K5_UNIFY_OVERVIEW_CONFIG", None),
    (
        "K6_IBM_BULLETS_CONFIG",
        {
            "cot_min_paths": 4,
            "tot_branches": 3,
            "min_tot_depth": 3,
            "self_consistency": 12,
            "reflexion": True,
        },
    ),
    (
        "K6_IBM_OVERVIEW_CONFIG",
        {
            "cot_min_paths": 2,
            "tot_branches": 2,
            "min_tot_depth": 2,
            "self_consistency": 4,
            "reflexion": False,
        },
    ),
    (
        "K8_EY_BULLETS_CONFIG",
        {
            "cot_min_paths": 2,
            "tot_branches": 2,
            "min_tot_depth": 2,
            "self_consistency": 4,
            "reflexion": False,
        },
    ),
    (
        "K8_EY_OVERVIEW_CONFIG",
        {
            "cot_min_paths": 2,
            "tot_branches": 2,
            "min_tot_depth": 2,
            "self_consistency": 4,
            "reflexion": False,
        },
    ),
    (
        "K9_EARLY_CAREER_BULLETS_CONFIG",
        {
            "cot_min_paths": 2,
            "tot_branches": 2,
            "min_tot_depth": 2,
            "self_consistency": 4,
            "reflexion": False,
        },
    ),
    (
        "K9_EARLY_CAREER_OVERVIEW_CONFIG",
        {
            "cot_min_paths": 2,
            "tot_branches": 2,
            "min_tot_depth": 2,
            "self_consistency": 4,
            "reflexion": False,
        },
    ),
    (
        "K2_SKILLS_CONFIG",
        {
            "cot_min_paths": 2,
            "tot_branches": 2,
            "min_tot_depth": 2,
            "self_consistency": 4,
            "reflexion": False,
        },
    ),
    (
        "K10_COMPETENCIES_CONFIG",
        {
            "cot_min_paths": 3,
            "tot_branches": 3,
            "min_tot_depth": 2,
            "self_consistency": 10,
            "reflexion": True,
        },
    ),
]

for _name, _cfg in _REASONING_CONFIGS:
    if _cfg is None:
        setattr(ReasoningConfig, _name, ReasoningConfig.DEFAULT)
    else:
        setattr(ReasoningConfig, _name, ReasoningConfig(**_cfg))

# Safety threshold for guardrail validation
SAFETY_THRESHOLD = 0.95

__all__ = [
    "ModelProvider",
    "ModelConfig",
    "RAGConfig",
    "GovernorConfig",
    "ReasoningConfig",
    "CONFIG",
    "C2",
    "SAFETY_THRESHOLD",
]
