"""
Section Balance Engine - Length/ratio validation
Refactored from SectionBalanceAgent.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


class SectionBalanceEngine(BaseRGEngine):
    """
    Validates section length and ratio balance.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.BALANCE")

    async def execute(self, sections: dict[str, Any]) -> dict[str, Any]:
        """
        Validate section balance and ratios.
        """
        self._mcp_audit("balance_check")

        # Calculate section lengths
        section_lengths = {}
        for name, content in sections.items():
            if isinstance(content, str):
                section_lengths[name] = len(content.split())
            elif isinstance(content, list):
                section_lengths[name] = sum(len(str(item).split()) for item in content)

        total_words = sum(section_lengths.values())

        # Calculate ratios
        ratios = {name: length / total_words for name, length in section_lengths.items()}

        # Validate balance
        issues = []

        # Experience should be 40-60% of total
        exp_ratio = ratios.get("experience", 0)
        if exp_ratio < 0.4 or exp_ratio > 0.6:
            issues.append(f"Experience ratio {exp_ratio:.1%} outside target 40-60%")

        # Summary should be 10-20%
        summary_ratio = ratios.get("summary", 0)
        if summary_ratio > 0.2:
            issues.append(f"Summary ratio {summary_ratio:.1%} exceeds 20% limit")

        result = {
            "balanced": len(issues) == 0,
            "section_lengths": section_lengths,
            "ratios": ratios,
            "issues": issues,
        }

        if issues:
            self.record_fail("Section balance issues detected", data=result, signal="BALANCE_VIOLATION")
        else:
            self.record_pass("Section balance validated")

        return result
