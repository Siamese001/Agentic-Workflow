"""
Message Generation Task - Outreach message writer
Refactored from execute_message_generation.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class MessageGenerationTask(BaseRGEngine):
    """
    Outreach message writer for networking/applications.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="GENERATION.MESSAGE")

    async def execute(self, recipient_context: dict[str, Any], message_type: str = "outreach") -> str:
        """
        Generate personalized outreach message.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MessageGenerationTask.execute")

        self._mcp_audit("message_generation_start", {"type": message_type})
        prompt = f"Generate a {message_type} message for {recipient_context.get('name', 'recipient')}"
        message = await self.call_llm(prompt)
        if message and len(message) > 50:
            self.record_pass(f"Generated {message_type} message")
        else:
            self.record_fail("Message generation produced insufficient content")
        return message or ""
