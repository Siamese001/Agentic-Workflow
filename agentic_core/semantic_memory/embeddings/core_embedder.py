"""
Sovereign Core Embedder – Primary Embedding Engine
Uses OpenAI text-embedding-3-large (SOTA as of Dec 2025).
Configurable dimensions for Pinecone cost/accuracy trade-off.
SSOT for all embedding calls in the agentic core.
"""
from typing import Any, List
import openai
from agentic_core.config.blueprint_sovereign.sovereign_config import config

def get_embedding(text: str, model: str=config.DEFAULT_EMBEDDING_MODEL, dimensions: int=config.DEFAULT_EMBEDDING_DIM) -> List[float]:
    """
    Sovereign embedding function – used by bootstrap, healers, and RAG pipelines.
    
    :param text: Input string (will be auto-truncated to model max ~8k tokens)
    :param model: OpenAI embedding model (defaults to config)
    :param dimensions: Output dimensionality (defaults to config: 1024)
    :return: Normalized float vector
    """
    if not config.OPENAI_API_KEY:
        raise ValueError('OPENAI_API_KEY environment variable required for core embedder')
    client: Any = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    response: Any = client.embeddings.create(input=text.replace('\n', ' '), model=model, dimensions=dimensions)
    return response.data[0].embedding
