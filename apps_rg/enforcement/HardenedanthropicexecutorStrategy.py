"""Hardened Anthropic executor with resilient client wiring (EX1 / EX2).

Regression suite: ``tests/unit/apps_rg/enforcement/test_hardened_anthropic_executor_setup.py``.
"""

from __future__ import annotations

import logging
import os

import anthropic
from dotenv import load_dotenv

from agentic_core.mixins.hardening_mixin import HardeningMixin

load_dotenv()

logger = logging.getLogger(__name__)


class HardenedAnthropicExecutor(HardeningMixin):
    """Executor that configures a live ``anthropic.Anthropic`` client when keyed."""

    def __init__(self) -> None:
        super().__init__(component_name="HardenedAnthropicExecutor")
        self._client: anthropic.Anthropic | None = None
        self._setup_client()

    def _setup_client(self) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self._client = anthropic.Anthropic(api_key=api_key)
            return
        logger.warning(
            "ANTHROPIC_API_KEY not set; anthropic executor has no authenticated client.",
        )
        self._client = None
