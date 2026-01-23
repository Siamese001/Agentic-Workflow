from __future__ import annotations

"""
Sovereign configuration SSOT
Centralizes all environment variables, feature flags, and system constants.
"""
import os
from dataclasses import dataclass
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)


# NOT_AN_AGENT — config dataclass, not a true agent — excluded from agent discovery
@dataclass(frozen=True)
class SovereignConfig:
    """Brief description of functionality and purpose."""

    PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "us-east-1")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"
    DEFAULT_EMBEDDING_DIM: int = 1024
    PRIMARY_MODEL: str = "gemini-2.5-flash"
    REASONING_MODEL: str = "gemini-2.5-flash"
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.95
    MAX_RETRY_ATTEMPTS: int = 3
    CHECKPOINT_INTERVAL_SECONDS: int = 300
    BASE_GIT_PATH: str = "c:/Git/Agentic-Workflow/"
    CORE_CONTRACTS_PATH: str = f"{BASE_GIT_PATH}agentic_core/schemas/models/core_contracts.py"
    PROMPT_CONSTITUTION_PATH: str = f"{BASE_GIT_PATH}agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py"
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__)).split(AGENTIC_CORE_DIR)[0]
    RG_MIN_WORDS: int = 300
    RG_MAX_WORDS: int = 800
    RG_REASONING_TEMPERATURE: float = 0.7
    RG_MAX_RESUME_LENGTH_CHARS: int = 10000
    RG_ATS_COMPLIANCE_LEVEL: str = "strict"
    LIC_MAX_MESSAGE_CHARS: int = 2000
    LIC_TARGET_TONE: str = "professional_warm"
    LIC_CTA_STRENGTH: str = "direct"
    APP_LOG_LEVEL: str = "INFO"
    APP_CACHE_TTL_SECONDS: int = 3600
    AGENT_IMPLEMENTATION_MODE: str = "real"
    MODEL_PRICING: dict[str, dict[str, float]] = None
    DEFAULT_COST_MODEL: str = "gemini-2.5-flash"
    SEQUENTIAL_THINKING_MCP_ENABLED: bool = True
    SEQ_THINKING_MAX_STEPS: int = 20
    SEQ_THINKING_TEMPERATURE: float = 0.7
    SEQ_THINKING_ENABLE_HYPOTHESIS_BRANCHING: bool = True
    SEQ_THINKING_ENABLE_SELF_REVISION: bool = True
    SEQ_THINKING_PRUNE_LOW_CONFIDENCE: bool = True
    SEQ_THINKING_MIN_HYPOTHESIS_CONFIDENCE: float = 0.6
    PINECONE_MCP_ENABLED: bool = True
    PINECONE_RERANK_MODEL: str = "bge-reranker-v2-m3"
    PINECONE_INFERENCE_MODEL: str = "multilingual-e5-large"
    PINECONE_DEFAULT_NAMESPACE: str = "sovereign_memory_v1"
    BRAVE_SEARCH_MCP_ENABLED: bool = True
    BRAVE_SEARCH_SUMMARIZE: bool = True
    BRAVE_SEARCH_SAFE_SEARCH: str = "moderate"
    BRAVE_SEARCH_COUNT: int = 5
    BRAVE_SEARCH_COUNTRY: str = "US"
    KG_MCP_ENABLED: bool = True
    KG_AUTO_SYNC_ENTITIES: bool = True
    DEEPWIKI_MCP_ENABLED: bool = True
    DEEPWIKI_REPO_CONTEXT: str = "local"
    DEEPWIKI_INDEX_ON_STARTUP: bool = False
    PLAYWRIGHT_MCP_ENABLED: bool = True
    PLAYWRIGHT_BROWSER_TYPE: str = "chromium"
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_VIEWPORT_WIDTH: int = 1280
    PLAYWRIGHT_VIEWPORT_HEIGHT: int = 720
    PLAYWRIGHT_SCREENSHOT_ON_FAILURE: bool = True
    FETCH_MCP_ENABLED: bool = True
    FETCH_MAX_CONTENT_LENGTH: int = 10000
    FETCH_EXTRACT_MARKDOWN: bool = True
    FETCH_TIMEOUT_SECONDS: int = 30
    REDIS_MCP_ENABLED: bool = True
    REDIS_DEFAULT_TTL_SECONDS: int = 3600
    REDIS_MAX_KEY_LENGTH: int = 512
    REDIS_CACHE_PREFIX: str = "sovereign:"
    LLM_ROUTER_MCP_ENABLED: bool = True
    LLM_ROUTER_DEFAULT_PROVIDER: str = "gemini-2.5-flash"
    LLM_ROUTER_SAFETY_MODEL: str = "gemini-2.5-flash"
    LLM_ROUTER_VALIDATION_TEMPERATURE: float = 0.0
    LLM_ROUTER_MAX_TOKENS: int = 1024
    FILESYSTEM_MCP_ENABLED: bool = True
    FILESYSTEM_MAX_READ_SIZE: int = 10000000
    FILESYSTEM_ALLOWED_ROOTS: list[str] = None
    FILESYSTEM_FORBIDDEN_PATTERNS: list[str] = None
    GITKRAKEN_MCP_ENABLED: bool = True
    GITKRAKEN_DEFAULT_REPO: str = "xai/sovereign-canon"
    GITKRAKEN_HEALING_BRANCH: str = "sovereign-healing"
    GITKRAKEN_PR_TITLE_PREFIX: str = "[SOVEREIGN HEALING]"
    AUTONOMOUS_HEALING_ENABLED: bool = True
    HEALING_AUTO_APPLY: bool = True
    HEALING_AUTO_COMMIT: bool = True
    HEALING_AUTO_PR: bool = False
    HEALING_MAX_FIXES_PER_CYCLE: int = 20
    PINECONE_VECTOR_HEALING_ENABLED: bool = True
    VECTOR_HEALING_BATCH_SIZE: int = 50
    VECTOR_HEALING_MAX_DAILY: int = 500
    VECTOR_HEALING_EMBED_MODEL: str = "multilingual-e5-large"
    KNOWLEDGE_GRAPH_HEALING_ENABLED: bool = True
    KG_HEALING_BATCH_SIZE: int = 20
    KG_HEALING_MAX_DAILY: int = 200
    KG_MIN_CONFIDENCE_FOR_HEALING: float = 0.7
    KG_HEALING_RE_EXTRACT_ON_DRIFT: bool = True
    DEEPWIKI_HEALING_ENABLED: bool = True
    DEEPWIKI_HEALING_BATCH_SIZE: int = 10
    DEEPWIKI_HEALING_MAX_DAILY: int = 100
    DEEPWIKI_DEFAULT_REPO: str = "xai/sovereign-canon"
    GITKRAKEN_HEALING_ENABLED: bool = True
    GITKRAKEN_HEALING_AUTO_COMMIT: bool = True
    GITKRAKEN_HEALING_AUTO_PR: bool = True
    L6_AUDIT_HEALING_ENABLED: bool = True
    L6_AUDIT_HEALING_MAX_DAILY: int = 500
    L6_AUDIT_RECONSTRUCTION_WINDOW_HOURS: int = 24

    def __post_init__(self):
        """Initialize mutable defaults after dataclass creation."""
        object.__setattr__(
            self,
            "MODEL_PRICING",
            {
                "gemini-2.5-flash": {"input": 0.075, "output": 0.3},
                "gpt-5.1": {"input": 0.003, "output": 0.012},
                "claude-sonnet-4.5": {"input": 0.0035, "output": 0.018},
            },
        )
        object.__setattr__(
            self,
            "FILESYSTEM_ALLOWED_ROOTS",
            [AGENTIC_CORE_DIR, APPS_SHARED_DIR, APPS_RG_DIR, APPS_LIC_DIR, "config"],
        )
        object.__setattr__(
            self, "FILESYSTEM_FORBIDDEN_PATTERNS", ["\\.\\./", "/etc/", "/proc/", "\\.env"]
        )

    def validate(self) -> Any:
        """Ensure critical secrets are present."""
        errors: Any = []
        if not self.PINECONE_API_KEY:
            errors.append("CRITICAL: PINECONE_API_KEY is Missing.")
        if not self.OPENAI_API_KEY:
            errors.append("CRITICAL: OPENAI_API_KEY is Missing.")
        if errors:
            raise ValueError("\n".join(errors))


# Alias for backward compatibility
config: Any = SovereignConfig()
