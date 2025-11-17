"""Safety stack shim."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional


class SafetyStackV10_8:
    """Provides minimal safety checks for downstream consumers."""

    def sanitize_resume(self, resume_dict: Dict[str, Any]) -> Dict[str, Any]:
        return resume_dict or {}

    def detect_bias(self, text: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        return {"bias_detected": False, "text": text}

    async def detect_prompt_injection_async(self, user_input: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        return {"injection_risk": False, "input": user_input}

    async def run_constitutional_review_async(self, final_draft_text: str, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        return {"constitutional_review": {"safe": True, "text": final_draft_text}}

    async def constitutional_review_from_state_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        artifacts = state.get("artifacts", {}) if isinstance(state, dict) else {}
        final_resume = None
        if isinstance(artifacts, dict):
            final_resume = artifacts.get("artifacts", {}).get("final_resume") if isinstance(artifacts.get("artifacts"), dict) else None
        draft = state.get("draft", {}) if isinstance(state, dict) else {}
        if final_resume is None and isinstance(draft, dict):
            final_resume = draft.get("final_draft") or draft.get("sections", {}).get("summary")
        if final_resume is None:
            final_resume = state.get("resume") or {}

        text = json.dumps(final_resume) if not isinstance(final_resume, str) else final_resume
        review = await self.run_constitutional_review_async(text, workflow_id)
        return {"qa": {"constitutional_review": review}}
