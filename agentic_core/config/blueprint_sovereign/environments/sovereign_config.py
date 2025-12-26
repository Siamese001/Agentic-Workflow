"""
Sovereign Configuration SSOT
Centralizes all environment variables, feature flags, and system constants.
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SovereignConfig:
    # Vector Database
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "us-east-1")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    
    # Model Defaults
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-large"
    DEFAULT_EMBEDDING_DIM: int = 1536
    
    # System Paths
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__)).split("agentic_core")[0]
    
    def validate(self):
        """Ensure critical secrets are present."""
        if not self.PINECONE_API_KEY:
            raise ValueError("CRITICAL: PINECONE_API_KEY is missing from environment.")

# Singleton Instance
config = SovereignConfig()
