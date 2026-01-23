from __future__ import annotations

"""
Sovereign Configuration SSOT
Centralizes all environment variables, feature flags, and system constants.
"""
import os
from dataclasses import dataclass

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)


@dataclass(frozen=True)
class SovereignConfig:
    # Vector Database
    PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "us-east-1")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")

    # Embedding Model (SOTA: text-embedding-3-large)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"
    DEFAULT_EMBEDDING_DIM: int = 1024  # Truncated for Pinecone cost/perf sweet spot

    # === Phase 4: Model Governance (Dec 26, 2025) ===
    PRIMARY_MODEL: str = "gpt-4o"
    REASONING_MODEL: str = "o1-preview"

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
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__)).split(AGENTIC_CORE_DIR)[0]

    def validate(self):
        """Ensure critical secrets are present."""
        errors = []
        if not self.PINECONE_API_KEY:
            errors.append("CRITICAL: PINECONE_API_KEY is Missing.")
        if not self.OPENAI_API_KEY:
            errors.append("CRITICAL: OPENAI_API_KEY is Missing.")

        if errors:
            raise ValueError("\n".join(errors))


# Singleton Instance
config = SovereignConfig()
