"""
Sovereign Configuration SSOT
Centralizes all environment variables, feature flags, and system constants.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict

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
    
    # === Phase 8A: Model Pricing Table (Dec 26, 2025) ===
    # Dollars per 1M tokens
    MODEL_PRICING: Dict[str, Dict[str, float]] = None  # Initialized below due to dataclass constraints
    DEFAULT_COST_MODEL: str = "gemini-2.5-flash"
    
    def __post_init__(self):
        """Initialize mutable defaults after dataclass creation."""
        # Must use object.__setattr__ due to frozen=True
        # Approved models: gemini-2.5-flash (default), gpt-5.1 (OpenAI), Claude Sonnet 4.5 (Anthropic)
        object.__setattr__(self, 'MODEL_PRICING', {
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # $0.075 / $0.30 per 1M tokens
            "gpt-5.1": {"input": 0.0030, "output": 0.012},  # $3.00 / $12.00 per 1M tokens (estimated)
            "claude-sonnet-4.5": {"input": 0.0035, "output": 0.018},  # $3.50 / $18.00 per 1M tokens (estimated)
        })
    
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
