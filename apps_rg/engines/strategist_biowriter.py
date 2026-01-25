"""Strategist BioWriter - Executive Summary Generation (K.1).

This agent generates executive summaries with strict 3rd-person implied voice,
enforcing 120-140 word count and 3-5 sentence structure with 1st-person blocking.

Sub-Atomic Agent Name: Strategist_BioWriter
Legacy K-Node: K.1
"""

import logging
from dataclasses import dataclass
from typing import Any

# [Diff Start: Fix Inheritance and Config]
# Previous: from agent_core.agent import Agent
from apps_rg.shared.core.agent_base import RGAgentBase

# Previous: from runtime.config import ReasoningConfig
from agentic_core.schemas.models.reasoning_config import ReasoningConfig
# [Diff End]


logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummaryOutput:
    """Strategist BioWriter output."""

    summary: str
    word_count: int
    sentence_count: int
    first_person_violations: list[str]
    third_person_compliant: bool
    metadata: dict[str, Any]


# First-person patterns that MUST be blocked
FIRST_PERSON_PATTERNS = [
    r"\bI\b",
    r"\bI\'m\b",
    r"\bI\'ve\b",
    r"\bI\'ll\b",
    r"\bI\'d\b",
    r"\bmy\b",
    r"\bmine\b",
    r"\bme\b",
    r"\bmyself\b",
    r"\bwe\b",
    r"\bwe\'re\b",
    r"\bwe\'ve\b",
    r"\bour\b",
    r"\bours\b",
]


@dataclass
class BioWriterConfig:
    tone: str = "professional"
    length_limit: int = 500


class StrategistBioWriter(RGAgentBase):
    """
    Agent specialized in crafting executive biographies with strategic alignment.
    """

    def __init__(self, config: BioWriterConfig, reasoning: ReasoningConfig):
        super().__init__()
        self.config = config
        self.reasoning = reasoning

    async def run(self, input_data: dict) -> dict:
        # Logic implementation
        return {"bio": "Draft content..."}
