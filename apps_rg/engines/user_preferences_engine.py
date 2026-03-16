"""
User Preferences Engine - Fetch user preferences
Refactored from fetch_user_preferences.py
"""

from __future__ import annotations

import logging
from typing import Any

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
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "user_preferences_engine", "p0_governance")
_emit_reads_policy_state("p0", "user_preferences_engine", "policy_binding")
_emit_snapshots_state("p0", "user_preferences_engine", "state_snapshot")
emit_replay_key("p0", "user_preferences_engine")
emit_determinism_digest("p0", "user_preferences_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
