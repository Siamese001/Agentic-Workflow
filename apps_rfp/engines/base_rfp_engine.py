"""
Base RFP Engine — Foundation for all apps_rfp engines.

Mirrors apps_exec BaseExecEngine pattern with rfp-specific contracts.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

_log = logging.getLogger(__name__)


class BaseRfpEngine(ABC):
    """Abstract base for all AI Proposal / RFP Generator engines.

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

        try:
            from apps_rfp.config.agent_spec_config import load_rfp_specs

            self.specs = load_rfp_specs()
        except ImportError:
            self.specs = None
            self.logger.warning("[%s] rfp specs not available", self.name)

        try:
            from apps_rfp.config.reasoning_toggles_config import DEFAULT_TOGGLES

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
