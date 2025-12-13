"""Split module 1 for config_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class ModelProvider(Enum):
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    AZURE = 'azure'
    LOCAL = 'local'

@dataclass
class ModelConfig:
    provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = 'gpt-4-turbo'
    api_key: Optional[str] = None
    temperature: float = DEFAULT_GENERATION_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS

@dataclass
class RAGConfig:
    enabled: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_count: int = 5

@dataclass
class GovernorConfig:
    strict_mode: bool = True
    constraints: 'ContentConstraintsConfig' = field(default_factory=lambda: ContentConstraintsConfig())

@dataclass
class WorkflowConfig:
    max_steps: int = 10
    stop_on_error: bool = True
    parallel_execution: bool = False

