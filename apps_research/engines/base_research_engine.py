"""
Base Research Engine — Foundation for all apps_research engines.

Mirrors apps_exec BaseExecEngine pattern with research-specific contracts.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

try:
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
except ImportError:  # guardian: allow-silent-swallow - optional dependency

    class SemanticCacheMixin:  # type: ignore[no-redef]
        pass


try:
    from agentic_core.mixins.embedding_mixin import EmbeddingMixin
except ImportError:

    class EmbeddingMixin:  # type: ignore[no-redef]
        pass


_log = logging.getLogger(__name__)


class BaseResearchEngine(SemanticCacheMixin, EmbeddingMixin, ABC):
    """Abstract base for all Autonomous Research Engine modules.

    Provides:
    - Standard logging interface
    - Specs and toggle loading
    - Provenance metadata injection
    - Dry-run protocol
    """

    AGENT_ID: str = ""

    def __init__(self, config: Any = None, **kwargs: Any) -> None:
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True
        self._semantic_namespace = "apps_research"

        try:
            from apps_research.config.agent_spec_config import load_research_specs

            self.specs = load_research_specs()
        except ImportError:
            self.specs = None
            self.logger.warning("[%s] research specs not available", self.name)

        try:
            from apps_research.config.reasoning_toggles_config import DEFAULT_TOGGLES

            self.toggles = DEFAULT_TOGGLES
        except ImportError:
            self.toggles = None

        # Initialize knowledge base for prompt templates
        try:
            from apps_research.config.knowledge_base import FROZEN_SNAPSHOT

            self.knowledge = FROZEN_SNAPSHOT
        except ImportError:
            self.knowledge = None
            self.logger.warning("[%s] knowledge base not available", self.name)

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Main execution method — must be implemented by subclasses."""

    def get_prompt(self, prompt_id: str) -> str:
        """Get prompt from knowledge base.

        Raises:
            TypeError: If prompt_id is None
            KeyError: If prompt_id not found in knowledge base
            RuntimeError: If knowledge base is not available
        """
        if prompt_id is None:
            raise TypeError("prompt_id cannot be None")
        if not self.knowledge:
            raise RuntimeError("Knowledge base not available")
        from apps_research.config.knowledge_base import get_prompt

        return get_prompt(prompt_id)

    def get_node_config(self, node_id: str) -> Any:
        """Get K-node configuration from knowledge base.

        Raises:
            TypeError: If node_id is None
            KeyError: If node_id not found in knowledge base
            RuntimeError: If knowledge base is not available
        """
        if node_id is None:
            raise TypeError("node_id cannot be None")
        if not self.knowledge:
            raise RuntimeError("Knowledge base not available")
        from apps_research.config.knowledge_base import get_node_config

        return get_node_config(node_id)

    def record_fail(self, message: str, *, signal: str = "", data: dict | None = None) -> None:
        self.logger.warning("FAIL [%s]: %s", self.name, message)

    def record_pass(self, message: str, *, data: dict | None = None) -> None:
        self.logger.info("PASS [%s]: %s", self.name, message)

    def get_status(self) -> dict[str, Any]:
        return {
            "engine": self.name,
            "initialized": self._initialized,
            "specs_available": self.specs is not None,
            "knowledge_available": self.knowledge is not None,
        }
