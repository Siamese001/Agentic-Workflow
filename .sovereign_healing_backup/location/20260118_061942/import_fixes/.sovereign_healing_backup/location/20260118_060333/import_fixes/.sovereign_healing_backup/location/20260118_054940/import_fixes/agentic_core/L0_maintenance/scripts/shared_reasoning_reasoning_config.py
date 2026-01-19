from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Protocol

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


_logger = logging.getLogger(__name__)
# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Reasoning configuration for LLM generation.

EXTRACTED from: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""


# NAMING FIXED: ModelProvider → ModelProvider
class ModelProvider(str, Enum):
    """Available model providers."""


@dataclass
# NAMING FIXED: ModelConfig → ModelConfig
class ModelConfig:
    """Configuration for LLM model parameters."""

    _provider: ModelProvider = ModelProvider.OPENAI
    _model_name: str = "gpt-4o"
    _temperature: float = 0.7
    _max_tokens: int = 2000
    _top_p: float = 0.95
    _frequency_penalty: float = 0.0
    _presence_penalty: float = 0.0
    _timeout: int = 30
    _max_retries: int = 3


@dataclass
# NAMING FIXED: RAGConfig → RagConfig
class RagConfig:
    """Configuration for Retrieval-Augmented Generation."""

    _enabled: bool = True
    _vector_store_path: str = "data/vector_store"
    _embedding_model: str = "text-embedding-3-large"
    _max_context_documents: int = 5
    _similarity_threshold: float = 0.8
    _rerank_enabled: bool = True
    _rerank_model: str = "rerank-multilingual-v3.0"
    _cache_enabled: bool = True
    _cache_ttl: int = 3600


@dataclass
# NAMING FIXED: GovernorConfig → GovernorConfig
class GovernorConfig:
    """Configuration for governance and safety controls."""

    _safety_enabled: bool = True
    _safety_threshold: float = 0.95
    _content_filter_enabled: bool = True
    _pii_detection_enabled: bool = True
    _bias_detection_enabled: bool = True
    _audit_logging_enabled: bool = True
    _max_requests_per_minute: int = 100
    _allowed_models: List[str] = field(
        default_factory=lambda: ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"]
    )


@dataclass
# NAMING FIXED: ReasoningConfig → ReasoningConfig
class ReasoningConfig:
    """Centralized reasoning configuration for LLM generation."""

    _cot_min_paths: int = 3
    _tot_branches: int = 3
    _min_tot_depth: int = 2
    _self_consistency: int = 6
    _reflexion: bool = True
    _max_reflexion_loops: int = 2

    # Section-specific configurations (ClassVars set after class definition)
    _K0_HEADLINE_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K1_EXECUTIVE_SUMMARY_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K5_UNIFY_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K5_UNIFY_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K6_IBM_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K6_IBM_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K8_EY_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K8_EY_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K9_EARLY_CAREER_BULLETS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K9_EARLY_CAREER_OVERVIEW_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K2_SKILLS_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _K10_COMPETENCIES_CONFIG: ClassVar[Optional[ReasoningConfig]] = None
    _DEFAULT: ClassVar[Optional[ReasoningConfig]] = None


# Initialize default config

# Global CONFIG singleton for backward compatibility
# NAMING FIXED: _CONFIG → _config
_config = ReasoningConfig.DEFAULT

# C2 variable for singleton testing

# Section-specific configurations
# NAMING FIXED: _REASONING_CONFIGS → _reasoning_configs
_reasoning_configs = [
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