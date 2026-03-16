"""
Word Counter Tool - Word counting utility
Refactored from compute_word_count.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_resume_engine import BaseRGEngine

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "word_counter_tool", "p0_governance")
_emit_reads_policy_state("p0", "word_counter_tool", "policy_binding")
_emit_snapshots_state("p0", "word_counter_tool", "state_snapshot")
emit_replay_key("p0", "word_counter_tool")
emit_determinism_digest("p0", "word_counter_tool")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "WordCounterTool.execute")

        word_count = len(text.split())
        self.record_pass(f"Counted {word_count} words")
        return word_count
