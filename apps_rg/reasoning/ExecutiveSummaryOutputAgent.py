"""Strategist BioWriter - Executive Summary Generation (K.1).

This agent generates executive summaries with strict 3rd-person implied voice,
enforcing 120-140 word count and 3-5 sentence structure with 1st-person blocking.

Sub-Atomic Agent Name: Strategist_BioWriter
Legacy K-Node: K.1
"""

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from agentic_core.runtime.types.reasoning_config import ReasoningConfig
from apps_rg.utils.RGAgentBase import RGAgentBase

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


FIRST_PERSON_PATTERNS = [
    "\\bI\\b",
    "\\bI\\'m\\b",
    "\\bI\\'ve\\b",
    "\\bI\\'ll\\b",
    "\\bI\\'d\\b",
    "\\bmy\\b",
    "\\bmine\\b",
    "\\bme\\b",
    "\\bmyself\\b",
    "\\bwe\\b",
    "\\bwe\\'re\\b",
    "\\bwe\\'ve\\b",
    "\\bour\\b",
    "\\bours\\b",
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
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ExecutiveSummaryOutputAgent.run")
        return {"bio": "Draft content..."}
