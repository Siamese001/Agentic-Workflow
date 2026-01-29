"""
SovereignConfigManager - Centralized configuration Management

[PHASE 6 MIGRATION] Consolidates configuration for:
- LLM defaults & API Keys (Phase 4)
- Embedding parameters (Phase 4)
- Safety thresholds (Phase 5)
- Infrastructure paths
"""

from __future__ import annotations
from dataclasses import dataclass
import os
import logging

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
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Dimensions (Phase 4)
    EMBEDDING_DIM_OPENAI: int = 1536
    EMBEDDING_DIM_GEMINI: int = 768

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


# Singleton Accessor
def get_sovereign_config() -> SovereignConfigManager:
    return SovereignConfigManager()
