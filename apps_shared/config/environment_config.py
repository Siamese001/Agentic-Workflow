"""
Environment Configuration Schema.

Provides configuration data models for environment variables.
Phase 3 - Semantic split from environment_util.py (schema vs validation logic).
Aligned with apps_* pattern with full lifecycle trace contract integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_environ,
    _emit_reads_policy_state,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

# L1 retrieval wiring (Turn 2, Wave 10): Import creates ADG edge to L1_cognition

# P0: Foundation Governance
_emit_applies_guardrail("p0", "environment_config", "p0_governance")
_emit_reads_policy_state("p0", "environment_config", "policy_binding")
_emit_snapshots_state("p0", "environment_config", "state_snapshot")

# P2: Execution Capability
_emit_reads_environ("p2", "environment_config", "env_read")
_emit_validates_capability("p2", "environment_config", "capability_check")

# P0: Determinism
emit_replay_key("p0", "environment_config")
emit_determinism_digest("p0", "environment_config")

from apps_shared.config.pipeline_constants_config import MAX_RETRIES  # noqa: F401

DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class EnvironmentConfig(BaseModel):
    """Environment configuration with validation for required API keys."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_default=True,
    )

    # Core LLM Providers (Required)
    OPENAI_API_KEY: str = Field(..., min_length=1, description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(..., min_length=1, description="Anthropic API key")
    GEMINI_API_KEY: str = Field(..., min_length=1, description="Google Gemini API key")

    # Redis Configuration (Required)
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")

    # Optional Providers
    MISTRALAI_API_KEY: str | None = Field(default=None, description="Mistral AI API key")
    COHERE_API_KEY: str | None = Field(default=None, description="Cohere API key")
    GROQ_API_KEY: str | None = Field(default=None, description="Groq API key")
    TOGETHER_API_KEY: str | None = Field(default=None, description="Together AI API key")
    FIREWORKS_API_KEY: str | None = Field(default=None, description="Fireworks AI API key")
    BRAVE_SEARCH_API_KEY: str | None = Field(default=None, description="Brave Search API key")

    # GitHub & MCP Configuration
    GITHUB_TOKEN: str | None = Field(default=None, description="GitHub personal access token")
    DATABASE_URL: str | None = Field(
        default=None,
        description="PostgreSQL database URL for MCP server",
    )
    FIGMA_TOKEN: str | None = Field(default=None, description="Figma API token")

    # Model Configuration
    GEMINI_MODEL: str = Field(default="gemini-3-flash-preview", description="Gemini model name")
    GEMINI_PRO_MODEL: str = Field(default="gemini-2.5-pro", description="Gemini Pro model name")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI model name")

    # Thresholds and Limits
    SOVEREIGN_HIGH_CONFIDENCE: float = Field(default=0.75, ge=0.0, le=1.0)
    SOVEREIGN_MEDIUM_CONFIDENCE: float = Field(default=0.50, ge=0.0, le=1.0)
    RAG_SIMILARITY_THRESHOLD: float = Field(default=0.8, ge=0.0, le=1.0)
    GOVERNOR_SAFETY_THRESHOLD: float = Field(default=0.95, ge=0.0, le=1.0)

    # Application Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    PYTHONUNBUFFERED: str = Field(default="1", description="Python unbuffered output")

    # Hive Mind Configuration
    HIVE_MIND_STRICT_MODE: bool = Field(default=False, description="Strict mode for Hive Mind")
    HIVE_MIND_MIN_CONFIDENCE: float = Field(default=0.98, ge=0.0, le=1.0)
    HIVE_MIND_TRACE_SAMPLING_RATE: float = Field(default=1.0, ge=0.0, le=1.0)
    HIVE_MIND_PROMOTION_THRESHOLD: float = Field(default=0.8, ge=0.0, le=1.0)
    HIVE_MIND_WORKING_MEMORY_TTL: int = Field(default=86400, ge=0)
    HIVE_MIND_LONG_TERM_TTL: int = Field(default=604800, ge=0)


@dataclass
class EnvironmentValidationResult:
    """Result of environment validation."""

    valid: bool
    missing_required: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    config: EnvironmentConfig | None = None
