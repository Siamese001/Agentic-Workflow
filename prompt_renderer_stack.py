"""Prompt renderer stack."""
from __future__ import annotations

from typing import Any, Dict, Optional

from prompt_envelope import PromptEnvelope


class PromptRendererStack:
    async def run_async(self, state: Dict[str, Any], workflow_id: Optional[str] = None) -> Dict[str, Any]:
        prompts = state.get("prompts", {}) if isinstance(state, dict) else {}
        env_data = prompts.get("prompt_envelope") or {}
        envelope = env_data if isinstance(env_data, PromptEnvelope) else PromptEnvelope(**env_data) if isinstance(env_data, dict) else PromptEnvelope()

        safety_context = {
            "injection": {"risk": False},
            "policy": {},
            "constitution": {},
        }
        envelope.metadata["safety_context"] = safety_context

        sections = envelope.to_sections()
        rendered = []
        for title, content in sections.items():
            rendered.append(f"### {title}\n{content}\n")
        rendered.append("### Safety\n" + str(safety_context))
        final_prompt = "\n".join(rendered).strip()

        return {"prompts": {"final_prompt": final_prompt}}
