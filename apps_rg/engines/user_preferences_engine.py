"""
User Preferences Engine - Fetch user preferences
Refactored from fetch_user_preferences.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class UserPreferencesEngine(BaseRGEngine):
    """
    Retrieves user preferences for resume generation.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="RETRIEVAL.PREFERENCES")

    async def execute(self, user_id: str) -> dict[str, Any]:
        """
        Fetch user preferences.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "UserPreferencesEngine.execute")

        self._mcp_audit("preferences_retrieval", {"user_id": user_id})
        preferences = {
            "template_style": "modern",
            "color_scheme": "professional",
            "include_photo": False,
            "preferred_sections": ["summary", "experience", "education", "skills"],
            "tone": "professional",
        }
        if hasattr(self.ctx, "user_preferences"):
            preferences.update(self.ctx.user_preferences.get(user_id, {}))
        self.record_pass("User preferences retrieved")
        return preferences
