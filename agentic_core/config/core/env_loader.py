from __future__ import annotations

"\nSovereignEnv.py - Eternal Single Source of Truth Gateway to .env\n\nThis module serves as the Constitutional Gateway for ALL environment configuration.\nEvery agent and script must pass through here to access environment variables.\nZero drift, fail-fast, type-safe enforcement of .env SSOT integrity.\n"
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class SovereignEnv:
    """Sovereign .env loader — fail-fast, type-safe, zero-drift."""

    _instance = None

    def __new__(cls, project_root: Path | None = None):
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
            raise FileNotFoundError(f"[L6 CRITICAL] .env Missing at {env_path} — Neural Link broken")
        load_dotenv(dotenv_path=env_path, override=True)
        self.GEMINI_API_KEY = self._require("GEMINI_API_KEY")
        self.GEMINI_MODEL = self._require("GEMINI_MODEL")
        inactive_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CLAUDE_API_KEY"]
        self._inactive_keys = [key for key in inactive_keys if os.getenv(key)]
        self.REDIS_URL = self._require("REDIS_URL")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() == "true"
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
        self.NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
        self.REDIS_SSL_CERT_PATH = os.getenv("REDIS_SSL_CERT_PATH")
        self.REDIS_SSL_KEY_PATH = os.getenv("REDIS_SSL_KEY_PATH")
        self.MCP_TIMEOUT_SECONDS = int(os.getenv("MCP_TIMEOUT_SECONDS", "30"))
        self.MCP_MAX_RETRIES = int(os.getenv("MCP_MAX_RETRIES", "3"))
        self.MAX_HEALING_PER_FILE = int(os.getenv("MAX_HEALING_PER_FILE", "8"))
        self.GLOBAL_HEALING_BUDGET = int(os.getenv("GLOBAL_HEALING_BUDGET", "50"))
        self.MAX_HEALING_ROUNDS = int(os.getenv("MAX_HEALING_ROUNDS", "3"))

    def _require(self, key: str) -> str:
        """Require a mandatory environment variable with fail-fast validation."""
        value = os.getenv(key)
        if not value or not value.strip():
            raise ValueError(f"[L6 CRITICAL] Missing mandatory .env key: {key}")
        return value.strip()


_config: SovereignEnv | None = None


def get_env(project_root: Path | None = None) -> SovereignEnv:
    """
    Get the singleton SovereignEnv instance.

    Args:
        project_root: Path to project root (required on first call)

    Returns:
        SovereignEnv singleton instance

    Raises:
        ValueError: If project_root not provided on first call
        FileNotFoundError: If .env file Missing
    """
    global _config
    if _config is None:
        if project_root is None:
            project_root: Any = Path.cwd()
        _config = SovereignEnv(project_root)
    return _config
