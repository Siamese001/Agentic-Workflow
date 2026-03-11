"""
SovereignConfigManager - Centralized configuration Management

[PHASE 6 MIGRATION] Consolidates configuration for:
- LLM defaults & API Keys (Phase 4)
- Embedding parameters (Phase 4)
- Safety thresholds (Phase 5)
- Infrastructure paths
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Setup basic logger since we can't depend on complex agent loggers here
Logger = logging.getLogger("SovereignConfig")


@dataclass
class SovereignConfigManager:
    """
    Centralized configuration Singleton.

    Design:
    - Low-level utility (No dependencies on BaseAgent).
    - Loads from Environment Variables with strictly typed defaults.
    - Single source of truth for Infrastructure constants.
    """

    _instance: SovereignConfigManager | None = None

    # --- DEFAULT CONSTANTS ---

    # Infrastructure Limits (Phases 4 & 5)
    DEFAULT_MAX_AUDIT_LOG_SIZE: int = 1000
    DEFAULT_MAX_HEALING_ATTEMPTS: int = 3
    DEFAULT_CACHE_TTL: int = 86400  # 24 Hours

    # Model Defaults (Phase 4) - Now sourced from environment
    DEFAULT_OPENAI_MODEL: str = "gpt-4o"
    DEFAULT_ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_GOOGLE_MODEL: str = "gemini-3-flash-preview"
    DEFAULT_GOOGLE_PRO_MODEL: str = "gemini-2.5-pro"
    DEFAULT_EMBEDDING_MODEL: str = "BAAI/bge-m3"
    DEFAULT_BGE_EMBEDDING_MODEL: str = "BAAI/bge-m3"

    # Dimensions (Phase 4)
    EMBEDDING_DIM_OPENAI: int = 1536
    EMBEDDING_DIM_GEMINI: int = 768
    EMBEDDING_DIM_BGE: int = 1024

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset singleton state."""
        cls._instance = None

    def get_str(self, key: str, default: str = "") -> str:
        """Get string env var."""
        return os.environ.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get int env var."""
        val = os.environ.get(key)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            Logger.warning(f"Config key {key} expected int, got {val}. Using default {default}.")
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get bool env var (true/false/1/0)."""
        val = os.environ.get(key)
        if val is None:
            return default
        return val.lower() in ("true", "1", "yes", "on")

    # --- Typed Accessors (API Surface) ---

    @property
    def max_audit_log_size(self) -> int:
        return self.get_int("SOVEREIGN_MAX_AUDIT_LOG_SIZE", self.DEFAULT_MAX_AUDIT_LOG_SIZE)

    @property
    def max_healing_attempts(self) -> int:
        return self.get_int("SOVEREIGN_MAX_HEALING_ATTEMPTS", self.DEFAULT_MAX_HEALING_ATTEMPTS)

    @property
    def openai_model(self) -> str:
        return self.get_str("OPENAI_MODEL", self.DEFAULT_OPENAI_MODEL)

    @property
    def anthropic_model(self) -> str:
        return self.get_str("ANTHROPIC_MODEL", self.DEFAULT_ANTHROPIC_MODEL)

    @property
    def google_model(self) -> str:
        return self.get_str("GEMINI_MODEL", self.DEFAULT_GOOGLE_MODEL)

    @property
    def google_pro_model(self) -> str:
        return self.get_str("GEMINI_PRO_MODEL", self.DEFAULT_GOOGLE_PRO_MODEL)

    # Redis MCP Configuration
    @property
    def redis_mcp_enabled(self) -> bool:
        """Redis MCP enablement - single source of truth from REDIS_MCP_ENABLED env var."""
        return self.get_bool("REDIS_MCP_ENABLED", False)

    # Compatibility alias for exact env var name
    @property
    def REDIS_MCP_ENABLED(self) -> bool:
        """Compatibility alias - exact env var name mapping."""
        return self.redis_mcp_enabled

    @property
    def redis_url(self) -> str:
        return self.get_str("REDIS_URL", "redis://localhost:6379")

    @property
    def redis_cache_prefix(self) -> str:
        return self.get_str("REDIS_CACHE_PREFIX", "agentic:")

    @property
    def redis_max_key_length(self) -> int:
        return self.get_int("REDIS_MAX_KEY_LENGTH", 250)

    @property
    def redis_default_ttl_seconds(self) -> int:
        return self.get_int("REDIS_DEFAULT_TTL_SECONDS", 3600)


# Singleton Accessor
def get_sovereign_config() -> SovereignConfigManager:
    return SovereignConfigManager()
