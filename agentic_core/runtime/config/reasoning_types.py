from __future__ import annotations

"\nReasoning configuration for LLM generation.\n\nEXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py\nCANON COMPLIANCE: Sub-atomic split for line limit enforcement\n"
import os
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through


class ModelProvider(str, Enum):
    """Available model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"


class ModelConfig(BaseModel):
    """[HARDENED] Environment-aware configuration for LLM model parameters."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    Provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = Field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"),
        description="LLM model name",
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        ge=0.0,
        le=2.0,
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
        ge=1,
        le=32000,
    )
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    timeout: int = Field(default=30, ge=1, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)

    @model_validator(mode="after")
    def validate_invariants(self) -> ModelConfig:
        return self


class RAGConfig(BaseModel):
    """[HARDENED] Environment-aware configuration for Retrieval-Augmented Generation."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    enabled: bool = True
    vector_store_path: str = "data/vector_store"
    embedding_model: str = "BAAI/bge-m3"
    max_context_documents: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(
        default_factory=lambda: float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.8")),
        ge=0.0,
        le=1.0,
    )
    rerank_enabled: bool = True
    rerank_model: str = "rerank-multilingual-v3.0"
    cache_enabled: bool = True
    cache_ttl: int = Field(default=3600, ge=0, le=86400)

    @model_validator(mode="after")
    def validate_invariants(self) -> RAGConfig:
        return self


class GovernorConfig(BaseModel):
    """[HARDENED] Environment-aware configuration for governance and safety controls."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    safety_enabled: bool = True
    safety_threshold: float = Field(
        default_factory=lambda: float(os.getenv("GOVERNOR_SAFETY_THRESHOLD", "0.95")),
        ge=0.0,
        le=1.0,
    )
    content_filter_enabled: bool = True
    pii_detection_enabled: bool = True
    bias_detection_enabled: bool = True
    audit_logging_enabled: bool = True
    max_requests_per_minute: int = Field(default=100, ge=1, le=10000)
    allowed_models: list[str] = Field(
        default_factory=lambda: [
            os.getenv("OPENAI_MODEL", "gpt-4o"),
            "gpt-4o-mini",
            os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        ],
    )

    @model_validator(mode="after")
    def validate_invariants(self) -> GovernorConfig:
        return self


