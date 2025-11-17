"""WorkflowContext bundling configuration, clients, and services."""
from __future__ import annotations

from dataclasses import dataclass, field

from .clients import AsyncBaseModelClient, AsyncEmbeddingClient, AsyncVisionClient
from .constants import DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE, MAX_TOKENS
from .models import WorkflowConfig
from .services import ContextBudgetManager, ServiceBundle


@dataclass
class WorkflowContext:
    config: WorkflowConfig
    services: ServiceBundle = field(default_factory=ServiceBundle)
    client: AsyncBaseModelClient = field(default_factory=AsyncBaseModelClient)
    embedding_client: AsyncEmbeddingClient = field(default_factory=AsyncEmbeddingClient)
    vision_client: AsyncVisionClient = field(default_factory=AsyncVisionClient)
    budget_manager: ContextBudgetManager = field(init=False)

    def __post_init__(self) -> None:
        self.budget_manager = ContextBudgetManager(self.config.max_tokens)


def create_workflow_context(model: str | None = None, temperature: float | None = None, max_tokens: int | None = None) -> WorkflowContext:
    cfg = WorkflowConfig(
        model=model or DEFAULT_MODEL_NAME,
        temperature=temperature or DEFAULT_TEMPERATURE,
        max_tokens=max_tokens or MAX_TOKENS,
    )
    return WorkflowContext(config=cfg)


__all__ = ["WorkflowContext", "create_workflow_context"]
