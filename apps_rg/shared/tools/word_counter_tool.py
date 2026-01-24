"""
Word Counter Tool - Word counting utility
Refactored from compute_word_count.py
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class WordCounterTool(BaseRGEngine):
    """
    Utility for counting words in text.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="TOOLS.WORD_COUNTER")

    async def execute(self, text: str) -> int:
        """
        Count words in text.
        """
        word_count = len(text.split())
        self.record_pass(f"Counted {word_count} words")
        return word_count