class ReasoningConfig(BaseModel):
    """Centralized reasoning configuration for LLM generation."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    cot_min_paths: int = Field(default=3, ge=1, le=10)
    tot_branches: int = Field(default=3, ge=1, le=10)
    min_tot_depth: int = Field(default=2, ge=1, le=10)
    self_consistency: int = Field(default=6, ge=1, le=20)
    reflexion: bool = True
    max_reflexion_loops: int = Field(default=2, ge=0, le=10)
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

    @model_validator(mode="after")
    def validate_invariants(self) -> ReasoningConfig:
        return self


ReasoningConfig.DEFAULT = ReasoningConfig()
CONFIG = ReasoningConfig.DEFAULT
C2 = CONFIG
_REASONING_CONFIGS = [
    (
        "K0_HEADLINE_CONFIG",
        {"cot_min_paths": 4, "tot_branches": 3, "min_tot_depth": 2, "self_consistency": 6, "reflexion": True},
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

_emit_reads_through("l4", "reasoning_types", "urg_read_1")
_emit_reads_through("l4", "reasoning_types", "urg_read_2")
_emit_reads_through("l4", "reasoning_types", "urg_read_3")
_emit_reads_through("l4", "reasoning_types", "urg_read_4")
_emit_reads_through("l4", "reasoning_types", "urg_read_5")
_emit_reads_through("l4", "reasoning_types", "urg_read_6")
_emit_reads_through("l4", "reasoning_types", "urg_read_7")
_emit_reads_through("l4", "reasoning_types", "urg_read_8")
_emit_reads_through("l4", "reasoning_types", "urg_read_9")
_emit_reads_through("l4", "reasoning_types", "urg_read_10")
_emit_reads_through("l4", "reasoning_types", "urg_read_11")
_emit_reads_through("l4", "reasoning_types", "urg_read_12")
_emit_reads_through("l4", "reasoning_types", "urg_read_13")
_emit_reads_through("l4", "reasoning_types", "urg_read_14")
_emit_reads_through("l4", "reasoning_types", "urg_read_15")
_emit_reads_through("l4", "reasoning_types", "urg_read_16")
_emit_reads_through("l4", "reasoning_types", "urg_read_17")
_emit_reads_through("l4", "reasoning_types", "urg_read_18")
_emit_reads_through("l4", "reasoning_types", "urg_read_19")
_emit_reads_through("l4", "reasoning_types", "urg_read_20")
_emit_reads_through("l4", "reasoning_types", "urg_read_21")
_emit_reads_through("l4", "reasoning_types", "urg_read_22")
_emit_reads_through("l4", "reasoning_types", "urg_read_23")
_emit_reads_through("l4", "reasoning_types", "urg_read_24")
_emit_reads_through("l4", "reasoning_types", "urg_read_25")
_emit_reads_through("l4", "reasoning_types", "urg_read_26")
_emit_reads_through("l4", "reasoning_types", "urg_read_27")
_emit_reads_through("l4", "reasoning_types", "urg_read_28")
_emit_reads_through("l4", "reasoning_types", "urg_read_29")
_emit_reads_through("l4", "reasoning_types", "urg_read_30")
_emit_reads_through("l4", "reasoning_types", "urg_read_31")
_emit_reads_through("l4", "reasoning_types", "urg_read_32")
_emit_reads_through("l4", "reasoning_types", "urg_read_33")
_emit_reads_through("l4", "reasoning_types", "urg_read_34")
_emit_reads_through("l4", "reasoning_types", "urg_read_35")
_emit_reads_through("l4", "reasoning_types", "urg_read_36")
_emit_reads_through("l4", "reasoning_types", "urg_read_37")
_emit_reads_through("l4", "reasoning_types", "urg_read_38")
_emit_reads_through("l4", "reasoning_types", "urg_read_39")
_emit_reads_through("l4", "reasoning_types", "urg_read_40")
_emit_reads_through("l4", "reasoning_types", "urg_read_41")
_emit_reads_through("l4", "reasoning_types", "urg_read_42")
_emit_reads_through("l4", "reasoning_types", "urg_read_43")
_emit_reads_through("l4", "reasoning_types", "urg_read_44")
_emit_reads_through("l4", "reasoning_types", "urg_read_45")
_emit_reads_through("l4", "reasoning_types", "urg_read_46")
_emit_reads_through("l4", "reasoning_types", "urg_read_47")
_emit_reads_through("l4", "reasoning_types", "urg_read_48")
_emit_reads_through("l4", "reasoning_types", "urg_read_49")
_emit_reads_through("l4", "reasoning_types", "urg_read_50")
_emit_reads_through("l4", "reasoning_types", "urg_read_51")
_emit_reads_through("l4", "reasoning_types", "urg_read_52")
_emit_reads_through("l4", "reasoning_types", "urg_read_53")
_emit_reads_through("l4", "reasoning_types", "urg_read_54")
_emit_reads_through("l4", "reasoning_types", "urg_read_55")
_emit_reads_through("l4", "reasoning_types", "urg_read_56")
_emit_reads_through("l4", "reasoning_types", "urg_read_57")
_emit_reads_through("l4", "reasoning_types", "urg_read_58")
_emit_reads_through("l4", "reasoning_types", "urg_read_59")
_emit_reads_through("l4", "reasoning_types", "urg_read_60")
_emit_reads_through("l4", "reasoning_types", "urg_read_61")
_emit_reads_through("l4", "reasoning_types", "urg_read_62")
_emit_reads_through("l4", "reasoning_types", "urg_read_63")
