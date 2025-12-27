"""
Sovereign Configuration SSOT
Centralizes all environment variables, feature flags, and system constants.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass(frozen=True)
class SovereignConfig:
    # Vector Database
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "us-east-1")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    
    # Embedding Model (SOTA: text-embedding-3-large)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"
    DEFAULT_EMBEDDING_DIM: int = 1024  # Truncated for Pinecone cost/perf sweet spot
    
    # === Phase 4: Model Governance (Dec 26, 2025) ===
    PRIMARY_MODEL: str = "gemini-2.5-flash"
    REASONING_MODEL: str = "gemini-2.5-flash"
    
    # === Phase 4: Semantic Cache Thresholds ===
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.95
    
    # === Phase 4: Global Operational Constants ===
    MAX_RETRY_ATTEMPTS: int = 3
    CHECKPOINT_INTERVAL_SECONDS: int = 300
    
    # === Phase 4: Critical Path Registry ===
    BASE_GIT_PATH: str = "c:/Git/Agentic-Workflow/"
    CORE_CONTRACTS_PATH: str = f"{BASE_GIT_PATH}agentic_core/schemas/models/core_contracts.py"
    PROMPT_CONSTITUTION_PATH: str = f"{BASE_GIT_PATH}agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py"
    
    # System Paths
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__)).split("agentic_core")[0]
    
    # === Phase 8: App Layer Configuration (Dec 26, 2025) ===
    # Resume Generation (apps_rg)
    RG_MIN_WORDS: int = 300
    RG_MAX_WORDS: int = 800
    RG_REASONING_TEMPERATURE: float = 0.7
    RG_MAX_RESUME_LENGTH_CHARS: int = 10000
    RG_ATS_COMPLIANCE_LEVEL: str = "strict"
    
    # LinkedIn Outreach (apps_lic)
    LIC_MAX_MESSAGE_CHARS: int = 2000
    LIC_TARGET_TONE: str = "professional_warm"
    LIC_CTA_STRENGTH: str = "direct"
    
    # Shared App Config
    APP_LOG_LEVEL: str = "INFO"
    APP_CACHE_TTL_SECONDS: int = 3600
    
    # === Phase 11: Agent Implementation Strategy (Dec 26, 2025) ===
    # Options: "real" (standard), "mock" (unit tests), "aggressive" (fast-healing)
    AGENT_IMPLEMENTATION_MODE: str = "real"
    
    # === Phase 8A: Model Pricing Table (Dec 26, 2025) ===
    # Dollars per 1M tokens
    MODEL_PRICING: Dict[str, Dict[str, float]] = None  # Initialized below due to dataclass constraints
    DEFAULT_COST_MODEL: str = "gemini-2.5-flash"
    
    # === Phase 13: MCP Integrations (Dec 26, 2025) ===
    # Sequential Thinking MCP – L1 Cognition Enhancement
    SEQUENTIAL_THINKING_MCP_ENABLED: bool = True
    SEQ_THINKING_MAX_STEPS: int = 20
    SEQ_THINKING_TEMPERATURE: float = 0.7
    SEQ_THINKING_ENABLE_HYPOTHESIS_BRANCHING: bool = True
    SEQ_THINKING_ENABLE_SELF_REVISION: bool = True
    SEQ_THINKING_PRUNE_LOW_CONFIDENCE: bool = True
    SEQ_THINKING_MIN_HYPOTHESIS_CONFIDENCE: float = 0.6
    
    # Pinecone MCP Defaults
    PINECONE_MCP_ENABLED: bool = True
    PINECONE_RERANK_MODEL: str = "bge-reranker-v2-m3"
    PINECONE_INFERENCE_MODEL: str = "multilingual-e5-large"
    PINECONE_DEFAULT_NAMESPACE: str = "sovereign_memory_v1"
    
    # === Phase 13F: Brave Search MCP (Dec 26, 2025) ===
    BRAVE_SEARCH_MCP_ENABLED: bool = True
    BRAVE_SEARCH_SUMMARIZE: bool = True
    BRAVE_SEARCH_SAFE_SEARCH: str = "moderate"  # options: off, moderate, strict
    BRAVE_SEARCH_COUNT: int = 5
    BRAVE_SEARCH_COUNTRY: str = "US"
    
    # === Phase 13D: Knowledge Graph & DeepWiki (Dec 26, 2025) ===
    # 1. Knowledge Graph (Entity Memory)
    KG_MCP_ENABLED: bool = True
    KG_AUTO_SYNC_ENTITIES: bool = True
    
    # === Phase 13E: DeepWiki MCP Enhancement (Dec 26, 2025) ===
    # L6 Codebase Intelligence
    DEEPWIKI_MCP_ENABLED: bool = True
    # "local" implies the agent inspects the disk where it runs.
    # Can be a GitHub URL if inspecting a remote repo.
    DEEPWIKI_REPO_CONTEXT: str = "local"
    DEEPWIKI_INDEX_ON_STARTUP: bool = False
    
    # === Phase 14: Playwright MCP (Dec 26, 2025) ===
    PLAYWRIGHT_MCP_ENABLED: bool = True
    PLAYWRIGHT_BROWSER_TYPE: str = "chromium"
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_VIEWPORT_WIDTH: int = 1280
    PLAYWRIGHT_VIEWPORT_HEIGHT: int = 720
    PLAYWRIGHT_SCREENSHOT_ON_FAILURE: bool = True
    
    # === Phase 15: Fetch MCP (Dec 26, 2025) ===
    FETCH_MCP_ENABLED: bool = True
    FETCH_MAX_CONTENT_LENGTH: int = 10000
    FETCH_EXTRACT_MARKDOWN: bool = True
    FETCH_TIMEOUT_SECONDS: int = 30
    
    # === Phase 16A: Redis MCP – Sovereign Caching (Dec 27, 2025) ===
    REDIS_MCP_ENABLED: bool = True
    REDIS_DEFAULT_TTL_SECONDS: int = 3600
    REDIS_MAX_KEY_LENGTH: int = 512
    REDIS_CACHE_PREFIX: str = "sovereign:"
    
    # === Phase 16B: LLM Router MCP – Sovereign Validation (Dec 27, 2025) ===
    LLM_ROUTER_MCP_ENABLED: bool = True
    LLM_ROUTER_DEFAULT_PROVIDER: str = "gemini-2.5-flash"
    LLM_ROUTER_SAFETY_MODEL: str = "gemini-2.5-flash"
    LLM_ROUTER_VALIDATION_TEMPERATURE: float = 0.0
    LLM_ROUTER_MAX_TOKENS: int = 1024
    
    # === Phase 16C: Filesystem MCP – Sovereign File Operations (Dec 27, 2025) ===
    FILESYSTEM_MCP_ENABLED: bool = True
    FILESYSTEM_MAX_READ_SIZE: int = 10_000_000  # 10MB
    FILESYSTEM_ALLOWED_ROOTS: List[str] = None  # Will be set in __post_init__
    FILESYSTEM_FORBIDDEN_PATTERNS: List[str] = None  # Will be set in __post_init__
    
    # === Phase 16D: GitKraken MCP – Sovereign Version Control (Dec 27, 2025) ===
    GITKRAKEN_MCP_ENABLED: bool = True
    GITKRAKEN_DEFAULT_REPO: str = "xai/sovereign-canon"
    GITKRAKEN_HEALING_BRANCH: str = "sovereign-healing"
    GITKRAKEN_PR_TITLE_PREFIX: str = "[SOVEREIGN HEALING]"
    
    # === Phase 17: Autonomous L0 Self-Healing (Dec 27, 2025) ===
    AUTONOMOUS_HEALING_ENABLED: bool = True
    HEALING_AUTO_APPLY: bool = True  # False = propose only
    HEALING_AUTO_COMMIT: bool = True
    HEALING_AUTO_PR: bool = False   # True = create PR for review
    HEALING_MAX_FIXES_PER_CYCLE: int = 20
    
    # === Phase 17B: Pinecone Vector Healing (Dec 27, 2025) ===
    PINECONE_VECTOR_HEALING_ENABLED: bool = True
    VECTOR_HEALING_BATCH_SIZE: int = 50
    VECTOR_HEALING_MAX_DAILY: int = 500  # Prevent runaway healing
    VECTOR_HEALING_EMBED_MODEL: str = "multilingual-e5-large"
    
    # === Phase 17C: Knowledge Graph Healing (Dec 27, 2025) ===
    KNOWLEDGE_GRAPH_HEALING_ENABLED: bool = True
    KG_HEALING_BATCH_SIZE: int = 20
    KG_HEALING_MAX_DAILY: int = 200
    KG_MIN_CONFIDENCE_FOR_HEALING: float = 0.7
    KG_HEALING_RE_EXTRACT_ON_DRIFT: bool = True
    
    # === Phase 17E: DeepWiki Healing – Codebase Intelligence (Dec 27, 2025) ===
    DEEPWIKI_HEALING_ENABLED: bool = True
    DEEPWIKI_HEALING_BATCH_SIZE: int = 10
    DEEPWIKI_HEALING_MAX_DAILY: int = 100
    DEEPWIKI_DEFAULT_REPO: str = "xai/sovereign-canon"
    
    # === Phase 17D: GitKraken Healing – Sovereign Version Control (Dec 27, 2025) ===
    GITKRAKEN_HEALING_ENABLED: bool = True
    GITKRAKEN_HEALING_AUTO_COMMIT: bool = True
    GITKRAKEN_HEALING_AUTO_PR: bool = True
    
    def __post_init__(self):
        """Initialize mutable defaults after dataclass creation."""
        # Must use object.__setattr__ due to frozen=True
        # Approved models: gemini-2.5-flash (default), gpt-5.1 (OpenAI), Claude Sonnet 4.5 (Anthropic)
        object.__setattr__(self, 'MODEL_PRICING', {
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # $0.075 / $0.30 per 1M tokens
            "gpt-5.1": {"input": 0.0030, "output": 0.012},  # $3.00 / $12.00 per 1M tokens (estimated)
            "claude-sonnet-4.5": {"input": 0.0035, "output": 0.018},  # $3.50 / $18.00 per 1M tokens (estimated)
        })
        
        # Phase 16C: Initialize filesystem allowed roots and forbidden patterns
        object.__setattr__(self, 'FILESYSTEM_ALLOWED_ROOTS', [
            "agentic_core",
            "apps_shared",
            "apps_rg",
            "apps_lic",
            "config"
        ])
        object.__setattr__(self, 'FILESYSTEM_FORBIDDEN_PATTERNS', [
            r"\.\./",
            r"/etc/",
            r"/proc/",
            r"\.env"
        ])
    
    def validate(self):
        """Ensure critical secrets are present."""
        errors = []
        if not self.PINECONE_API_KEY:
            errors.append("CRITICAL: PINECONE_API_KEY is missing.")
        if not self.OPENAI_API_KEY:
            errors.append("CRITICAL: OPENAI_API_KEY is missing.")
        
        if errors:
            raise ValueError("\n".join(errors))

# Singleton Instance
config = SovereignConfig()
