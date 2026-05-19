from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


class SovereignEnv:
    """Sovereign .env loader - fail-fast, type-safe, zero-drift."""

    _instance: "SovereignEnv | None" = None
    _loaded_env_path: Path | None = None

    def __new__(cls, project_root: Path | None = None):
        normalized_root = Path(project_root).resolve() if project_root is not None else None
        if cls._instance is None:
            if normalized_root is None:
                raise ValueError("[L6 CRITICAL] SovereignEnv requires project_root on first init")
            # Atomic init: if _load() raises, roll back _instance so the next
            # caller can retry instead of inheriting a half-initialized
            # singleton with _loaded_env_path=None (which produced the
            # misleading "already initialized from None" cascade).
            cls._instance = super().__new__(cls)
            try:
                cls._instance._load(normalized_root)
            except Exception:  # guardian: allow-broad-catch -- singleton init failed: reset instance to None then re-raise; broad catch ensures any init failure rolls back
                cls._instance = None
                raise
            cls._loaded_env_path = normalized_root / ".env"
        elif normalized_root is not None:
            expected_env_path = normalized_root / ".env"
            if cls._loaded_env_path != expected_env_path:
                raise ValueError(
                    f"[L6 CRITICAL] SovereignEnv already initialized from {cls._loaded_env_path}; "
                    f"refusing conflicting root {expected_env_path}"
                )
        return cls._instance

    @staticmethod
    def _read_int(key: str, default: int, *, minimum: int | None = None) -> int:
        raw = os.getenv(key)
        if raw is None or not raw.strip():
            value = default
        else:
            try:
                value = int(raw)
            except ValueError as exc:
                raise ValueError(f"[L6 CRITICAL] Invalid integer for {key}: {raw}") from exc
        if minimum is not None and value < minimum:
            raise ValueError(f"[L6 CRITICAL] {key} must be >= {minimum}, got {value}")
        return value

    def _load(self, project_root: Path):
        """Load and validate all environment configuration from root .env."""
        env_path = project_root / ".env"
        if not env_path.is_file():
            raise FileNotFoundError(f"[L6 CRITICAL] .env missing at {env_path} - Neural Link broken")

        load_dotenv(dotenv_path=env_path, override=False)

        from agentic_core.config.google_ai_env import (
            GEMINI_API_KEY_LEGACY,
            GEMINI_MODEL_LEGACY,
            GOOGLE_AI_MODEL,
            GOOGLE_API_KEY,
            google_ai_flash_model_id,
            google_api_key,
        )

        api_key, api_key_src = google_api_key()
        if not api_key:
            raise ValueError(
                f"[L6 CRITICAL] {GOOGLE_API_KEY} required "
                f"(deprecated alias: {GEMINI_API_KEY_LEGACY})"
            )
        if api_key_src == GEMINI_API_KEY_LEGACY and not os.getenv(GOOGLE_API_KEY):
            os.environ[GOOGLE_API_KEY] = api_key
        self.GOOGLE_API_KEY = api_key
        self.GEMINI_API_KEY = api_key  # backward-compat attribute for legacy callers

        flash_model, flash_src = google_ai_flash_model_id()
        if not flash_model:
            raise ValueError(
                f"[L6 CRITICAL] {GOOGLE_AI_MODEL} required "
                f"(deprecated alias: {GEMINI_MODEL_LEGACY})"
            )
        if flash_src == GEMINI_MODEL_LEGACY and not os.getenv(GOOGLE_AI_MODEL):
            os.environ[GOOGLE_AI_MODEL] = flash_model
        self.GOOGLE_AI_MODEL = flash_model
        self.GEMINI_MODEL = flash_model  # backward-compat attribute
        inactive_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CLAUDE_API_KEY"]
        self._inactive_keys = [key for key in inactive_keys if os.getenv(key)]
        self.REDIS_URL = self._require("REDIS_URL")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.REDIS_SSL = os.getenv("REDIS_SSL", "false").strip().lower() == "true"
        self.EMBEDDING_DIMENSION = self._read_int("EMBEDDING_DIMENSION", 1536, minimum=1)
        self.NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687").strip()
        self.NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j").strip()
        self.NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
        self.REDIS_SSL_CERT_PATH = os.getenv("REDIS_SSL_CERT_PATH")
        self.REDIS_SSL_KEY_PATH = os.getenv("REDIS_SSL_KEY_PATH")
        self.MCP_TIMEOUT_SECONDS = self._read_int("MCP_TIMEOUT_SECONDS", 30, minimum=1)
        self.MCP_MAX_RETRIES = self._read_int("MCP_MAX_RETRIES", 3, minimum=0)
        self.MAX_HEALING_PER_FILE = self._read_int("MAX_HEALING_PER_FILE", 8, minimum=0)
        self.GLOBAL_HEALING_BUDGET = self._read_int("GLOBAL_HEALING_BUDGET", 50, minimum=0)
        self.MAX_HEALING_ROUNDS = self._read_int("MAX_HEALING_ROUNDS", 3, minimum=0)

        if self.REDIS_SSL and (not self.REDIS_SSL_CERT_PATH or not self.REDIS_SSL_KEY_PATH):
            raise ValueError("[L6 CRITICAL] REDIS_SSL requires REDIS_SSL_CERT_PATH and REDIS_SSL_KEY_PATH")

    def _require(self, key: str) -> str:
        value = os.getenv(key)
        if not value or not value.strip():
            raise ValueError(f"[L6 CRITICAL] Missing mandatory .env key: {key}")
        return value.strip()


_config: SovereignEnv | None = None


def get_env(project_root: Path | None = None) -> SovereignEnv:
    """Get the singleton SovereignEnv instance."""
    global _config
    if _config is None:
        if project_root is None:
            raise ValueError("[L6 CRITICAL] get_env requires project_root on first call")
        _config = SovereignEnv(Path(project_root).resolve())
    return _config
