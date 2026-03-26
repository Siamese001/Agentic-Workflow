"""
Base Research Engine — Foundation for all apps_research engines.

Mirrors apps_exec BaseExecEngine pattern with research-specific contracts.
"""

from __future__ import annotations

import logging
from abc import ABCMeta, abstractmethod
from typing import Any

try:
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
# guardian: allow-silent-swallow - optional dependency
except ImportError:

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

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Main execution method — must be implemented by subclasses."""

    def record_fail(self, message: str, *, signal: str = "", data: dict | None = None) -> None:
        self.logger.warning("FAIL [%s]: %s", self.name, message)

    def record_pass(self, message: str, *, data: dict | None = None) -> None:
        self.logger.info("PASS [%s]: %s", self.name, message)

    def get_status(self) -> dict[str, Any]:
        return {
            "engine": self.name,
            "initialized": self._initialized,
            "specs_available": self.specs is not None,
        }
