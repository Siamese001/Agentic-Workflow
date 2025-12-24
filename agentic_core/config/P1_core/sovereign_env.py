#!/usr/bin/env python3
"""
sovereign_env.py - Eternal Single Source of Truth Gateway to .env

This module serves as the Constitutional Gateway for ALL environment configuration.
Every agent and script must pass through here to access environment variables.
Zero drift, fail-fast, type-safe enforcement of .env SSOT integrity.
"""
import os
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv


class SovereignEnv:
    """Sovereign .env loader — fail-fast, type-safe, zero-drift."""
    _instance = None

    def __new__(cls, project_root: Optional[Path] = None):
        if cls._instance is None:
            if project_root is None:
                raise ValueError("[L6 CRITICAL] SovereignEnv requires project_root on first init")
            cls._instance = super().__new__(cls)
            cls._instance._load(project_root)
        return cls._instance

    def _load(self, project_root: Path):
        """Load and validate all environment configuration from root .env"""
        env_path = project_root / ".env"
        if not env_path.exists():
            raise FileNotFoundError(f"[L6 CRITICAL] .env missing at {env_path} — Neural Link broken")

        load_dotenv(dotenv_path=env_path, override=True)

        # [ETERNAL MANDATORY] GEMINI-ONLY policy — enforced at load
        self.GEMINI_API_KEY = self._require("GEMINI_API_KEY")
        self.GEMINI_MODEL = self._require("GEMINI_MODEL")

        # Forbidden non-Gemini keys — immediate halt if present
        if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("[L6 NEURAL LINK BREACH] Non-Gemini keys detected — GEMINI-ONLY policy violated")

        # === VECTOR & CACHE ===
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.PINECONE_API_KEY = self._require("PINECONE_API_KEY")
        self.PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "canon-sovereign-territory")
        self.PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
        self.PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

        # === HEALING BUDGETS ===
        self.MAX_HEALING_PER_FILE = int(os.getenv("MAX_HEALING_PER_FILE", "8"))
        self.GLOBAL_HEALING_BUDGET = int(os.getenv("GLOBAL_HEALING_BUDGET", "50"))
        self.MAX_HEALING_ROUNDS = int(os.getenv("MAX_HEALING_ROUNDS", "3"))

    def _require(self, key: str) -> str:
        """Require a mandatory environment variable with fail-fast validation."""
        value = os.getenv(key)
        if not value or not value.strip():
            raise ValueError(f"[L6 CRITICAL] Missing mandatory .env key: {key}")
        return value.strip()


# Global singleton
_config: Optional[SovereignEnv] = None


def get_env(project_root: Optional[Path] = None) -> SovereignEnv:
    """
    Get the singleton SovereignEnv instance.
    
    Args:
        project_root: Path to project root (required on first call)
        
    Returns:
        SovereignEnv singleton instance
        
    Raises:
        ValueError: If project_root not provided on first call
        FileNotFoundError: If .env file missing
    """
    global _config
    if _config is None:
        if project_root is None:
            # Fallback to current working directory if root not passed
            project_root = Path.cwd()
        _config = SovereignEnv(project_root)
    return _config
