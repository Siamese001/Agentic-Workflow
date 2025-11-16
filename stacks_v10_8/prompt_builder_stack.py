"""L1 PromptBuilder stack for constructing deterministic prompt envelopes."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from core_v10_7 import BaseAgent
from prompting_v10_8 import PromptEnvelope


class PromptBuilderStack(BaseAgent):
    """Builds a unified PromptEnvelope for downstream L2 agents."""

    async def run_async(self, state: Dict[str, Any], workflow_id: str):
        self.context.workflow_id = workflow_id
        env = PromptEnvelope(
            framing=self._default_framing(state),
            context=self._extract_context(state),
            reasoning=self._inject_reasoning(),
            instructions=self._assemble_instructions(state),
            tool_context=self._tool_metadata(state),
            safety_context={},
            output_schema=self._schema_from_state(state),
            raw_template=None,
        )

        detector = getattr(self.context, "prompt_injection_detector", None)
        if detector is not None:
            aggregated_text = "\n\n".join(
                part
                for part in (
                    env.framing,
                    env.instructions,
                    json.dumps(env.context, sort_keys=True, ensure_ascii=False)
                    if env.context
                    else "",
                )
                if part
            )
            env.safety_context["injection"] = detector.detect(aggregated_text)

        return {"prompts": {"prompt_envelope": env.model_dump()}}

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _default_framing(self, state: Dict[str, Any]) -> str:
        system_goal = state.get("system_goal") or state.get("mission")
        base_framing = (
            "You are the L1 Prompt Builder responsible for assembling a deterministic "
            "prompt envelope for downstream tool-using agents. Maintain alignment with "
            "developer and safety policies."
        )
        if system_goal:
            return f"{base_framing} Primary goal: {system_goal}."
        return base_framing

    def _extract_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        for key in (
            "job_description",
            "resume",
            "strategy",
            "rag_context",
            "conversation_history",
        ):
            if state.get(key):
                context[key] = state[key]

        additional_context = state.get("context")
        if isinstance(additional_context, dict):
            context.update(additional_context)

        return context

    def _inject_reasoning(self) -> str:
        return (
            "[REASONING]\n"
            "1) Validate the mission and safety requirements.\n"
            "2) Identify relevant context elements (job, resume, strategy, RAG).\n"
            "3) Draft clear instructions for downstream agents.\n"
            "4) Confirm the output schema and tool interfaces.\n"
            "5) Surface any safety signals for review."
        )

    def _assemble_instructions(self, state: Dict[str, Any]) -> str:
        base_instructions: List[str] = [
            "Construct a prompt envelope that is deterministic and explicit.",
            "Do not execute tools; only describe them for downstream agents.",
            "Preserve system roles and honor all developer and safety constraints.",
        ]

        state_instructions: List[str] = []
        for key in ("task", "instructions", "user_request", "developer_instructions"):
            if state.get(key):
                state_instructions.append(f"{key}: {state[key]}")

        if state_instructions:
            base_instructions.append("Contextual directives:\n" + "\n".join(state_instructions))

        return "\n".join(base_instructions)

    def _tool_metadata(self, state: Dict[str, Any]) -> Dict[str, Any]:
        available_tools = state.get("available_tools") or []
        if isinstance(available_tools, dict):
            # Normalize single tool map to list for consistency
            available_tools = [available_tools]
        constraints = state.get("tool_constraints") or {}
        return {"available_tools": available_tools, "constraints": constraints}

    def _schema_from_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        schema = state.get("output_schema")
        if isinstance(schema, dict) and schema:
            return schema

        return {
            "type": "object",
            "properties": {
                "framing": {"type": "string"},
                "instructions": {"type": "string"},
                "context": {"type": "object"},
                "tool_context": {"type": "object"},
                "safety_context": {"type": "object"},
            },
            "required": ["framing", "instructions", "context"],
            "additionalProperties": True,
        }
